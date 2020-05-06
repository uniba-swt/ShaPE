
# `examples-dsi`

This README.md file provides further information on the memory graph examples in
`.dot` format. These `.dot` files have been extracted from a running program
using the DSI tool. The tool and the obtained memory graphs are further detailed
in [*D.H. White, T. Rupprecht, and G. Lüttgen. DSI: An evidence-based approach
to identify dynamic data structures in C programs. In Software Testing and
Analysis (ISSTA ’16), pages 259–269. ACM,
2016.*](https://dl.acm.org/doi/10.1145/2931037.2931071). Symbol '🔨' indicates
that an example cannot be transformed into the memory graph format required by
ShaPE automatically.

## `sll_0.dot`, `sll_2.dot`, `sll_4.dot`, `sll_5.dot`, `sll_6.dot`, `sll_8.dot`

Standard singly linked list; NULL terminated.

## `sll_7.dot` & `sll_9.dot` 🔨

The shape of this simple singly-linked list cannot be learnred automatically,
because the longest running entry pointer points to the last node of the list.
Hence, the previous nodes are unreachable and a predicate cannot be synthesized.
A manual adjustment of the entry pointer, i.e., the first instead of the last
list node, solves the problem. Selecting the entry pointer based on a simple
reachability analysis would solve this issue. Ideas on heuristics for entry
pointer selection are discussed in the translation script `dsi2json.py`.

## `treeadd.dot` 🔨

Contains two disjunct binary-trees that are merged together during the program
execution. So far, the `dsi2json.py` script does not correctly label graphs with
multiple entry pointers, hence, only a single entry pointer is created causing
an learnence to fail, because nodes are unreachable. A manual translation
containing two entrypoints is present as well.

## `binary-trees-debian.dot` 🔨

Essentially the same as the `binary-tree` example. However, the heuristics for
picking the right node as the entry to the graph does not work here. Hence,
manual adjustment is requried.

## `binary-tree.dot`

A simple binary tree; NULL terminated.

## ``dll_5.dot``

A simple DLL; NULL terminated.

## `dll-insert-middle.dot`

A simple DLL where the longest running entry pointer points to a node in the
middle; NULL terminated.

## `two-dlls-direct.dot`

A DLL where list nodes contain duplicate next and prev pointers. ShaPE’s node
abstraction pruning is key, because it identifies that only three out of the
approx. 360 node abstractions need to be considered for the rule search.

## `weiss-sll-cut1.dot`

A simple singly linked list; NULL terminated.

## `weiss-stack-cut1.dot`

A simple singly linked list; NULL terminated.

## `wolf-dll.dot`

A simple DLL; NULL terminated.

## `wolf-queue-cut1.dot`

A simple DLL; NULL terminated.
