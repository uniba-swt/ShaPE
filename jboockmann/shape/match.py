#!/usr/bin/env python3
"""
Provides the match functionality of ShaPE. It can be used to match memory graphs
against (1) a concrete predicate, (2) a predicate template, or (3) all
predefined templates.
"""

import copy
from glob import glob
from typing import List

from . import constants
from . import helper
from . import search
from . import verifast
from .model import MemoryGraph
from .helper import ShaPEexception, logger


def match_repository(
        memory_graphs: List[MemoryGraph]
) -> List[str]:
    """
    Matches memory graphs against the templates in the repository and returns the first match.

    :param memory_graphs: A non-empty list of memory graphs.
    :return: A matching shape predicate.
    :raises ShaPEexception: If no template in the repository matches.
    """
    template_files = glob(f'{constants.FOLDER_TEMPLATES}/*.pl')
    for template_file in template_files:
        logger().debug(f'Checking template: {template_file}')
        template = helper.parseRulesTemplate(template_file)
        try:
            predicate = match_template(memory_graphs, template)
            verifast.check_witness(
                verifast.construct_witness(predicate, memory_graphs)
            )
            return template
        except ShaPEexception:
            pass
    raise ShaPEexception(
        'No template in the repository matches the memory graphs.'
    )


def match_template(
        memory_graphs: List[MemoryGraph],
        template: List[str] = None
) -> List[str]:
    """
    Checks if the memory graphs match with respect to the provided template.

    :param memory_graphs: A non-empty list of memory graphs.
    :param template: The shape template.
    :return: Rules matching the input memory graphs.
    :raises ShaPEexception: If the template does not match the memory graphs.
    """
    for predicate in derive_predicates(memory_graphs, template):
        try:
            match_predicate(memory_graphs, predicate)
            verifast.check_witness(
                verifast.construct_witness(predicate, memory_graphs)
            )
            return predicate
        except ShaPEexception:
            pass
    raise ShaPEexception('The template does not match the memory graphs.')


def match_predicate(
        memory_graphs: List[MemoryGraph],
        predicate: List[str]
) -> None:
    """
    Checks if a predicate match a list of memory graphs.

    :param memory_graphs: The memory graphs.
    :param predicate: The predicate.
    :return: None.
    :raises ShaPEexception: If the rules do not match.
    """
    search.search(
        predicate,
        memory_graphs
    )


def derive_predicates(
        memory_graphs: List[MemoryGraph],
        template: List[str]
) -> List[List[str]]:
    """
    Resolves the ambiguous field mapping between the type information of the memory graphs and a predicate template
    by explicitly enumerating all candidate predicates.

    :param memory_graphs: The memory graphs.
    :param template: The predicate template.
    :raises ShaPEexception: If the type information is not compatible with the memory graphs.
    :return: A list of possible predicates.
    """
    helper.homogeneously_typed(memory_graphs)

    template_fields = helper.extractFieldNames(template)

    if len(memory_graphs[0].json['structs'][0]['fields']) != len(template_fields):
        raise ShaPEexception(
            'Number of struct fields in template do not match the number of fields present in the memory graphs.'
        )

    fields = memory_graphs[0].fields()

    # compute possible field name mappings
    mappings = [{}]  # map template field to actual field

    for templateField in template_fields:
        stack_ = []
        for top in mappings:
            for mgField in [f for f in fields if f not in top.values()]:
                top2 = copy.deepcopy(top)
                top2[templateField] = mgField
                stack_.append(top2)
        mappings = stack_
    logger().debug(f"Number of possible mappings: {len(mappings)}")

    # apply mappings by replacing fields to derive possible rules
    mapped_rules = []
    for dct in mappings:
        # turn dictionary into list of tuples
        changes_lower = [
            (key, value)
            for (key, value) in dct.items()
        ]
        # capitalize to capture capitalized variables as well
        changes_capitalize = [
            (key.capitalize(), value.capitalize())
            for (key, value) in dct.items()
        ]
        changes = changes_lower + changes_capitalize
        mapped_rules.append(
            [
                helper.multireplace(r, changes) for r in copy.deepcopy(template)
            ]
        )
    return mapped_rules
