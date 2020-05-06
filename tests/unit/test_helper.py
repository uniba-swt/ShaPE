#!/usr/bin/env python3
'''
Test cases for the `helper.py` module.
'''

from jboockmann.shape import (
    helper
)
from jboockmann.shape.helper import ShaPEexception
from jboockmann.shape.model import MemoryGraph
import pytest

from ..settings import EXAMPLES_DSI, EXAMPLES_PROLOG, FOLDER_PACKAGE
import os


def test_boundVars():
    assert ['This'] == helper.boundVars(
        "p(This, This)  :-  node(This)")
    assert ['Par1', 'This'] == helper.boundVars(
        "p(This, Par1)  :-  node(This)")
    assert ['Next', 'This'] == helper.boundVars(
        "p(This, This)  :-  node(This), next(This, Next), p(")
    assert ['Next', 'Par1', 'This'] == helper.boundVars(
        "p(This, Par1)  :-  node(This), next(This, Next), p(")


def test_getModuleFolder():
    import os
    expected = os.path.realpath(FOLDER_PACKAGE)
    actual = helper.getModuleFolder()
    assert expected == actual


def test_logger():
    import logging
    actual = helper.logger()
    assert actual is not None
    assert isinstance(actual, logging.Logger)


def test_timer():
    from jboockmann.shape.helper import timer
    expected = 101

    @timer
    def dummy():
        return expected
    assert expected == dummy()


def test_ShaPEexception_1():
    value = 'foo'
    expected = value
    actual = ShaPEexception(value).value
    assert expected == actual


def test_ShaPEexception_2():
    value = 'foo'
    expected = f"'{value}'"
    actual = str(ShaPEexception(value))
    assert expected == actual


def test_Unique_1() -> int:
    assert helper.Unique() is not None
    helper.Unique().reset()


def test_Unique_2() -> int:
    assert helper.Unique()._instance == helper.Unique()._instance
    helper.Unique().reset()


def test_Unique_3() -> int:
    val1 = helper.Unique().Integer()
    val2 = helper.Unique().Integer()
    val3 = helper.Unique().Integer()
    assert val1 != val2
    assert val2 != val3
    assert val1 != val3
    helper.Unique().reset()

    xval1 = helper.Unique().Integer()
    xval2 = helper.Unique().Integer()
    xval3 = helper.Unique().Integer()
    assert val1 == xval1
    assert val2 == xval2
    assert val3 == xval3
    helper.Unique().reset()


def test_parseRulesTemplate():
    import tempfile
    import os

    line_comment = r'% this is a comment'
    line_empty = r''  # an empty line
    line_rule = r'entry(This) :- true.'

    content = "\n".join([line_comment, line_empty, line_rule])
    with tempfile.NamedTemporaryFile(mode='w', delete=False, newline="\n") as tfile:
        tfile.write(content)
        tfile.flush()

    actual = helper.parseRulesTemplate(tfile.name)

    os.unlink(tfile.name)
    assert not os.path.exists(tfile.name)

    assert line_comment not in actual
    assert line_empty not in actual
    assert line_rule in actual


def test_prependClause():
    rule = "entry(This) :- node(This), next(This, Next), p(Next), true."
    clause = "dummy(1)"
    expected = "entry(This) :- dummy(1), node(This), next(This, Next), p(Next), true."

    actual = helper.prependClause(rule, clause)
    assert expected == actual


def test_multireplace_1():
    text = 'ABC'
    changes = [('A', 'B'), ('B', 'C'), ('C', 'A')]
    expected = 'BCA'

    actual = helper.multireplace(text, changes)

    assert expected == actual


def test_multireplace_2():
    text = 'ABC'
    actual = helper.multireplace(text, [])
    expected = text
    assert expected == actual


def test_extractFieldNames():
    rules = [
        'entry(This) :- node(This), fieldA(This, null), fieldB(This, This), fieldC(This, FieldC), fieldD(This, FieldD), p(FieldA, This).',
        'p(This) :- node(This), fieldA(This, null), fieldB(This, This), fieldC(This, FieldC), fieldD(This, FieldD), p(FieldA, This).'
    ]
    expected = ['fieldA', 'fieldB', 'fieldC', 'fieldD']
    actual = helper.extractFieldNames(rules)

    assert expected == actual
