#!/usr/bin/env python3
import json
import os
import tempfile

from . import composition, constants, helper, learn, match, verifast
from .helper import logger
from .model import MemoryGraph

from typing import Optional


class FireCLI(object):

    @staticmethod
    def learn(*memory_graph_paths: str):
        """
        Infers a shape predicate matching a list of input memory graphs.

        :param memory_graph_paths: A non-empty list of paths containing memory graphs.
        :return: None
        """
        memory_graphs = list(
            map(lambda p: MemoryGraph.fromFile(p), memory_graph_paths))
        rules = learn.learn(memory_graphs)

        logger().info("The learned rules are:")
        for rule in rules:
            logger().info(rule)

    @staticmethod
    def composition(*memory_graph_paths: str):
        memory_graphs = list(
            map(lambda p: MemoryGraph.fromFile(p), memory_graph_paths)
        )
        rules = composition.composition(memory_graphs)
        logger().info("The learned rules are:")
        for rule in rules:
            logger().info(rule)

    @staticmethod
    def match(*memory_graph_paths: str, template_path=None) -> None:
        """
        Check whether any or a predefined shape template match with respect to
        an input list of memory graphs.

        :param memory_graph_paths: A non-empty list of paths containing memory graphs.
        :param template_path:
        :return: None
        """
        memory_graphs = list(
            map(lambda p: MemoryGraph.fromFile(p), memory_graph_paths))

        if template_path is None:
            rules = match.match_repository(memory_graphs)
        else:
            template = helper.parseRulesTemplate(template_path)
            rules = match.match_template(memory_graphs, template)

        logger().info("The learned rules are:")
        for rule in rules:
            logger().info(rule)

    @staticmethod
    def convert(memory_graph: str):
        """
        Converts a memory graph from .pl or .dot format to .json format.

        :param memory_graph: The path to the memory graph.
        :return: None
        """
        name, _ = os.path.splitext(memory_graph)
        output_file = f'{name}.json'
        logger().info(
            f'Translating MemoryGraph from "{memory_graph}" to "{output_file}"'
        )
        memory_graph = MemoryGraph.fromFile(memory_graph)
        with open(output_file, 'w') as f:
            f.write(json.dumps(memory_graph.json, indent=4))
            f.flush()

    @staticmethod
    def visualize(memory_graph: str):
        """
        Visualizes a memory graph using the dot package.

        :param memory_graph: The path to the memory graph.
        :return: None
        """
        logger().info(f'Visualizing memory graph "{memory_graph}"')
        memory_graph = MemoryGraph.fromFile(memory_graph)
        dot = memory_graph.constructDot()
        dot.render(
            view=True,
            cleanup=True,
            directory=tempfile.TemporaryDirectory().name
        )


def main():
    import fire
    try:
        fire.Fire(FireCLI)
    except helper.ShaPEexception as e:
        if constants.CLI_SHOW_STACK_TRACE:
            raise e
        logger().error(f'An exception occurred while executing your command.')
        logger().error(f'Type: {type(e)}')
        logger().error(f'Reason: {str(e)}')
