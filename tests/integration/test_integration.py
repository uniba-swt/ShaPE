#!/usr/bin/env python3

import os
from glob import glob
import pytest

from jboockmann.shape import (
    composition, learn, match,
    verifast, constants, helper
)
from jboockmann.shape.model import MemoryGraph

# FOLDER_EXAMPLES = 'examples-prolog'
# FOLDER_DSI = 'examples-dsi'

# TESTS_ShaPElearn = [
#     'bt-null.json',
#     'bt-this.json',
#     'sll-null.json',
#     'sll-this.json',
#     'csll.json',
#     'bt-parent.json',
#     'sll-tailPtr.json',
#     'sll-headPtr.json',
#     'dll-stable-null.json',
#     'dll-stable-this.json'
# ]
# TESTS_ShaPElearn = sorted(list(set(TESTS_ShaPElearn)))

# TESTS_ShaPEmatch = [
#     'bt-null.json',
#     'sll-null.json',
#     'cdll.json',
#     'bt-parent.json',
#     'dll-stable-null-inner-ep.json',
#     'sll-tailPtr.json',
#     'sll-headPtr.json'
# ]
# TESTS_ShaPEmatch = sorted(list(set(TESTS_ShaPEmatch)))

# TESTS_ShaPEcomplex = TESTS_ShaPElearn + TESTS_ShaPEmatch + [
#     'sll-and-bt.json',
#     'nesting-sll-bt.json',
#     'wrapper-sll-bt.json',
#     'nesting-csll-bt.json',
#     'nesting-bt-sll.json',
#     'SHN-sll-sll.json'
# ]
# TESTS_ShaPEcomplex = sorted(list(set(TESTS_ShaPEcomplex)))

# TESTS_verifast = TESTS_ShaPEcomplex
# TESTS_verifast = sorted(list(set(TESTS_verifast)))


# def path(example: str) -> str:
#     return f'{FOLDER_EXAMPLES}/{example}'


# def test_verifast() -> None:
#     for test in TESTS_verifast:
#         memoryGraph = MemoryGraph.fromFile(path(test))
#         verifast.main(memoryGraph)
