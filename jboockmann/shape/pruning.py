#!/usr/bin/env python3
'''
Provides functions to prune a list of candidate rules, i.e., `pruneRules`, and
optimize the ordering of rules, i.e., `optimizeOrderOfRules`.
'''

import re
from typing import Dict, List

from . import constants
from .model import MemoryGraph
from .helper import logger
from . import constants
from . import helper


def optimizeOrderOfRules(rules: List[str], comparators=None) -> List[str]:
    '''
    Optimizes the ordering of the provided rules by moving more-likely rules to
    the beginning and less-likely rules to the end. This shall increase the
    performance of the later conducted rule search in Prolog, where rules are
    tested sequentially, i.e., traversing the list from head to tail. Adjusting
    the order of rules can therefore be seen as a form of controlling the
    search. Besides, the ordering also improves readability of the rules for humans.
    '''

    if comparators is None:
        comparators = constants.COMPARATORS_DEFAULT

    import functools
    return sorted(
        rules,
        key=functools.cmp_to_key(
            functools.partial(
                multiHeuristicsComparator,
                comparators=comparators
            )
        )
    )


def multiHeuristicsComparator(rule1: str, rule2: str, comparators) -> int:
    '''
    Heuristics in the form of rule comparators are used to decide whether a rule
    is assumed to be more/less-likely compared to another rule. This function
    consults the provided comparators one after the other until a comparator
    yields `-1` (rule1 is more likely) or `+1` (rule2 is more likely) as a
    result. If all comparator consider the two rules to be equally likely then a
    deterministic choice is performed, i.e., rule1 is considered to be
    more-likely.

    The `comparators` parameter contains a List of tuples. The first tuple
    element contains the comparator function, which follows the typed function
    header: `def cmp(r1: str, r2: str) -> int`. The second tuple element
    contains a modifier of type int, which is multiplied with the result of the
    comparator. Hence, a value of `1` keeps the original comparator return value
    whereas a value of `-1` negates the value.
    '''
    for comparator, modification in comparators:
        decision = modification * comparator(rule1, rule2)
        if decision:
            return decision

    # perform any deterministic choice here
    return -1


def comparator_pname(rule1: str, rule2: str) -> int:
    '''
    Entry rules are considered more-likely than non-entry, i.e., `p`, rules.

    For example, rule1 `p(This) :- ...` is considered more-likely when compared
    to rule2 `entry(This) :- ...` in which case the comparator yields `-1` as
    output.
    '''
    head1, _ = rule1.split(constants.DELIMITER_RULE)
    head2, _ = rule2.split(constants.DELIMITER_RULE)
    if head1.startswith("entry(") and not head2.startswith("entry("):
        return -1
    elif not head1.startswith("entry(") and head2.startswith("entry("):
        return 1
    else:
        return 0


def comparator_calls(rule1: str, rule2: str) -> int:
    '''
    Rules with less recursive calls are considered more-likely than rules with
    more recursive calls. A rule with no recursive call is considered most
    likely. Two rules with different, but the same number of recursive calls are
    assumed to be equally likely.

    For example, rule1 `p(This, null) :- node(This), next(This, Next), p(Next).`
    is considered more-likely when compared to rule2 `p(This, Par1) :-
    node(This), next(This, Next), p(Next), p(Par1).` in which case the
    comparator yields `-1` as output.
    '''
    _, tail1 = rule1.split(constants.DELIMITER_RULE)
    _, tail2 = rule2.split(constants.DELIMITER_RULE)
    calls1 = tail1.count("p(")
    calls2 = tail2.count("p(")

    if calls1 < calls2:
        return -1
    elif calls1 > calls2:
        return 1
    else:
        return 0


def comparator_nullArgs(rule1: str, rule2: str) -> int:
    '''
    Compares two rules regarding the occurce of `null` in arguments of
    recursive calls. Observe that by applying the comparator
    `comparator_calls` first ensures that both rules have the same number of
    recursive calls. And with respect to the rule generation procedure, each
    recursive call has the same number of arguments.

    For example, rule1 `p(This) :- node(This), next(This, Next), p(Next, This).`
    is considered more-likely when compared to rule2 `p(This) :- node(This),
    next(This, Next), p(Next, null).` in which case the comparator yields `-1`
    as output.
    '''
    _, tail1 = rule1.split(constants.DELIMITER_RULE)
    _, tail2 = rule2.split(constants.DELIMITER_RULE)
    nulls1 = sum(
        [i.count("null") for i in re.findall(constants.RE_REC_CALLS, tail1)]
    )
    nulls2 = sum(
        [i.count("null") for i in re.findall(constants.RE_REC_CALLS, tail2)]
    )
    if nulls1 < nulls2:
        return -1
    elif nulls1 > nulls2:
        return 1
    else:
        return 0


def comparator_nullParams(rule1: str, rule2: str) -> int:
    '''
    Compares two rules regarding their occurce of `null` in the list of
    parameters. Note that by construction we can assume that both rules have the
    same number of parameters. However, this does not nececssarily hold if one
    is an `entry` rule and the other is a `p` rule. But note that such
    situations are prevented, because the overall comparator conducts a
    comparison on this property before already, see `comparator_pname`.

    For example, rule1 `p(This, This) :- node(This), next(This, Next), p(Next).`
    is considered more-likely when compared to rule2 `p(This, null) :-
    node(This), next(This, Next), p(Next).` in which case the comparator yields
    `-1` as output.
    '''
    head1, _ = rule1.split(constants.DELIMITER_RULE)
    head2, _ = rule2.split(constants.DELIMITER_RULE)
    nulls1 = head1.count(constants.NULL_LOWER)
    nulls2 = head2.count(constants.NULL_LOWER)

    if nulls1 < nulls2:
        return -1
    elif nulls1 > nulls2:
        return 1
    else:
        return 0


def comparator_paramsAsArgs(rule1: str, rule2: str) -> int:
    '''
    Compares two rules regarding how often parameters are used as the first
    argument in recursive calls.

    For example, rule1 `p(This, Par1, null) :- node(This), next(This, Next),
    p(Par1).` is considered more-likely when compared to rule2 `p(This, This,
    null) :- node(This), next(This, Par1), p(Next).` in which case the
    comparator yields `-1` as output.
    '''
    _, tail1 = rule1.split(constants.DELIMITER_RULE)
    _, tail2 = rule2.split(constants.DELIMITER_RULE)
    pattern = r'p\(Par\d*(?:, \w+)*\)'
    calls1 = len(re.findall(pattern, tail1))
    calls2 = len(re.findall(pattern, tail2))

    if calls1 > calls2:
        return 1
    elif calls1 < calls2:
        return -1
    else:
        return 0


def pruneRules(rules: List[str], memoryGraphs: List[MemoryGraph]) -> List[str]:
    '''
    Conducts a rule pruning by removing rules that either do not match the
    node abstraction, are not feasibly according to a static rule analysis, or
    violate heuristics.

    node abstraction is performed by function `pruneByVertexAbstraction`, static
    rule analysis by function `pruneByStaticAnalysis`, and heuristics by
    function `pruneByHeuristics`.
    '''
    # node abstraction
    rulesEP = [r for r in rules if r.startswith("entry(")]
    rulesOther = [r for r in rules if not r.startswith("entry(")]

    # node abstraction for entry rules
    if len(memoryGraphs) == 1:
        memoryGraph = memoryGraphs[0]
        ep2rules = {}
        for rule in rulesEP:
            relevant_ep = helper.relevantEPname(rule, memoryGraph)
            if relevant_ep not in ep2rules.keys():
                ep2rules[relevant_ep] = []
            ep2rules[relevant_ep].append(rule)
        rulesEP_ = []
        for ep, ep_rules in ep2rules.items():
            rulesEP_.extend(
                pruneByVertexAbstraction(
                    ep_rules,
                    memoryGraph.vertexAbstractionEPs()[ep]
                )
            )
        rulesEP = rulesEP_
    logger().debug(
        f'Completed node abstraction for entry rules'
    )

    # node abstraction for p rules
    vertexAbstractionsOther = []
    for memoryGraph in memoryGraphs:
        vertexAbstractionsOther.extend(memoryGraph.vertexAbstractionOthers())
    # drop duplicate abstractions
    vertexAbstractionsOther = [
        dict(t) for t in {
            tuple(sorted(d.items())) for d in vertexAbstractionsOther
        }
    ]
    rulesOther = pruneByVertexAbstraction(
        rulesOther,
        vertexAbstractionsOther
    )
    logger().debug(
        f'Completed node abstraction for p rules'
    )

    # combine pruned rules
    rules = rulesEP + rulesOther

    # static rule analysis
    rules = pruneByStaticAnalysis(rules)
    logger().debug(
        f'Completed static rule pruning'
    )

    # heuristics
    rules = pruneByHeuristics(rules)
    logger().debug(
        f'Completed heuristic rule pruning'
    )

    return rules


def pruneByVertexAbstraction(rules: List[str], abstractions: List[Dict[str, str]]) -> List[str]:
    '''
    For a given list of rules and a list of node abstraction, this function
    returns those rules, which match at least one observed node abstraction.

    A rule matches a single node abstraction, if the field assignment of the
    rule matches the node abstraction: if field `next` in the rule has value
    `null` then field `next` in the abstraction must have value `null` as well.
    The same holds for value `This`. A particular variable in the abstraction,
    e.g., `Var0`, must map to a particular variable in the rule.

    For example, the rule `p(This) :- node(This), left(This, Left), right(This,
    null), true.` matches the abstraction `{'left': 'Var0', 'right': 'null'}`,

    '''

    def ruleMatchesAbstraction(rule: str, abstraction: Dict) -> bool:
        '''
        Check if a rule matches a node abstraction.
        '''
        assignment = extractFieldAssignment(rule)
        assert assignment.keys() == abstraction.keys()

        for field in abstraction.keys():
            if assignment[field] == "null" and abstraction[field] != "null":
                return False
            elif assignment[field] != "null" and abstraction[field] == "null":
                return False
            elif assignment[field] == "This" and abstraction[field] != "This":
                return False
            elif assignment[field] != "This" and abstraction[field] == "This":
                return False

            abstractionKeys = [
                f for f in abstraction.keys()
                if abstraction[f] == abstraction[field]
            ]
            assignmentKeys = [
                f for f in assignment.keys()
                if assignment[f] == assignment[field]
            ]
            if abstractionKeys != assignmentKeys:
                return False
        return True

    return [
        rule for rule in rules
        if any(
            [
                ruleMatchesAbstraction(rule, abstraction)
                for abstraction in abstractions
            ]
        )
    ]


def pruneByStaticAnalysis(rules: List[str]) -> List[str]:
    '''
    Conducts a static rule analysis and removes rules that are not feasiable,
    i.e., always yield a resource failure. The following static analysis
    functions are employed:

    - `hasRecursiveCallsToThis`
    - `hasRecursiveCallsToNull`
    - `hasIdenticalRecursiveCalls`
    - `pruneCommutativeCalls`

    '''
    rules = [r for r in rules if not hasRecursiveCallsToThis(r)]
    rules = [r for r in rules if not hasRecursiveCallsToNull(r)]
    rules = [r for r in rules if not hasIdenticalRecursiveCalls(r)]

    def numberOfRecursiveCalls(rule):
        _, tail = rule.split(constants.DELIMITER_RULE)
        return tail.count("p(")

    # commutative calls only occur if rules have more than one recursive call
    if any([numberOfRecursiveCalls(r) > 1 for r in rules]):
        rules = pruneCommutativeCalls(rules)

    return rules


def hasRecursiveCallsToThis(rule: str) -> bool:
    '''
    Check if a rule contains at least one recursive call with `This` as first
    argument. Such rules always cause a resource failure, because `This` already
    got consumed by the current rule.

    The rule `p(This) :- node(This), next(This, null), p(This), true` contains
    one recursive call with `This` as first argument.
    '''
    _, tail = rule.split(constants.DELIMITER_RULE)
    return "p(This" in tail


def hasRecursiveCallsToNull(rule: str) -> bool:
    '''
    Check if a rule contains at least one recursive call with `null` as first
    argument. Such rules always cause a resource failure, because `null` cannot
    be consumed.

    The rule `p(This) :- node(This), next(This, null), p(null), true` contains
    one recursive call with `null` as first argument.
    '''
    _, tail = rule.split(constants.DELIMITER_RULE)
    return "p(null" in tail


def hasIdenticalRecursiveCalls(rule: str) -> bool:
    '''
    Check if a rule contains at least two calls that are identical wrt. the
    first argument, e.g., `p(Next), p(Next)`. These rules always cause a
    resource failure, because the node -- given that the first recursive call is
    succesfull -- can no longer be consumed by the second call.

    The rule `p(This, This) :- node(This), next(This, Next), p(Next, This),
    p(Next, null), true` contains two identical recursive calls, i.e., `p(Next,
    This)` and `p(Next, null)`, because both have `Next` as their first
    argument.
    '''
    _, tail = rule.split(constants.DELIMITER_RULE)
    iterator = re.finditer(r'p\(([A-Z]\w+)', tail)
    matches = [i.group(1) for i in iterator]
    return len(matches) != len(set(matches))


def pruneCommutativeCalls(rules: List[str]) -> List[str]:
    '''
    Removes semantically duplicate rules wrt. the commutativity of the separting
    conjunction operator, i.e., `A * B <=> B * A` for recursive calls `A` and
    `B`. Hence, two rules that only differ in the order of their recursive calls
    are semantically equivalent.

    Note that this pruning technique does not alter the rules if these contain
    at most a single recursive call. Hence, one rule can be dropped from the
    list of candidate rules.

    Internally, the function `onlyDiffersInCallOrder` is used to remove rules
    that only differ in the order of their recursive calls.
    '''
    rules_ = []
    for pos1, rule1 in enumerate(rules):
        for rule2 in rules[(pos1 + 1):]:
            if onlyDiffersInCallOrder(rule1, rule2):
                break
        else:
            # rule1 has no duplicate rules, i.e., is semantically unique
            rules_.append(rule1)
    return rules_


def onlyDiffersInCallOrder(rule1: str, rule2: str) -> bool:
    '''
    Checks if two rules only differ in the order of their recursive calls.
    Observe that this function is commutative, i.e.,
    `onlyDiffersInCallOrder(rule1, rule2) == onlyDiffersInCallOrder(rule2,
    rule1)`

    For example, the two rules depicted below only differ in the order of their
    recursive calls. Hence, they are semantically equivalent.

    - `p(This) :- node(This), left(This, Left), right(This, Right), p(Left),
      p(Right), true.`
    - `p(This) :- node(This), left(This, Left), right(This, Right), p(Right),
      p(Left), true.`
    '''
    # neither both are entry nor both are p
    if rule1.startswith("entry(") and rule2.startswith("p("):
        return False
    if rule1.startswith("p(") and rule2.startswith("entry("):
        return False

    if extractOverallAssignment(rule1) != extractOverallAssignment(rule2):
        # the two rules differ wrt. their assignment (fields and arguments)
        return False

    # check if the recursive calls are the same
    _, tail1 = rule1.split(constants.DELIMITER_RULE)
    _, tail2 = rule2.split(constants.DELIMITER_RULE)
    from collections import Counter
    calls_rule1 = Counter(re.findall(constants.RE_REC_CALLS, tail1))
    calls_rule2 = Counter(re.findall(constants.RE_REC_CALLS, tail2))
    return calls_rule1 == calls_rule2


def pruneByHeuristics(rules: List[str]) -> List[str]:
    '''
    Removes rules violating particular heuristics. In contrast to static
    analysis, which removes infeasible rules, heuristics remove rules that may
    be feasible but lead to "bad" rules, i.e., not capturing the underlying
    shape of the memory graph.

    The following heuristics are applied:

    - `isSingletonRule`
    '''
    # singleton heurstics
    rules = [r for r in rules if not isSingletonRule(r)]

    return rules


def isSingletonRule(rule: str) -> bool:
    '''
    Checks if a rule is a singleton rule, i.e., contains at least one singleton
    variable. According to https://www.swi-prolog.org/FAQ/SingletonVar.html a
    variable is a singleton variable if it occurs only once within the rule.
    Technically, this is not a problem, because a variable's first appearance
    always yields a succesfull variable binds. However, an underscore is
    typically used for anonymous variables that are not being referred to later
    on.

    In this use case, singleton rules are **not** desired, because they ignore
    parts of the essential structure of a memory graph. For example, a
    doubly-linked list can be described using a singly-linked list predicate
    where the previous field clause is always equal to `prev(This, Prev)`. Note
    that such rules are all singleton rules, because they introduce `Prev` as a
    fresh variable, but do not use it later on.

    The rule `p(This) :- node(This), left(This, Left), right(This, Right),
    true.` is a singleton rule, because variables `Left` and `Right` are
    introduced, but not used. In contrast, `p(This, Par1) :- node(This),
    next(This, Next), p(Next, Par1), true.` is not a singleton rule, because the
    variables `Par1` and `Next` are used in the recursive call.
    '''
    vars_ = re.findall(r'([A-Z]\w+)', rule)
    vars_singleton = [v for v in vars_ if vars_.count(v) == 1]
    return True if vars_singleton else False


def extractOverallAssignment(rule: str) -> Dict:
    '''
    Extracts the field and parameter assignment of a rule and returns it in the
    form of a dictionary.

    The input `p(This, Par1) :- node(This), next(This, Par1), true.` yields
    `{'Par1': 'Par1', 'This': 'This', 'next': 'Par1'}` as output.
    '''
    assignment = extractParameterAssignment(rule)
    assignment.update(extractFieldAssignment(rule))
    return assignment


def extractParameterAssignment(rule: str) -> Dict:
    '''
    Extracts the parameter assignment of a rule and returns it in the form of a
    dictionary.

    The input `p(This, null) :- node(This), next(This, Next), p(Next, null),
    true.` yields `{'Par1': 'null', 'This': 'This'}` as output.
    '''
    head, _ = rule.split(constants.DELIMITER_RULE)
    assignment = {}
    params = head.split("(")[1].split(")")[0].split(", ")
    # traverse the parameter, excluding the first one (`This`)
    for pos, p in list(enumerate(params))[1:]:
        assignment[f"Par{pos}"] = p
    assignment["This"] = "This"
    return assignment


def extractFieldAssignment(rule: str) -> Dict:
    '''
    Extracts the field assignment of a rule and returns it in the form of a
    dictionary.

    The input `p(This) :- node(This), left(This, Left), right(This, null),
    true.` yields `{'left': 'Left', 'right': 'null'}` as output.
    '''
    _, tail = rule.split(constants.DELIMITER_RULE)
    assignment = {}
    for field, value in re.findall(constants.RE_FIELD_ASSIGNMENT, tail):
        assignment[field] = value
    return assignment


def extractEqualities(rule: str):
    return list(re.findall(r"\w* = \w*", rule))


def extractInequalities(rule: str):
    return list(re.findall(r"\w* \\= \w*", rule))


def extractCalls(rule: str):
    _, tail = rule.split(constants.DELIMITER_RULE)
    return list(re.findall(r"p\(\w*(?:, \w*)*\)", tail))
