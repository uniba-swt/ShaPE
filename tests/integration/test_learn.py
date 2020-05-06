#!/usr/bin/env python3
"""
Contains integration tests for the learn functionality of ShaPE.
"""

import pytest

from jboockmann.shape import learn
from jboockmann.shape.model import MemoryGraph
from ..settings import EXAMPLES_PROLOG, EXAMPLES_DSI


def test_series_bt() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/series-bt/bt-null-1.pl',
        f'{EXAMPLES_PROLOG}/series-bt/bt-null-2.pl',
        f'{EXAMPLES_PROLOG}/series-bt/bt-null-3.pl',
    ]))
    learn.learn(graphs)


def test_bt_parent() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/bt-parent.pl'
    ]))
    learn.learn(graphs)


def test_bt_this() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/bt-this.pl'
    ]))
    learn.learn(graphs)


def test_csll() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/csll.pl'
    ]))
    learn.learn(graphs)


def test_dll_stable_null() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/dll-stable-null.pl'
    ]))
    learn.learn(graphs)


def test_sll_null() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/sll-null.pl'
    ]))
    learn.learn(graphs)


def test_bt_null_all() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/bt-null-all.pl'
    ]))
    learn.learn(graphs)


def test_bt_root() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/bt-root.pl'
    ]))
    learn.learn(graphs)


def test_bt_root_ptr() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/bt-root-ptr.pl'
    ]))
    learn.learn(graphs)


def test_dll_stable_this() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/dll-stable-this.pl'
    ]))
    learn.learn(graphs)


def test_sll_headptr() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/sll-headPtr.pl'
    ]))
    learn.learn(graphs)


def test_sll_tailptr() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/sll-tailPtr.pl'
    ]))
    learn.learn(graphs)


def test_bt_null() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/bt-null.pl'
    ]))
    learn.learn(graphs)


def test_bt_ternary() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/bt-ternary.pl'
    ]))
    learn.learn(graphs)


def test_dll_stable_null_inner_ep() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/dll-stable-null-inner-ep.pl'
    ]))
    learn.learn(graphs)


def test_sll_head_tail() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/lseg.pl'
    ]))
    learn.learn(graphs)


def test_sll_this() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/sll-this.pl'
    ]))
    learn.learn(graphs)


def test_sll_2() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_DSI}/sll_2.dot'
    ]))
    learn.learn(graphs)


def test_sll_7() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_DSI}/sll_7.dot'
    ]))
    learn.learn(graphs)


def test_sll_9() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_DSI}/sll_9.dot'
    ]))
    learn.learn(graphs)


def test_binary_trees_debian() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_DSI}/binary-trees-debian.dot'
    ]))
    learn.learn(graphs)
