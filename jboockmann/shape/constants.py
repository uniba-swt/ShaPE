#!/usr/bin/env python3

from . import helper
from . import pruning

RE_VARS = r'[A-Z]\w*'
NULL_LOWER = 'null'
NULL_UPPER = 'NULL'
PNAME_ENTRY = 'entry'
PNAME_OTHER = 'p'
RE_FIELD_ASSIGNMENT = r' (?!p\_?\()([a-zA-Z0-9]+)\(This, (\w+)\)'
RE_REC_CALLS = r'p\(\w+(?:, \w+)*\)'
CLI_SHOW_STACK_TRACE = True

RE_METAINFORMATION: str = r'condition\((\d+), (\d+)\)'
'''
Regular expression to capture the 1st and 2nd parameter of a condition
predicate, i.e., rule ID and condition group ID, as a tuple.
'''

RE_METAINFORMATION_SUB = r'condition\(\d+, \d+\), '
'''
Regular expression to replace condition clauses capturing metainformation, i.e.,
rule ID and condition ID.
'''

RE_INEQ_SUB = r', \w+ \\= \w+'
'''
Regular expression to replace inequality clauses.
'''
RE_FRESH_SUB = r', fresh\(\w+\)'
'''
Regular expression to replace freshness clauses.
'''

RE_FIELDNAMES = r'(\w+)\(This, \w+\)'
'''
Regular expression to extract field names from a rule.
'''

DELIMITER_RULE = r' :- '
'''
Delimiter string to split a Prolog rule into its head and body.
'''

MI_INFER = f'{helper.getModuleFolder()}/mi_seplog.pl'
'''
Path to the meta-interpreter used for the rule search.
'''

DEBUG_CODEC = 'code.c'
'''
Store generated C code, e.g., when synthesizing the proof witness to be checked
by verifast, in this file.
'''

DEBUG_CODEPL = 'code.pl'
'''
Store generated Prolog code, e.g., when conducting a rule search, in this file.
'''

LOGGING_CONFIG = "logging.ini"
'''
The path to the logging configuration file.
'''

TIMEOUT_VERIFAST = 30
'''
Timeout for the verifast program verifier.
'''

TIMEOUT_PROLOG = 180
'''
Timeout for the prolog interpreter.
'''

BIN_VERIFAST = 'verifast'
'''
Command line name for the verifast program verifier executable.
'''

BIN_SWIPL = 'swipl'

FOLDER_TEMPLATES = f'{helper.getModuleFolder()}/rules-templates'
'''
Denotes the folder in which rules templates are stored.
'''

LIMIT_PARAMS = 3

COMPARATORS_DEFAULT = [
    (pruning.comparator_pname, 1),
    (pruning.comparator_calls, 1),
    (pruning.comparator_nullArgs, 1),
    (pruning.comparator_nullParams, 1),
    (pruning.comparator_paramsAsArgs, 1)
]
