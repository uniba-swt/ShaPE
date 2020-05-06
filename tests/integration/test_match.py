#!/usr/bin/env python3
"""
Contains integration tests for the match functionality of ShaPE.
"""

from jboockmann.shape import match
from jboockmann.shape.model import MemoryGraph
from ..settings import EXAMPLES_PROLOG


def test_series_bt() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/series-bt/bt-null-1.pl',
        f'{EXAMPLES_PROLOG}/series-bt/bt-null-2.pl',
        f'{EXAMPLES_PROLOG}/series-bt/bt-null-3.pl',
    ]))
    match.match_repository(graphs)


def test_bt_parent() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/bt-parent.pl'
    ]))
    match.match_repository(graphs)


def test_bt_this() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/bt-this.pl'
    ]))
    match.match_repository(graphs)


def test_csll() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/csll.pl'
    ]))
    match.match_repository(graphs)


def test_dll_stable_null() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/dll-stable-null.pl'
    ]))
    match.match_repository(graphs)


def test_sll_null() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/sll-null.pl'
    ]))
    match.match_repository(graphs)


def test_bt_null_all() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/bt-null-all.pl'
    ]))
    match.match_repository(graphs)


def test_bt_root() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/bt-root.pl'
    ]))
    match.match_repository(graphs)


def test_bt_root_ptr() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/bt-root-ptr.pl'
    ]))
    match.match_repository(graphs)


def test_dll_stable_this() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/dll-stable-this.pl'
    ]))
    match.match_repository(graphs)


def test_sll_headptr() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/sll-headPtr.pl'
    ]))
    match.match_repository(graphs)


def test_sll_tailptr() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/sll-tailPtr.pl'
    ]))
    match.match_repository(graphs)


def test_bt_null() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/bt-null.pl'
    ]))
    match.match_repository(graphs)


def test_bt_ternary() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/bt-ternary.pl'
    ]))
    match.match_repository(graphs)


def test_cdll() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/cdll.pl'
    ]))
    match.match_repository(graphs)


def test_dll_stable_null_inner_ep() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/dll-stable-null-inner-ep.pl'
    ]))
    match.match_repository(graphs)


def test_sll_head_tail() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/lseg.pl'
    ]))
    match.match_repository(graphs)


def test_sll_this() -> None:
    graphs = list(map(lambda f: MemoryGraph.fromFile(f), [
        f'{EXAMPLES_PROLOG}/sll-this.pl'
    ]))
    match.match_repository(graphs)
