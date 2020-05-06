#!/usr/bin/env python3

import copy
import re
from typing import List

from . import pruning
from . import constants
from . import helper
from . import learn
from . import match
from .model import MemoryGraph
from .helper import ShaPEexception, logger


def recursiveCallComparator(rule: str) -> int:
    tail = rule.split(constants.DELIMITER_RULE)[1]
    recursiveCalls = tail.count("p(")
    return recursiveCalls


def divideanconquer(memory_graph: MemoryGraph) -> List[str]:
    """
    Split a memory graph containing multiple EPs pointing to disjunct parts of
    the memory graph into subtasks. The result of each is merged accordingly.
    """
    entrypoints = memory_graph.json["entrypoints"]
    ep2nodes = {}
    for ep in entrypoints:
        nodes = []
        stack = [ep["target"]]
        while stack:
            top = stack.pop()
            node = [n for n in memory_graph.json["vertices"]
                    if n["id"] == top][0]
            stack.extend(
                [a["value"] for a in node["assignment"] if a["value"] != "NULL"]
            )
            nodes.append(top)
        ep2nodes[ep["target"]] = nodes

    shared_nodes = set.intersection(
        *[set(nodes) for nodes in ep2nodes.values()]
    )
    if shared_nodes:
        raise ShaPEexception("entrypoints point to non-disjunct heap parts")

    memory_graphs = []
    ep2rules = {}
    for ep, nodes in ep2nodes.items():
        used_structs = [
            v["struct"]
            for v in memory_graph.json["vertices"] if v["id"] in nodes
        ]
        used_structs = list(set(used_structs))
        memory_graph2 = copy.deepcopy(memory_graph)
        memory_graph2.json["vertices"] = [
            v for v in memory_graph2.json["vertices"]
            if v["id"] in nodes
        ]
        memory_graph2.json["entrypoints"] = [
            v for v in memory_graph2.json["entrypoints"]
            if v["target"] == ep
        ]
        memory_graph2.json["structs"] = [
            s for s in memory_graph2.json["structs"]
            if s["name"] in used_structs
        ]
        memory_graphs.append(memory_graph2)
        ep2rules[ep] = composition([memory_graph2])

    allrules = []
    for ep in [e for e in ep2rules.keys()]:
        rules = [r.replace("p(", "%s_p(" % ep) for r in ep2rules[ep]]
        rules = [r.replace("entry(", "%s_entry(" % ep) for r in rules]
        ep2rules[ep] = rules
        allrules.extend(rules)

    ep = [r for r in allrules if "entry(" in r]

    eps = [e["target"] for e in memory_graph.entrypoints()]
    entry = "entry({}) :- {}, true.".format(
        ", ".join([ep.capitalize() for ep in eps]),
        ", ".join(["%s_entry(%s)" % (ep, ep.capitalize()) for ep in eps])
    )
    return [entry] + allrules


def extract_subgraph(memory_graph: MemoryGraph, ep: str) -> MemoryGraph:
    """
    Removes vertices not reachable from ep, updates structs accordingly, and
    sets the new entrypointer to ep.
    """
    # patch vertices
    rnodes = memory_graph.reachableNodes(ep)
    memory_graph.json["vertices"] = [
        v for v in memory_graph.vertices() if v["id"] in rnodes
    ]

    # patch structs
    rtypes = list(set([
        v["struct"] for v in memory_graph.vertices() if v["id"] in rnodes
    ]))
    memory_graph.json["structs"] = [
        s for s in memory_graph.structs() if s["name"] in rtypes
    ]

    # patch entrypoints
    ep_node = [v for v in memory_graph.vertices() if v["id"] == ep][0]
    memory_graph.json["entrypoints"] = [
        {
            'name': 'ep0',
            'target': ep,
            'type': ep_node["struct"]
        }
    ]

    return memory_graph


def inject_call(rule: str, field: str, name: str) -> str:
    """
    Inject a field clause and a predicate call into a rule. Example:

    rule = "entry(This) :- node(This), next(This, Next), p(Next), true."
    field = "child"
    name = "entry1"

    "entry(This) :- node(This), next(This, Next), child(This, Child), p(Next), entry1(Child), true."
    """
    assignment = pruning.extractFieldAssignment(rule)
    head = rule.split(constants.DELIMITER_RULE)[0]
    tail = rule.split(constants.DELIMITER_RULE)[1]
    p_calls = list(re.findall(constants.RE_REC_CALLS, tail))
    entry_calls = list(re.findall(r'entry_\d+\(\w+(?:, \w+)*\)', tail))
    calls = p_calls + entry_calls

    assignment[field] = field.capitalize()
    calls.append("%s(%s)" % (name, field.capitalize()))

    tail = "node(This), {ass}, {calls}, true.".format(
        ass=", ".join([
            "%s(This, %s)" % (a, assignment[a])
            for a in assignment
        ]),
        calls=", ".join(calls)
    )
    rule = "%s :- %s" % (head, tail)

    return rule


def resolve_nesting(memory_graph: MemoryGraph) -> List[str]:
    """
    Given that a memory graph contains a single entry pointer, but nodes of
    different type, the memory graph may exhibit nesting.
    """
    assert len(memory_graph.entrypoints()) == 1
    assert len(memory_graph.structs()) > 1

    parent = copy.deepcopy(memory_graph)

    # parent: subgraph with all nodes reachable from EP with same type
    ep_type = parent.entrypoints()[0]["type"]
    parent.json["structs"] = [
        s for s in parent.structs() if s["name"] == ep_type
    ]
    parent.json["vertices"] = [
        v for v in parent.vertices() if v["struct"] == ep_type
    ]

    entries = []
    # traverse each vertex of the parent memory graph
    for v in parent.vertices():
        # add each node pointed to by the vertex if not in the parent's vertices list
        for a in v["assignment"]:
            if a["value"] == "NULL":
                continue
            if a["value"] in [v["id"] for v in parent.vertices()]:
                continue
            entries.append((a["name"], a["value"]))

    # patch struct information of parent
    assert len(parent.structs()) == 1
    parent.json["structs"][0]["fields"] = [
        f for f in parent.structs()[0]["fields"] if f["type"] == ep_type
    ]

    # patch assignment of parent vertices
    for vertex in parent.vertices():
        vertex["assignment"] = [
            a for a in vertex["assignment"] if a["type"] == ep_type
        ]

    # map fields to entry nodes
    field2entrynodes = {}
    for field, node in entries:
        if field not in field2entrynodes.keys():
            field2entrynodes[field] = []
        field2entrynodes[field].append(node)

    # build the subgraph reachable from each new ep
    epnode2memorygraph = {}
    for _, ep in entries:
        epnode2memorygraph[ep] = extract_subgraph(
            copy.deepcopy(memory_graph),
            ep
        )
    field2rules = {}
    for field, entrynodes in field2entrynodes.items():
        memory_graphs = [epnode2memorygraph[ep] for ep in entrynodes]
        field2rules[field] = synth_master_shape(memory_graphs)

    # learn rules for the parent
    rules_parent = composition([parent])

    # merge parent rules with children rules
    rulesChildren = []
    for field, rules in field2rules.items():
        logger().debug(f'working on field {field}')
        # make the rules of the child unique
        unique = helper.Unique().Integer()
        name = f"entry_{unique}"
        rules = [re.sub(r"p\(", "p_%s(" % unique, r) for r in rules]
        rules = [re.sub(r"entry\(", "%s(" % name, r) for r in rules]

        # inject field clause and recursive call into each parent rule
        rules_parent = [
            inject_call(rule, field, name)
            for rule in rules_parent
        ]

        # add the child rules to the rulesChildren
        rulesChildren.extend(rules)

    rules_all = rules_parent + rulesChildren

    return rules_all


def are_deterministic_rules(rules: List[str]) -> None:
    """
    Check if a list of rules is deterministic, i.e., there do not exist two
    rules that only differ with regards to their recursive calls.
    """

    # remove recursive calls
    nonrecs = [
        re.sub(r'p\(\w+(?:, \w+)*\), ', "", rule) for rule in rules
    ]
    # raise an exception if there is a duplicate in nonrecs
    if len(nonrecs) != len(set(nonrecs)):
        raise ShaPEexception("the supplied rules are not deterministic")


def synth_master_shape(memory_graphs: List[MemoryGraph]) -> List[str]:
    """
    Synthesize a master shape predicate that correctly models every provided
    memory graph.
    """
    # learn the rules for each memory graph
    memory_graph2rules = {}
    for memoryGraph in memory_graphs:
        memory_graph2rules[memoryGraph] = composition([memoryGraph])

    # union over the learnred rules for each subgraph
    master_rules = list(set().union(*memory_graph2rules.values()))

    # sort the learnred rules (ep then other, within each by rec calls)
    ep_rules = [r for r in master_rules if r.startswith("entry")]
    ep_rules = sorted(ep_rules, key=recursiveCallComparator)
    other_rules = [r for r in master_rules if not r.startswith("entry")]
    other_rules = sorted(other_rules, key=recursiveCallComparator)
    master_rules = ep_rules + other_rules

    # check that the master rules are deterministic
    are_deterministic_rules(master_rules)

    return master_rules


def composition(memory_graphs: List[MemoryGraph]) -> List[str]:

    if len(memory_graphs) > 1:
        try:
            return separate_memory_regions(memory_graphs)
        except ShaPEexception:
            pass

    assert len(memory_graphs) == 1
    memory_graph = memory_graphs[0]
    entrypoints = memory_graph.entrypoints()
    structs = memory_graph.structs()

    if len(entrypoints) > 1:
        # split the memory graph along the entry points
        rules = separate_memory_regions([memory_graph])
        match.match_predicate([memory_graph], rules)
        return rules

    assert len(entrypoints) == 1

    if len(structs) > 1:
        # single entry pointer, but multiple structs indicate nesting
        rules = resolve_nesting(memory_graph)
        match.match_predicate([memory_graph], rules)
        return rules

    assert len(entrypoints) == 1
    assert len(structs) == 1
    # we are dealing with a simple memory graph, i.e., single entry pointer and
    # single struct type
    try:
        # check if there exists a template matching the memory graph
        rules = match.match_repository([memory_graph])
        return rules
    except ShaPEexception:
        # try to learn a new shape predicate
        rules = learn.learn([memory_graph])
        return rules


def evaluate_partition(partition: List[List[str]], memory_graphs: List[MemoryGraph]):
    # partition: [('ep0',), ('ep1',)]
    logger().debug(
        f'Testing partition: {" * ".join([" ∧ ".join(p) for p in partition])}'
    )
    for memory_graph in memory_graphs:
        item_nodes = []
        # a partition has multiple items
        for item in partition:
            rnodes = []
            # an item contains multiple entry pointers
            for ep in item:
                f = memory_graph.entrypoints()
                target = [e for e in f if e["name"] == ep][0]["target"]
                rnodes_ = memory_graph.reachableNodes(target)
                rnodes.extend(rnodes_)
            item_nodes.append(rnodes_)
            logger().debug(f"The partition items {item} reach nodes {rnodes}")

        logger().debug(
            f"Nodes reachable from each partition item: {item_nodes}"
        )
        # shared nodes within a partition item are allowed
        # shared nodes between partition items are not allowed
        shared_nodes = list(set.intersection(
            *[set(nodes) for nodes in item_nodes]
        ))
        logger().debug(f"shared_nodes: {shared_nodes}")
        if shared_nodes:
            raise ShaPEexception(
                f"The suggested partition shares nodes {shared_nodes}."
            )


def partition_memory_graphs(memory_graphs, partition):
    # partition memory graphs into list with memory graphs that each have the
    # same eps according to the partition
    partitioned_memory_graphs = []
    for item in partition:
        partitioned_memory_graphs_ = []
        for memory_graph in memory_graphs:
            memory_graph_ = copy.deepcopy(memory_graph)

            # patch entry points
            memory_graph_.json["entrypoints"] = [
                ep for ep in memory_graph_.entrypoints()
                if ep["name"] in item
            ]

            # patch vertices
            ep_nodes = [
                ep["target"]
                for ep in memory_graph_.entrypoints()
                if ep["name"] in item
            ]
            rnodes = []
            for ep_node in ep_nodes:
                rnodes.extend(
                    memory_graph_.reachableNodes(ep_node)
                )
            rnodes = list(set(rnodes))
            memory_graph_.json["vertices"] = [
                v for v in memory_graph_.vertices()
                if v["id"] in rnodes
            ]

            # patch structs
            rtypes = list(set([
                v["struct"] for v in memory_graph_.vertices() if v["id"] in rnodes
            ]))
            # print(memory_graph_.structs())
            memory_graph_.json["structs"] = [
                s for s in memory_graph_.structs() if s["name"] in rtypes
            ]

            partitioned_memory_graphs_.append(memory_graph_)
        partitioned_memory_graphs.append(partitioned_memory_graphs_)
    return partitioned_memory_graphs


def separate_memory_regions(memory_graphs: List[MemoryGraph]):
    helper.same_entrypointer_names(memory_graphs)
    ep_names = [e["name"] for e in memory_graphs[0].json["entrypoints"]]

    logger().debug(f"ep_names: {ep_names}")

    # de-composition

    import more_itertools
    partitions = [
        list(part) for part in more_itertools.set_partitions(ep_names)
    ]
    partitions.reverse()

    logger().debug(f"partitions: {partitions}")
    logger().debug(f"number of partitions: {len(partitions)}")

    for partition in partitions:
        try:
            evaluate_partition(partition, memory_graphs)
            break
        except ShaPEexception:
            pass
    else:
        raise ShaPEexception(
            "No partition is valid for the input memory graphs."
        )

    logger().debug(
        f"The valid partition with the strongest split is: {partition}")
    partitioned_memory_graphs = partition_memory_graphs(
        memory_graphs,
        partition
    )

    rules = []

    for partitioned_memory_graphs_ in partitioned_memory_graphs:
        rules.append(
            match.match_repository(partitioned_memory_graphs_)
        )

    # re-composition
    calls = []
    merged_rules = []

    for position, rules_ in enumerate(rules):
        postfix = "_".join(partition[position])
        for rule in rules_:
            if rule.startswith("entry("):
                rule = rule.replace("entry(", f"entry_{postfix}(")
                rule = rule.replace("p(", f"p_{postfix}(")
            elif rule.startswith("p("):
                rule = rule.replace("p(", f"p_{postfix}(")
            merged_rules.append(rule)
        calls.append(
            f"entry_{postfix}({', '.join([ep.capitalize() for ep in partition[position]])})"
        )

    entry_rule = f"entry({', '.join([ep.capitalize() for ep in ep_names])}) :- {', '.join(calls)}."
    finalized_rules = [entry_rule] + merged_rules

    return finalized_rules
