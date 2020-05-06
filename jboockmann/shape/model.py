#!/usr/bin/env python3
'''
Provides the `MemoryGraph` class as a means to encode
and operate on memory graphs.
'''

import json
import re
from typing import Dict, List, Union

from graphviz.dot import Digraph

from . import constants
from . import helper


def vertexAbstraction(
        vertices: List[Dict[str, Union[str, List[Dict[str, str]]]]],
        fields: List[str]
) -> List[Dict[str, str]]:
    '''
    Computes the node abstraction given a list of vertices and field names as
    input. In this abstraction, each field points to one of the following
    values:

    1. `null`
    2. `This`
    3. `VarX` where `VarX` is bound
    4. `VarY` where `VarY` is free

    Observe that a later value implies that the value is not equal to any
    predecessor, e.g., a value of `VarX` implies that the value is neither equal
    to `null` or `This`. Also note that two different `Var` values encode
    different values. Finally, observe that the abstraction is computed along
    the order of the provided fields.

    For example, the assignment `{'left': '6', 'right': '7'}` yields `{'left':
    'Var0', 'right': 'Var1'}`. Whereas the assignment `{'left': '8', 'right':
    '8'}` yields `{'left': 'Var0', 'right': 'Var0'}`.
    '''
    abstractions = []
    for vertex in vertices:
        assignment = {}
        for va in vertex['assignment']:
            assignment[va['name']] = va['value']

        abstraction = {}
        varCtr = 0
        for (pos, field) in enumerate(fields):
            if assignment[field] == constants.NULL_UPPER:
                abstraction[field] = constants.NULL_LOWER
            elif assignment[field] == vertex['id']:
                abstraction[field] = 'This'
            else:
                previous = fields[:pos]
                for p in previous:
                    if assignment[field] == assignment[p]:
                        abstraction[field] = abstraction[p]
                if not field in abstraction:
                    abstraction[field] = f'Var{varCtr}'
                    varCtr += 1
        abstractions.append(abstraction)
    result = [dict(t) for t in {tuple(sorted(d.items()))
                                for d in abstractions}]
    return result


class MemoryGraph(object):
    '''Encodes a memory graph object and provides functions to retrieve
    values, e.g., `MemoryGraph.vertices` returning all vertices of the graph.
    Furthermore, static functions are provided to create a new instance of a
    memory graph, e.g., `MemoryGraph.fromPLFile` expecting a Prolog
    file as input.'''

    def __init__(self) -> None:
        self.json = None
        '''
        Representation of the memory graph in JSON format.
        '''

    def vertices(self) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
        '''
        Returns the structs of the memory graph as denoted in the `vertices`
        section of the JSON string.
        '''
        return self.json['vertices']

    def structs(self) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
        '''
        Returns the structs of the memory graph as denoted in the `structs`
        section of the JSON string.
        '''
        return self.json['structs']

    def entrypoints(self) -> List[Dict[str, str]]:
        '''
        Returns the entry points of the memory graph as denoted in the `entrypoints`
        section of the JSON string.
        '''
        return self.json['entrypoints']

    def entrypoint(self) -> str:
        '''
        Returns the entry pointer for a memory graph with a single entry
        pointer.
        '''
        assert len(self.entrypoints()) == 1
        return self.entrypoints()[0]

    def fields(self) -> List[str]:
        '''
        Returns the field names for a memory graph with a single struct as
        denoted in the `structs` section of the JSON string.
        '''
        assert len(self.structs()) == 1
        fields = self.structs()[0]['fields']
        fields = [f['name'] for f in fields]
        return fields

    def detect_entrypointers(self):
        '''
        Detects nodes that are most likely entry pointers to the graph, which is
        useful during translation to a memory graph from an input format that
        does not (properly) support entry pointers. For example, points-to
        graphs from *DSI* often capture too many possible entry pointers. This
        function supports the detection of multiple entry points, i.e., when the
        graph contains disjunct sub graphs.

        A node `n1` is considered to likely be an entry pointer if there does
        not exist another node `n2` that reaches the same and more nodes
        compared to `n1`.

        Note that this approach can be made more sophisticated by minimizing the
        usage of fields. A *field reachability analysis* can be conducted to
        select the node as an entry node that can *a)* reach all nodes of the
        separate graph, and *b)* reach all nodes using a minimal number of
        different fields. Consider the graph of a binary tree with parent
        pointers where the root node is to be preferred over an inner tree node.
        '''
        node2nodes = {}
        for node in self.vertices():
            node2nodes[node["id"]] = self.reachableNodes(node["id"])

        for node in [k for k in node2nodes.keys()]:
            # check if the entry still exists
            if not node in node2nodes.keys():
                continue
            # remove the entry of each reachable node
            for rnode in node2nodes[node]:
                if rnode == node:
                    continue
                node2nodes.pop(rnode, None)

        # recreate the entrypoints
        entrypoints = []
        for pos, key in enumerate(node2nodes.keys()):
            ep = [v for v in self.vertices() if v["id"] == key][0]
            ep_dct = {
                "name": f"ep{pos}",
                "target": ep["id"],
                "type": ep["struct"]
            }
            entrypoints.append(ep_dct)

        # update the entry points of the memory graph
        self.json["entrypoints"] = entrypoints

    def reachableNodes(self, node: str, fields: str = None) -> List[str]:
        """
        Returns a list containing the ID of each node reachable from the node
        with ID `node`. The ID of reachable nodes always contain the id of the
        starting node. Note that the implemented graph traversal algorithm
        detects and handles cycles in graphs accordingly. The optional parameter
        `fields` contains a list of field names that shall be considered during
        the reachability analysis. By default, i.e., `fields` is `None`, all
        fields are considered.
        """
        lst = []
        stack = [node]
        while stack:
            top = stack.pop()
            topNode = [v for v in self.vertices() if v["id"] == top][0]
            if fields is None:
                rnodes = [a["value"] for a in topNode["assignment"]]
            else:
                rnodes = [
                    a["value"]
                    for a in topNode["assignment"]
                    if a["name"] in fields
                ]
            for rnode in rnodes:
                if rnode == "NULL":
                    # ignore NULL values
                    continue
                if rnode in lst:
                    # we have already visited this node
                    continue
                stack.append(rnode)
            lst.append(top)
        return lst

    def synthCStructDef(self) -> str:
        '''
        Synthesizes C code that resembles a C struct definition.
        '''
        chunks = []
        for struct in self.structs():
            name = struct['name']
            chunks.append(f'struct {name} {{')
            for field in struct['fields']:
                ttype = field['type']
                tname = field['name']
                chunks.append(f'struct {ttype}* {tname};')
            chunks.append('};\n')
        return '\n'.join(chunks)

    def structOfVertex(self, id: str) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        '''
        Returns the struct name of a vertex given its ID.
        '''
        vertices = [v for v in self.vertices() if v['id'].capitalize() == id]
        assert len(vertices) == 1
        vertex = vertices[0]
        return vertex["struct"]

    def vertexAbstractionEPs(self) -> List[Dict[str, str]]:
        '''
        Computes a dictionary mapping entry pointer names to their nodes vertex
        abstraction. This is internally performed using function
        `vertexAbstraction`. 
        '''
        abstractions = {}
        for ep in self.entrypoints():
            vertex = [v for v in self.vertices() if ep["target"] == v["id"]][0]
            abstraction = vertexAbstraction([vertex], self.fields())
            abstractions[ep["name"]] = abstraction
        return abstractions

    def vertexAbstractionEP(self) -> List[Dict[str, str]]:
        '''
        Computes a node abstraction for the single entry node using function
        `vertexAbstraction`. 
        '''
        return self.vertexAbstractionEPs()[self.entrypoint()["name"]]

    def vertexAbstractionOthers(self) -> List[Dict[str, str]]:
        '''
        Computes a node abstraction for non entry nodes using
        `vertexAbstraction`. 
        '''
        entrypoints = [v["target"] for v in self.entrypoints()]
        vertices = [
            v for v in self.json['vertices']
            if v['id'] not in entrypoints
        ]
        return vertexAbstraction(vertices, self.fields())

    def synthPrologFacts(self) -> List[str]:
        data = self.json
        clauses = []

        for vertex in data['vertices']:
            clause = 'node({id}).'.format(id=vertex['id'])
            clauses.append(clause)
            for assignment in vertex['assignment']:
                target: str
                if assignment['value'] == constants.NULL_UPPER:
                    target = constants.NULL_LOWER
                else:
                    target = '{id}'.format(id=assignment['value'])
                clause = '{field}({id}, {target}).'.format(
                    field=assignment['name'], id=vertex['id'], target=target
                )
                clauses.append(clause)

        return clauses

    def constructDot(self) -> Digraph:
        '''
        Transforms the memory graph into an instance of class `Dot.Digraph`.
        '''
        dot = Digraph(comment='', format='dot')

        for vertex in self.vertices():
            dot.node(vertex['id'], '{}@{}'.format(
                vertex['id'], vertex['struct']))

        for vertex in self.vertices():
            for assignment in vertex['assignment']:
                if assignment['value'] != constants.NULL_UPPER:
                    dot.edge(
                        vertex['id'],
                        assignment['value'],
                        label=assignment['name']
                    )

        for entrypoint in self.entrypoints():
            dot.node(entrypoint['name'], entrypoint['name'])
            dot.edge(entrypoint['name'], entrypoint['target'])

        return dot

    @staticmethod
    def fromJSON(content: str) -> 'MemoryGraph':
        '''
        Creates a new `MemoryGraph` object from a JSON string or dictionarys.

        The listing below indicates the singly-linked list example from
        `./examples/sll-null.pl` in JSON format:
        ```
        {
            "structs": [
                {
                    "name": "struct0",
                    "fields": [
                        {
                            "type": "struct0",
                            "name": "next"
                        }
                    ]
                }
            ],
            "vertices": [
                {
                    "id": "n1",
                    "assignment": [
                        {
                            "name": "next",
                            "value": "n2",
                            "type": "struct0"
                        }
                    ],
                    "struct": "struct0"
                },
                {
                    "id": "n2",
                    "assignment": [
                        {
                            "name": "next",
                            "value": "n3",
                            "type": "struct0"
                        }
                    ],
                    "struct": "struct0"
                },
                {
                    "id": "n3",
                    "assignment": [
                        {
                            "name": "next",
                            "value": "NULL",
                            "type": "struct0"
                        }
                    ],
                    "struct": "struct0"
                }
            ],
            "entrypoints": [
                {
                    "name": "ep0",
                    "target": "n1",
                    "type": "struct0"
                }
            ]
        }
        ```
        '''
        memoryGraph = MemoryGraph()
        if type(content) == str:
            memoryGraph.json = json.loads(content)
        elif type(content) == dict:
            memoryGraph.json = content
        else:
            assert False
        return memoryGraph

    @staticmethod
    def fromFile(filename: str):
        if filename.endswith(".json"):
            return MemoryGraph.fromJSONFile(filename)
        elif filename.endswith(".pl"):
            return MemoryGraph.fromPLFile(filename)
        elif filename.endswith(".dot"):
            return MemoryGraph.fromDOTFile(filename)
        else:
            raise Exception("Unknown file ending.")

    @staticmethod
    def fromJSONFile(filename: str):
        '''
        Creates a new `MemoryGraph` object given the path to a JSON file.
        '''
        with open(filename, r'r') as f:
            return MemoryGraph.fromJSON(json.load(f))

    @staticmethod
    def fromDOTFile(filename: str) -> 'MemoryGraph':
        '''
        Creates a new `MemoryGraph` object given the path to a DOT file
        containing a points-to graph derived from the *DSI* tool.
        '''
        helper.logger().debug(
            f"Translating the points-to graph file {filename} ...")
        with open(filename, r'r') as f:
            data = f.read()
            json_ = helper.pointstograph_to_JSON(data)
            memoryGraph = MemoryGraph.fromJSON(json_)
            memoryGraph.detect_entrypointers()
            return memoryGraph

    @staticmethod
    def fromPLFile(filename: str) -> 'MemoryGraph':
        '''
        Creates a new `MemoryGraph` object given the path to a PL file. The
        Prolog code is assumed to comply with the following notation:

        - empty and commented out lines are allowed, but dropped during parsing
        - the `node` predicate encodes vertices, e.g., `node(n1)` encodes a
          vertex with name `n1`
        - the `entrypoint` predicate denotes entrypoints of the memory graph,
          e.g., `entrypoint(n1)` denotes that `n1` is an entrypoint to the
          graph. Note that this requires a corresponding node statement.
        - any other predicate is assumed to be a field name, e.g., `next(n1,
          n2)` states that field `next` of vertex `n1` points to vertex `n2`.
          Mind the space between the first and second argument.

        The listing below indicates the singly-linked list example from
        `./examples/sll-null.pl`:
        ```
        node(n1).
        node(n2).
        node(n3).

        next(n1, n2).
        next(n2, n3).
        next(n3, null).

        entrypoint(n1).
        ```

        Finally, note that type information is not stored in the Prolog program,
        but required by the JSON format used to encode a memory graph. Hence,
        type information is reverse engineered assuming that same fields belong
        to the same struct and different fields belong to different structs.
        '''
        helper.logger().debug(f"Translating the Prolog file {filename} ...")
        facts = None
        with open(filename, 'r') as f:
            facts = f.read().splitlines()

        vertices = []
        entrypoints = []
        structs = []

        # drop empty lines
        facts = list(filter(lambda f: f, facts))

        # drop comments
        facts = list(filter(lambda f: not f.startswith('%'), facts))

        entrypointsCtr = 0

        for f in facts:
            fact = re.search(r'(\w+)\((\w+)(?:, (\w+))*\).', f).groups()
            fact = list(filter(lambda f: f, fact))
            if fact[0] == 'node':
                vertices.append({'id': fact[1], 'assignment': []})
            elif fact[0] == 'entrypoint':
                entrypoints.append(
                    {'name': 'ep%s' % entrypointsCtr, 'target': fact[1]})
                entrypointsCtr += 1
            else:
                field = fact[0]
                src = fact[1]
                dst = fact[2]
                if dst == 'null':
                    dst = 'NULL'
                vertex = [v for v in vertices if v['id'] == src][0]
                vertex['assignment'].append({'name': field, 'value': dst})

        # resynth type information
        fields2nodes = {}
        for v in vertices:
            fields = list(map(lambda a: a['name'], v['assignment']))
            fields.sort()
            if str(fields) not in fields2nodes.keys():
                fields2nodes[str(fields)] = []
            fields2nodes[str(fields)].append(v['id'])
        helper.logger().debug(f"fields2nodes: {fields2nodes}")

        structCtr = 0
        fields2struct = {}
        vertexid2struct = {}

        for _, nodes in fields2nodes.items():
            struct = 'struct%s' % structCtr
            fields2struct[struct] = nodes
            structCtr += 1
            for n in nodes:
                vertexid2struct[n] = struct
        helper.logger().debug(f"vertexid2struct: {vertexid2struct}")

        for v in vertices:
            v['struct'] = vertexid2struct[v['id']]
            for a in v['assignment']:
                # edge case: when a single node points to NULL, we cannot
                # resynth the type it points to. In such a situation, we assume
                # that its a pointer to the struct itself.
                if a['value'] != 'NULL':
                    a['type'] = vertexid2struct[a['value']]
                else:
                    a['type'] = vertexid2struct[v['id']]

        for structname in sorted(list(set(vertexid2struct.values()))):
            typeVerticeIDs = [x for x in vertexid2struct.keys(
            ) if vertexid2struct[x] == structname]
            typeVertices = [x for x in vertices if x['id'] in typeVerticeIDs]
            fields = []
            for tv in typeVertices:
                ass = tv['assignment']
                for a in ass:
                    if not 'type' in a:
                        continue
                    vertexfield = {'type': a['type'], 'name': a['name']}
                    if not vertexfield in fields:
                        fields.append(vertexfield)
            struct = {'name': structname, 'fields': fields}
            structs.append(struct)

        for ep in entrypoints:
            ep['type'] = vertexid2struct[ep['target']]

        for v in vertices:
            for a in v['assignment']:
                if not 'type' in a.keys():
                    struct = [
                        s for s in structs
                        if s['name'] == v['struct']
                    ][0]
                    xxx = [
                        x['type'] for x in struct['fields']
                        if x['name'] == a['name']]
                    if xxx:
                        xxx = xxx[0]
                        a['type'] = xxx

        memoryGraph = MemoryGraph()
        memoryGraph.json = {
            'structs': structs,
            'vertices': vertices,
            'entrypoints': entrypoints
        }

        return memoryGraph
