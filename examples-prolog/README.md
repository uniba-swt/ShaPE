
# `examples-prolog`

This README.md file provides further information on the memory graph examples in
`.pl` format. Symbol '🚨' indicates that an example cannot be learned via ShaPE.

## `bash-pipe.pl` 🚨

The memory graph was obtained from an execution of
[`bash`](https://ftp.gnu.org/gnu/bash/) and exhibits a cyclic doubly-linked list
(CDLL) data structure that encodes piped commands, where an initial node (`n8`)
wraps access to the underlying CDLL via a head pointer. The nesting detection
feature can correctly split the memory graph into two sub-graphs, i.e.,
containing the single wrapper struct node and the CDLL. However, the CDLL data
structure cannot be learned, because it requires more than three parameters.

## `bt-artificial-terminal-node.pl`

A binary tree with a single terminal leaf node. Two entry pointers, i.e., one
pointing to the root of the tree and one pointing to the terminal node. Note
that ShaPE can only learn the correct predicate due to the existence of the
second entry pointer, because otherwise it could not communicate the shared
node.

## `bt-null-all.pl`

A binary tree where both pointers of each node either point to valid child nodes
or to NULL.

## `bt-null.pl`

A simple binary tree where leaf nodes are NULL termianted. a simple binary tree
example.

## `bt-parent.pl`

A binary tree with an additional pointer pointing to the parent of a node.

## `bt-root.pl`

A simple binary tree where leaf nodes are root termianted.

## `bt-root-ptr.pl`

A binary tree with an additional pointer pointing to the root of the tree.

## `bt-ternary.pl`

A simple ternary tree with the three pointer fields mid, left, and right.

## `bt-this.pl`

A simple binary tree where leaf nodes are self termianted.

## `bt-triple-ep.pl`

A binary tree with three entry pointers: ep0 points to the root node of the
tree, ep1 points to root->left, and ep2 points to root->right.

## `cdll.pl` 🚨

A standard cyclic doubly linked list. The matching predicate cannot be learned,
because it requires more than three parameters.

## `csll.pl`

A cyclic singly linked list.

## `dll-gl.pl`

A doubly-linked where the prev pointer of the first element still points to
NULL. Such a situation may be found during a modifying operation.

## `dll-LPAR.pl`

The four element DLL used as the running example for the LPAR23 publication.

## `dll-stable-null-inner-ep.pl`

A doubly linked list where the entry pointer points to an inner node of the dll.

## `dll-stable-null.pl`

A doubly linked list with three elements; NULL terminated.

## `dll-stable-this.pl`

A doubly linked list with three elements dll; self terminated.

## `dll-unstable-null.pl`

A doubly linked list with three elements where the prev pointer of the last node
is set to NULL; NULL terminated.

## `lasso-dual-ep.pl`

A lasso (pan-handle list) where the beginning of the list and the beginning of
the cycle is denoted by an entry pointer. Can be learned via ShaPE.

## `lasso.pl` 🚨

A lasso (pan-handle list) where only the first node of the initial list is
pointed to by an entry pointer. This cannot be solved by ShaPE, because one
cannot forsee if the next node is the first node of the cycle.

## `logo.pl`

A pan-handle list with an initial list segment of fixed length one. This is the
memory graph of the ShaPE logo.

## `nesting-bt-sll.pl`

A parent binary tree with a child nested singly linked list.

## `nesting-csll-bt.pl`

A parent cyclic singly linked list with a child nested binary tree.

## `nesting-sll-bt.pl`

A parent singly linked list with a child nested binary tree.

## `SHN-sll-sll.pl`

A shared head node (`wrapper`) that points to two unshared singly linked lists.

## `skip-list-generic.pl` 🚨

A generic skip list whose shape predicate cannot be learned via ShaPE.

## `sll-and-bt.pl`

A memory graph with two unshared sub-graphs that exhibit a singly linked list
and a binary tree.

## `sll-headPtr.pl`

A singly linked list with an additional pointer pointing to the head, i.e.,
first element of the lists.

## `lseg.pl`

A singly linked list with two entry pointers pointing to the first and last node
of the list.

## `sll-null.pl`

A simple singly linked list; NULL terminated.

## `sll-tailPtr.pl`

A singly linked list with an additional pointer pointing to the tail, i.e., last
element of the lists.

## `sll-this.pl`

A simple singly linked list; self terminated.

## `wrapper-sll-bt.pl`

A wrapper node (`wrapper`) that points to two unshared sub-graphs exhibiting a
singly linked list and binary tree.

## `wrapper-thesis.pl`

A wrapper node (`wrapper`) that points to two unshared sub-graphs exhibiting a
singly linked list and cyclic singly linked list.

## `series-bt\`

A series of three memory graphs exhibiting a simple binary tree shape:
`bt-null-1.pl`, `bt-null-2.pl`, and `bt-null-3.pl`.

## `series-sll-and-bt\`

A series of three memory graphs exhibiting an unshared singly linked list and
binary tree: `sll-and-bt-0.pl`, `sll-and-bt-1.pl`, and `sll-and-bt-2.pl`.
