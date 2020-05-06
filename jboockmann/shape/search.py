#!/usr/bin/env python3
"""
Provides access to the meta-interpretive search.
"""

import copy
import re
import subprocess
from typing import List, Tuple, Any

from . import pruning
from . import constants
from . import helper
from .model import MemoryGraph
from .helper import ShaPEexception, logger


def search(
        rules: List[str],
        memory_graphs: List[MemoryGraph],
) -> List[str]:

    # rules pre-processing
    rules = inject_conditions(rules)
    rules = [inject_freshness(r) for r in rules]
    rules = [inject_inequalities(r) for r in rules]

    # extract mapping information
    id2rule = {}
    id2condition = {}
    for rule in rules:
        rule_id, condition_id = meta_information(rule)
        id2condition[rule_id] = condition_id
        id2rule[rule_id] = rule

    rules = pruning.optimizeOrderOfRules(rules)
    out, _ = conduct(assemble_prolog_program(rules, memory_graphs))

    # the MI returns a list of rule IDs, e.g., `[1,2,3,4,5]`
    rule_ids = out[1:-1].split(',')
    rule_ids = sorted(rule_ids)
    solution = rule_ids

    # map rule ID to rule and remove special clauses
    solution = [id2rule[r] for r in solution]
    solution = [remove_freshness(r) for r in solution]
    solution = [remove_inequalities(r) for r in solution]
    solution = [remove_condition(r) for r in solution]

    solution = pruning.optimizeOrderOfRules(solution)

    logger().debug(f'Found a solution:')
    for r in solution:
        logger().debug(f'{r}')
    return solution


def assemble_prolog_program(
        rules: List[str],
        memory_graphs: List[MemoryGraph],
        mi_path: str = constants.MI_INFER
) -> str:
    """
    Assembles a Prolog program from the following four chunks of information:

    1. the meta-interpreter definition
    2. the memory graph encoded as Prolog facts
    3. the list of candidate rules
    4. the query to be performed

    Observe that the first chunk is derived from parameter `miPath` denoting the
    path to the meta-interpreter, the second chunk is derived from parameter
    `memoryGraph`, and the third chunk is derived from parameter `rules`. The
    query, i.e., the fourth chunk, is constructed from the memory graph as well.
    """
    program = []

    with open(mi_path, r'r') as f:
        for l in f.read().splitlines():
            program.append(l)

    program.append(r'')

    # Discontiguous definitions to supress warnings
    program.append(r'% Discontiguous definitions')
    program.append(r':- (discontiguous node/1).')
    program.append(r':- (discontiguous condition/2).')
    program.append(r':- (discontiguous fresh/1).')
    for struct in memory_graphs[0].structs():
        for field in struct["fields"]:
            field_name = field["name"]
            program.append(f':- (discontiguous {field_name}/2).')
    # NOTE: discontiguous definition of predicate p usually suffice until 4
    program.append(r':- (discontiguous p/1).')
    program.append(r':- (discontiguous p/2).')
    program.append(r':- (discontiguous p/3).')
    program.append(r':- (discontiguous p/4).')
    program.append(r'')

    # MI keyword clauses unconditionally evaluate to true
    program.append(r'% MI keyword clauses unconditionally evaluate to true')
    program.append(r'condition(_, _).')
    program.append(r'fresh(_).')
    program.append(r'')

    # Memory graph encoded as Prolog facts
    program.append(r'% Memory graph encoded as Prolog facts')
    for memoryGraph in memory_graphs:
        program.extend(memoryGraph.synthPrologFacts())
    program.append(r'')

    # Candidate rules
    program.append(r'% Candidate rules')
    program.extend(rules)
    program.append(r'')

    # Query code
    program.append(r'% Query code')
    queries = []
    p = 0
    for p, memoryGraph in enumerate(memory_graphs):
        node_ids = [v['id'] for v in memoryGraph.json['vertices']]
        node_ids = ", ".join(node_ids)
        ep_nodes = [ep["target"] for ep in memoryGraph.entrypoints()]
        ep_nodes = ", ".join(ep_nodes)
        query = f'mi_seplog(entry({ep_nodes}), [{node_ids}], [], ROut{p}, ROut{p + 1}, COut{p}, COut{p + 1})'
        queries.append(query)
    queries_string = ",\n\t".join(queries)
    go_query = f'go() :- ROut0 = [], COut0 = [],{queries_string},print(ROut{p + 1}).'
    program.append(go_query)
    program.append(r'')

    return '\n'.join(program)


def conduct(
        program: str,
        output_file: None = None,
        timeout: None = None
) -> Tuple[Any, Any]:
    if output_file is None:
        output_file = constants.DEBUG_CODEPL
    if timeout is None:
        timeout = constants.TIMEOUT_PROLOG

    with open(output_file, 'w') as pfile:
        pfile.write(program)
        pfile.flush()

    p = subprocess.Popen(
        f'swipl -s {output_file} --quiet -g go -g halt',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    try:
        out, err = p.communicate(timeout=timeout)
        out = out.decode('utf-8')
        err = err.decode('utf-8')
    except subprocess.TimeoutExpired:
        raise ShaPEexception(f'swipl caused a timeout after {timeout} sec')

    if p.returncode != 0:
        # Something is rotten in the implementation of the MI ...
        assert 'No permission to access private_procedure' not in err
        raise ShaPEexception('The MI could not find a matching rules subset.')

    return out, err


def meta_information(
        rule: str
) -> Tuple[str, str]:
    """
    Analyses a rule and returns a tuple containing the rule ID as first element
    and the condition ID as second element. Note that the IDs are of type
    string.

    For example, the rule `p(This) :- condition(13, 42), node(This), next(This,
    Next), p(Next).` yields the tuple `("13", "42")`.
    """
    ref = re.findall(constants.RE_METAINFORMATION, rule)
    assert len(ref) == 1
    return ref[0]


def inject_fake_conditions(rules):
    """
    Add fake condition clauses into the rules, where the condition ID is equal
    to the rule ID. Thereby, each rule is associated with a different condition
    ID due to which any rules subset is deterministic. This is used to disable
    the search for a deterministic rules subset while still being compatible
    with the meta-interpreter. Conduct function `injectConditions` for further
    documentation.
    """
    rules_ = []
    rule_id = 0
    for rule in rules:
        condition = f'condition({rule_id}, {rule_id})'
        rules_.append(helper.prependClause(rule, condition))
        rule_id += 1
    return rules_


def inject_conditions(
        rules: List[str]
) -> List[str]:
    """
    Injects the meta-interpreter keyword clause `condition(ruleID, conditionID)`
    into each rule, where `ruleID` is a unique rule identifier and `conditionID`
    assigns each rule sharing the same rule condition the same `conditionID`.
    Two rules share the same rule condition if they only differ in their
    recursive calls, i.e., share the same parameter and field assignemnt. The
    condition clause is injected at the beginning, i.e., its the first clause of
    the rule body.

    For example, consider the four rules depicted below.

        "p(This, Par1) :- node(This), next(This, Next), p(Next, Par1)."
        "p(This, Par1) :- node(This), next(This, Next), p(Next, Next)."
        "p(This, null) :- node(This), next(This, Next), p(Next, Next)."
        "p(This, null) :- node(This), next(This, null)."

    The first and second rule share the same rule condition, as they only
    differ in the second argument to their recursive call. The third rule
    is different from both, as its second parameter differs. The fourth
    rule shares the same parameters as the third rule. but contains no
    recursive call at all. Hence, the third and fourth rule do not share
    the same rule condition. Accordingly, the rules are transformed as
    indicated below:

        "p(This, Par1) :- condition(0, 0), node(This), next(This, Next), p(Next, Par1)."
        "p(This, Par1) :- condition(1, 0), node(This), next(This, Next), p(Next, Next)."
        "p(This, null) :- condition(2, 1), node(This), next(This, Next), p(Next, Next)."
        "p(This, null) :- condition(3, 2), node(This), next(This, null)."
    """

    def condition_string(rule):
        """
        Retrieve a unique identifier for the rule condition of this rule, i.e.,
        the rule itself without the trailing recursive calls.
        """
        (head, tail) = rule.split(constants.DELIMITER_RULE)
        if 'p(' in tail:
            return '%s :- %s' % (head, tail.split(', p(', maxsplit=1)[0])
        else:
            return rule.split(', true', maxsplit=1)[0]

    # build mapping from rule condition to rule condition ID
    condition_dictionary = {}  # mapping from conditionString to condID
    cond_id = 0
    for rule_ in rules:
        if condition_string(rule_) not in condition_dictionary.keys():
            condition_dictionary[condition_string(rule_)] = cond_id
            cond_id += 1

    # inject conditions into rules
    candidate_rules_with_conditions = []
    rule_id = 0
    for rule_ in rules:
        condition = 'condition({ruleID}, {condID})'.format(
            ruleID=rule_id,
            condID=condition_dictionary[condition_string(rule_)]
        )
        candidate_rules_with_conditions.append(
            helper.prependClause(rule_, condition)
        )
        rule_id += 1

    return candidate_rules_with_conditions


def inject_freshness(
        rule: str
) -> str:
    """
    Injects the meta-interpreter keyword clause `fresh(Var)` into rules whose
    field clauses introduce a fresh variable `Var`. In case of multiple fields,
    multiple fresh clauses may be injected. The clause is injected before the
    recursive call clauses.

    For example, rule `p(This, Par1) :- node(This), next(This, Next), p(Next,
    Par1).` contains the single fresh field variable `Next` and hence the clause
    `fresh(Next)` gets injected, which yields `p(This, Par1) :- node(This),
    next(This, Next), fresh(Next), p(Next, Par1).`
    """
    ass = pruning.extractFieldAssignment(rule)
    fresh_fields = [
        a.capitalize()
        for a in ass.keys() if ass[a].lower() == a.lower()
    ]
    fresh_statements = [f'fresh({f})' for f in fresh_fields]
    if not fresh_statements:
        fresh_statements = ['true']
    injection = ', '.join(fresh_statements)
    # rule_ = rule
    head, tail = rule.split(constants.DELIMITER_RULE)
    if 'p(' not in tail:
        if 'p_' not in tail:
            if 'entry_' not in tail:
                rule_ = rule.replace(', true.', f', {injection}, true.')
            else:
                before, after = tail.split('entry_', maxsplit=1)
                rule_ = f'{head} :- {before}{injection}, entry_{after}'
        else:
            before, after = tail.split('p_', maxsplit=1)
            rule_ = f'{head} :- {before}{injection}, p_{after}'
    else:
        before, after = tail.split('p(', maxsplit=1)
        rule_ = f'{head} :- {before}{injection}, p({after}'
    return rule_


def inject_inequalities(
        rule: str
) -> str:
    r"""
    Makes the implicit equalities that are encoded using conventions of the
    naming of Prolog variables explicit:

    1. A variable never has value `null`
    2. Variables with different name have different values

    The derived inequality clauses are injected before the recursive call
    clauses.

    For example, the rule `p(This, Par1) :- node(This), next(This, Next),
    p(Next, Par1).` yields `p(This, Par1)  :-  node(This), next(This, Next),
    Next \= Par1, Next \= This, Next \= null, Par1 \= This, Par1 \= null,
    This \= null, p(Next, Par1).`
    """
    variables = sorted(list(set(re.findall(constants.RE_VARS, rule))))
    variables.append(constants.NULL_LOWER)
    from itertools import combinations
    ineqs = list(combinations(variables, 2))
    ineqs.sort()
    # inject the inequalities between the field assignments and recursive calls
    head, tail = rule.split(constants.DELIMITER_RULE)
    sineqs = ", ".join([rf"{a} \= {b}" for (a, b) in ineqs])

    if "p(" not in tail:
        # no recursive call, hence, `true` indicates the last clause
        tail = tail.replace(", true.", ", %s, true." % sineqs)
    else:
        # at least one recursive call
        tail = tail.replace(", p(", ", %s, p(" % sineqs, 1)

    return f'{head} {constants.DELIMITER_RULE} {tail}'


def remove_condition(rule: str) -> str:
    """
    Removes a `condition` clause from a rule. See function `injectConditions`
    for further documentation on this type of clause.
    """
    return re.sub(constants.RE_METAINFORMATION_SUB, r'', rule)


def remove_freshness(rule: str) -> str:
    """
    Removes a `fresh` clause from a rule. See function `injectFreshness` for
    further documentation on this type of clause.
    """
    return re.sub(constants.RE_FRESH_SUB, r'', rule)


def remove_inequalities(rule: str) -> str:
    """
    Removes inequality clauses from a rule. See function `injectInequalities`
    for further documentation on this type of clause.
    """
    return re.sub(constants.RE_INEQ_SUB, r'', rule)
