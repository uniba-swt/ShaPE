#!/usr/bin/env python3
"""
Provides means to learn a shape predicate from homogeneously typed memory graphs.
"""

from typing import List

from . import pruning
from . import search
from . import rules
from .model import MemoryGraph
from .helper import ShaPEexception, logger, timer


@timer
def learn(memory_graphs: List[MemoryGraph]) -> List[str]:
    """
    Infers a shape predicate from homogeneously typed memory graphs.

    :param memory_graphs: A non-empty list of homogeneously typed memory graphs.
    :return: A shape predicate.
    """

    fields = memory_graphs[0].fields()
    ep_count = len(memory_graphs[0].entrypoints())

    for complexity in rules.generator(fields, ep_count):
        logger().debug(
            f'using complexity {complexity}'
        )
        rules_ = rules.generateRules(
            complexity
        )
        logger().debug(
            f'rules before pruning: {len(rules_)}'
        )
        rules_ = pruning.pruneRules(rules_, memory_graphs)
        logger().debug(
            f'rules after pruning: {len(rules_)}'
        )

        try:
            return search.search(rules_, memory_graphs)
        except ShaPEexception:
            pass
    raise ShaPEexception('could not find a matching shape predicate')
