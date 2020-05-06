#!/usr/bin/env python3

import copy
from typing import List

from . import constants, helper
from .model import MemoryGraph


"""
Encodes a rule configuration via the following attributes:
- fields
- p_arity
- entry_arity
- p_calls
- entry_calls
"""


def generator(fields: List[str], ep_count):
    complexity = {}
    fields_count = len(fields)
    complexity['fields'] = fields

    complexity['entry_arity'] = ep_count

    for p_arity in range(1, constants.LIMIT_PARAMS + 1):
        complexity['p_arity'] = p_arity

        for p_calls in range(0, fields_count + p_arity - 1 + 1):
            complexity['p_calls'] = list(range(0, p_calls))

            for entry_calls in range(0, fields_count + ep_count+1):
                complexity['entry_calls'] = list(range(0, entry_calls))

                yield copy.deepcopy(complexity)


def generateRules(
        complexity
) -> List[str]:
    '''
    Composes a list of candidate rules following the schema provided as an
    instance of class `RulesConfiguration`. Internally, the function
    `buildRules` is used to create candidate rules from partial rule schemata.

    The additionaly supplied memory graph is necessary for pruning.
    '''
    rules = []

    # synthesize rules for EP nodes
    for entry_calls in complexity['entry_calls']:
        rules.extend(buildRules(
            params=complexity['entry_arity'],
            fields=complexity['fields'],
            arguments=complexity['p_arity'],
            calls=entry_calls,
            pname=constants.PNAME_ENTRY
        ))

    # synthesize rules for non EP nodes
    for p_calls in complexity['p_calls']:
        rules.extend(buildRules(
            params=complexity['p_arity'],
            fields=complexity['fields'],
            arguments=complexity['p_arity'],
            calls=p_calls,
            pname=constants.PNAME_OTHER
        ))

    return rules


def buildRules(
        params: int,
        fields: List[str],
        arguments: int,
        calls: int,
        pname: str
) -> List[str]:
    '''
    Constructs the candidate rules for single rule configuration, i.e., `params`
    and `calls` are single integers instead of lists. The `pname` parameter
    denotes the name of the predicate, e.g., `entry` for rules to be used as
    entry predicate.

    The input `params=1, fields=["next"], arguemts=1, calls=0,
    pname="entry"` yields the following output:

    ['entry(This) :- node(This), next(This, null), true.', 'entry(This) :-
        node(This), next(This, This), true.', 'entry(This) :- node(This),
        next(This, Next), true.']
    '''
    if pname == constants.PNAME_ENTRY:
        # in entry rules, This must not be on first position
        rules = [f'{pname}(']
        # synth rule head segment
        for param in range(0, params):
            rules_ = []
            for rule in rules:
                vars_ = [constants.NULL_LOWER] + helper.boundVars(rule)
                vars_.append(f"Par{param}")
                if not "This" in vars_:
                    vars_.append("This")
                for v in vars_:
                    rules_.append((f"{rule}{v}, "))
            rules = rules_
        rules = [f"{r[:-2]})" for r in rules]
        # drop rules that do not contain This as a parameter
        rules = [r for r in rules if "This" in r]
    else:
        rules = [f'{pname}(This']
        # synth rule head segment
        for param in range(1, params):
            rules_ = []
            for rule in rules:
                vars_ = [constants.NULL_LOWER] + helper.boundVars(rule)
                vars_.append(f"Par{param}")
                for v in vars_:
                    rules_.append((f"{rule}, {v}"))
            rules = rules_
        rules = [f"{r})" for r in rules]

    # synth connector between rule head and body
    rules = [f"{r}{constants.DELIMITER_RULE}" for r in rules]

    # synth node clause
    rules = [f"{r}node(This)" for r in rules]

    # synth field clause
    for field in fields:
        rules_ = []
        for rule in rules:
            vars_ = [constants.NULL_LOWER] + helper.boundVars(rule)
            vars_.append(field.capitalize())
            for v in vars_:
                rules_.append(f"{rule}, {field}(This, {v})")
        rules = rules_

    # synth recursive calls
    for _ in range(1, calls + 1):
        rules = [f"{r}, p(" for r in rules]
        for _ in range(1, arguments + 1):
            rules_ = []
            for rule in rules:
                vars_ = [constants.NULL_LOWER] + helper.boundVars(rule)
                for v in vars_:
                    rules_.append(f"{rule}{v}, ")
            rules = rules_
        rules = [r[:-2] for r in rules]  # remove trailing ", "
        rules = [f"{r})" for r in rules]  # add closing bracket

    # synth trailing true clause
    rules = [f"{r}, true." for r in rules]

    return rules
