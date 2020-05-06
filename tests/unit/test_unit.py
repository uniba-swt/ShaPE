#!/usr/bin/env python3

from glob import glob

from jboockmann.shape import (
    pruning, search, rules,
    composition, learn, match,
    verifast, constants, helper
)
from jboockmann.shape.helper import ShaPEexception
from jboockmann.shape.model import MemoryGraph

FOLDER_EXAMPLES = 'examples-prolog'
FOLDER_DSI = 'examples-dsi'


def test_metainformation():
    rule = 'p(This) :- condition(13, 42), node(This), next(This, Next), p(Next).'
    assert search.meta_information(rule) == ("13", "42")


def test_fromPLFile():
    for file_ in glob(f'{FOLDER_EXAMPLES}/*.pl'):
        MemoryGraph.fromPLFile(file_)


def test_constructDot():
    for file_ in glob(f'{FOLDER_EXAMPLES}/*.json'):
        MemoryGraph.fromJSONFile(file_).constructDot()


def test_onlyDiffersInCallOrder():
    rule1 = 'p(This) :- node(This), left(This, This), right(This, Right), p(Right), true.'
    rule2 = 'p(This) :- node(This), left(This, Left), right(This, This), p(Left), true.'
    assert pruning.onlyDiffersInCallOrder(rule1, rule1)
    assert pruning.onlyDiffersInCallOrder(rule2, rule2)
    assert not pruning.onlyDiffersInCallOrder(rule1, rule2)
    assert not pruning.onlyDiffersInCallOrder(rule2, rule1)

    rule1 = 'p(This) :- node(This), left(This, Left), right(This, Right), p(Right), p(Left), true.'
    rule2 = 'p(This) :- node(This), left(This, Left), right(This, Right), p(Left), p(Right), true.'
    assert pruning.onlyDiffersInCallOrder(rule1, rule1)
    assert pruning.onlyDiffersInCallOrder(rule2, rule2)
    assert pruning.onlyDiffersInCallOrder(rule1, rule2)
    assert pruning.onlyDiffersInCallOrder(rule2, rule1)


def test_areDeterministicRules():
    rules = [
        'entry(This) :- node(This), left(This, Left), right(This, null), p(Left), true.',
        'entry(This) :- node(This), left(This, null), right(This, null), true.',
        'entry(This) :- node(This), left(This, null), right(This, Right), p(Right), true.',
        'entry(This) :- node(This), left(This, Left), right(This, Right), p(Left), p(Right), true.',
        'p(This) :- node(This), left(This, null), right(This, null), true.'
    ]
    composition.are_deterministic_rules(rules)
    assert True


def test_areNotDeterministicRules():
    try:
        rules = [
            'entry(This) :- node(This), left(This, Left), right(This, null), p(Left), true.',
            'entry(This) :- node(This), left(This, Left), right(This, null), p(Left), true.',
        ]
        composition.are_deterministic_rules(rules)
        assert False
    except:
        assert True


def test_injectCall():
    vin = 'entry(This) :- node(This), next(This, Next), p(Next), true.'
    vout = 'entry(This) :- node(This), next(This, Next), child(This, Child), p(Next), entry1(Child), true.'
    assert composition.inject_call(vin, 'child', 'entry1') == vout
