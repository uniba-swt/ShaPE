#!/usr/bin/env python3
"""
Contains integration tests for the memory graph de- and recompositon functionality of ShaPE.
"""

import pytest

from jboockmann.shape import composition, helper
from jboockmann.shape.helper import ShaPEexception
from jboockmann.shape.model import MemoryGraph

from ..settings import EXAMPLES_DSI, EXAMPLES_PROLOG, FOLDER_PACKAGE, examples_dsi, examples_prolog


def test_series_sll_and_bt() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/series-sll-and-bt/sll-and-bt-0.pl',
        f'{EXAMPLES_PROLOG}/series-sll-and-bt/sll-and-bt-1.pl',
        f'{EXAMPLES_PROLOG}/series-sll-and-bt/sll-and-bt-2.pl'
    ]))
    composition.composition(graphs)


def test_sll_and_bt() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/sll-and-bt.pl'
    ]))
    composition.composition(graphs)


def test_nesting_sll_bt() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/nesting-sll-bt.pl'
    ]))
    composition.composition(graphs)


def test_wrapper_sll_bt() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/wrapper-sll-bt.pl'
    ]))
    composition.composition(graphs)


def test_nesting_csll_bt() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/nesting-csll-bt.pl'
    ]))
    composition.composition(graphs)


def test_nesting_bt_sll() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/nesting-bt-sll.pl'
    ]))
    composition.composition(graphs)


def test_SHN_sll_sll() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/SHN-sll-sll.pl'
    ]))
    composition.composition(graphs)
