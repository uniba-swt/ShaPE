#!/usr/bin/env python3

from jboockmann.shape.model import MemoryGraph

EXAMPLES_PROLOG: str = 'examples-prolog'
EXAMPLES_DSI: str = 'examples-dsi'
FOLDER_PACKAGE: str = 'jboockmann/shape'


# TODO: can be removed soon
def examples_prolog(example: str) -> str:
    fname = f'{EXAMPLES_PROLOG}/{example}'
    return MemoryGraph.fromPLFile(fname)


def examples_dsi(example: str) -> str:
    fname = f'{EXAMPLES_DSI}/{example}'
    return MemoryGraph.fromDOTFile(fname)
