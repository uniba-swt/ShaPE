#!/usr/bin/env python3

import itertools
import json
import re
import subprocess
from typing import List, Optional

from . import constants, pruning, search
from .helper import ShaPEexception, logger
from .model import MemoryGraph

VERIFAST_WITNESS_TEMPLATE = """
# include <stdlib.h>
# include <stdio.h>

{type_information}

/*@
{predicates}
@*/

void check({entry_points})
//@ requires {check_contract}
//@ ensures  {check_contract}
{{
    // trigger verifast
}}

{input_functions}

int main(void)
//@ requires emp;
//@ ensures emp;
{{
printf("Executing main ... \\n");

{input_function_calls}
return 0;

}}
"""

INPUT_FUNCTION_TEMPLATE = """
void input_{position}()
//@ requires emp;
//@ ensures  emp;
{{
// allocate vertices
{allocate_vertices}

// update fields
{update_assignment}

// define entrypointers
{define_entrypointers}

// invoke check function
{invoke_check_function}

// leak chunks
{leak_chunks};
}}
"""


def check_witness(program: str, outputfile=None, timeout=None) -> None:
    """
    Runs the VeriFast program verifier on the supplied program.

    :param program: The annotated program to be verified.
    :param outputfile: The path to the file where the program is written to.
    :param timeout: Timeout in seconds.
    :raises ShaPEexception: If VeriFast returns a non-zero exit code or on a timeout.
    :return: None.
    """
    if outputfile is None:
        outputfile = constants.DEBUG_CODEC
    if timeout is None:
        timeout = constants.TIMEOUT_VERIFAST

    # write program to file
    with open(outputfile, 'w') as file_:
        file_.write(program)
        file_.write("\n")
        file_.flush()

    # invoke verifast
    p = subprocess.Popen(
        f'{constants.BIN_VERIFAST} -shared {outputfile}',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        raise ShaPEexception("verifast caused a timeout")

    out = out.decode("utf-8")
    err = err.decode("utf-8")

    if p.returncode != 0:
        logger().warning(
            f'verifast failed with non-zero exit code {p.returncode}')
        logger().warning(f'STDERR: {err}')
        logger().warning(f'STDOUT: {out}')
        raise ShaPEexception('verifast failed with non-zero exit code.')


def distribute_by_predicate_name(rules: List[str]):
    """
    returns a list of lists where each sublist contains all rules sharing the
    same predicate name.
    """
    name_to_rules = {}
    for rule in rules:
        name = rule.split(r"(")[0]
        if name not in name_to_rules.keys():
            name_to_rules[name] = []
        name_to_rules[name].append(rule)
    return name_to_rules


def translate(rules: List[str], struct=Optional[str]):
    """
    translates a list of PL rules to a verifast predicate. the struct name is
    required by verifast, but not contained in the rules.
    """
    rule = rules[0]
    head, _ = rule.split(constants.DELIMITER_RULE)
    name = head.split("(")[0]
    parameters = head.split("(")[1].split(")")[0].split(", ")
    typed_parameters = [f"struct {struct}* {p}" for p in parameters]
    signature = f"predicate {name}({', '.join(typed_parameters)};)"
    malloc_clause = f"malloc_block_{struct}(This)"

    field_clauses = []
    for field, value in pruning.extractFieldAssignment(rules[0]).items():
        field_clauses.append(f"This->{field} |-> ?{value}")

    ternaries = []
    for rule in rules:
        equalities = pruning.extractEqualities(rule)
        inequalities = pruning.extractInequalities(rule)
        calls = pruning.extractCalls(rule)
        if not calls:
            calls = ["emp"]
        assertions = equalities + inequalities
        ternaries.append(
            "{} ?\n\t\t{}\n".format(
                " && ".join(assertions),
                " &*& ".join(calls)
            )
        )
    ternaries_ = " : ".join(ternaries)
    ternary = f"{ternaries_} : false"

    predicate_body = f"\n\t{malloc_clause} &*&\n\t{' &*& '.join(field_clauses)} &*&\n{ternary};"

    # ugly hack
    predicate_body = predicate_body.replace(r"null", r"NULL")
    predicate_body = predicate_body.replace(r" = ", r" == ")
    predicate_body = predicate_body.replace(r"\=", r"!=")

    return f"{signature} = \n{predicate_body}"


def standardize_rules(rules: List[str]):
    """
    standardize rules to have the same rule head. add equality and inequality
    clauses. fields point to a fresh variable and adds the resp. equality
    clause.
    """
    rules_ = []
    for rule in rules:
        rule = search.inject_inequalities(rule)
        head, tail = rule.split(constants.DELIMITER_RULE)
        name = head.split("(")[0]
        parameters = head.split("(")[1].split(")")[0].split(", ")
        clauses = list(re.findall(r"\w*\(\w*(?:, \w*)*\)", tail))
        call_clauses = [c for c in clauses if c.startswith(
            "p(") or c.startswith("p_")]
        logger().debug(f'call_clauses: {call_clauses}')

        inequalities = list(re.findall(r"\w* \\= \w*", tail))

        equalities = []

        # standardize parameters
        parameters_ = []
        for position, parameter in enumerate(parameters):
            # first This that appears in the parameters
            if parameter == "This" and "This" not in parameters[1:position]:
                parameters_.append(parameter)
                continue
            # replace with P{position} and add resp. equality
            parameters_.append(f"P{position}")
            if parameter != f"P{position}":
                equalities.append(f"P{position} = {parameter}")
        parameters = parameters_

        # standardize fields
        field_clauses = []
        for field, value in pruning.extractFieldAssignment(rule).items():
            field_clauses.append(f"{field}(This, {field.capitalize()})")
            if value != field.capitalize():
                equalities.append(f"{field.capitalize()} = {value}")

        rule_ = f"{name}({', '.join(parameters)}) {constants.DELIMITER_RULE} node(This), {', '.join(field_clauses + equalities + inequalities + call_clauses + ['true'])}."
        rules_.append(rule_)
    return rules_


def build_input_functions(memory_graphs: List[MemoryGraph]):
    """
    Constructs the C code for the input functions.
    """
    input_functions = []
    for position, memory_graph in enumerate(memory_graphs):
        # allocate_vertices
        chunks = []
        for vertex in memory_graph.vertices():
            struct = vertex["struct"]
            name = vertex["id"]
            chunk = (
                f"struct {struct}* {name} = malloc(sizeof(struct {struct}));\n"
                f"if({name} == NULL){{abort();}}"
            )
            chunks.append(chunk)
        allocate_vertices = "\n".join(chunks)
        # allocate_vertices

        # update_assignment
        chunks = []
        for vertex in memory_graph.vertices():
            name = vertex["id"]
            for assignment in vertex["assignment"]:
                field = assignment["name"]
                value = assignment["value"]
                chunks.append(f"{name}->{field} = {value};")
            chunks.append("")
        update_assignment = "\n".join(chunks)
        # update_assignment

        # define_entrypointers
        define_entrypointers = "\n".join([
            f"struct {ep['type']}* {ep['name']} = {ep['target']};" for ep
            in memory_graph.entrypoints()
        ])
        # define_entrypointers

        # invoke_check_function
        invoke_check_function = "check({});".format(
            ', '.join(
                [ep["name"] for ep in memory_graph.entrypoints()]
            )
        )
        # invoke_check_function

        # leak_chunks
        leak_chunks = "//@ leak entry({})".format(
            ', '.join(
                [ep["name"] for ep in memory_graph.entrypoints()]
            )
        )
        # leak_chunks

        input_functions.append(INPUT_FUNCTION_TEMPLATE.format(
            position=position,
            allocate_vertices=allocate_vertices,
            update_assignment=update_assignment,
            define_entrypointers=define_entrypointers,
            invoke_check_function=invoke_check_function,
            leak_chunks=leak_chunks
        ))
    return input_functions


def construct_witness(
        rules: List[str],
        memory_graphs: List[MemoryGraph]
) -> str:
    """
    Constructs a proof witness for a list of rules and memory graphs.

    :param rules: A list of rules containing a predicate, i.e., entry and p rules.
    :param memory_graphs: A non-empty list of memory graphs.
    :return: The constructed program.
    """
    rules = standardize_rules(rules)
    name2rules = distribute_by_predicate_name(rules)
    name2predicate = {}

    # remove duplicate structs
    structs = list(itertools.chain(
        *[m.structs() for m in memory_graphs]
    ))
    structs = list(set(
        [json.dumps(s) for s in structs]
    ))
    structs = [json.loads(s) for s in structs]

    if len(structs) == 1:
        default_struct_name = structs[0]["name"]

    for name, rules in name2rules.items():
        # TODO: remove hard-coded struct information
        name2predicate[name] = translate(rules, default_struct_name)

    input_functions = build_input_functions(memory_graphs)

    input_function_calls = "\n".join(
        [
            f"input_{position}();"
            for position, value
            in enumerate(memory_graphs)
        ]
    )

    # entry_points
    entry_points = ", ".join(
        [
            f"struct {ep['type']}* {ep['name']}" for ep in memory_graphs[0].entrypoints()
        ]
    )
    # entry_points

    # check_contract
    check_contract = "entry(" + ", ".join(
        [
            f"{ep['name']}" for ep in memory_graphs[0].entrypoints()
        ]
    ) + ");"
    # check_contract

    program = VERIFAST_WITNESS_TEMPLATE.format(
        type_information=memory_graphs[0].synthCStructDef(),
        predicates="\n\n".join(name2predicate.values()),
        entry_points=entry_points,
        check_contract=check_contract,
        input_functions="\n\n".join(input_functions),
        input_function_calls=input_function_calls
    )

    # check_witness(program)
    return program
