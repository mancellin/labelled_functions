#!/usr/bin/env python
# coding: utf-8

from typing import Set
from labelled_functions.abstract import AbstractLabelledCallable
from labelled_functions.labels import Unknown, LabelledFunction
from toolz.itertoolz import groupby
from toolz.dicttoolz import merge, keyfilter
from collections import namedtuple

# API
# Builders

def compose(funcs, **kwargs):
    return LabelledPipeline(list(reversed(funcs)), **kwargs)

def pipeline(funcs, **kwargs):
    return LabelledPipeline(funcs, **kwargs)

# Tools

def let(**kwargs):
    return LabelledFunction(lambda: tuple(kwargs.values()), name="setter", output_names=list(kwargs.keys()))

def relabel(old, new):
    def identity(**kwargs):
        return {new: kwargs[old]}
    lf = LabelledFunction(identity, name=f"relabel {old} as {new}", output_names=[new])
    lf.input_names = [old]
    return lf

def show(*names):
    def showing(**kwargs):
        showed = {name: kwargs[name] for name in names}
        print(showed)
        return showed
    lf = LabelledFunction(showing, name="showing " + " ".join(names), output_names=names)
    lf.input_names = names
    return lf


# INTERNALS

class LabelledPipeline(AbstractLabelledCallable):
    def __init__(self, funcs,
                 *, name=None, return_intermediate_outputs=False, default_values=None
                 ):
        self.funcs = [LabelledFunction(f) for f in funcs]

        if name is None:
            name = f"pipeline_of_{len(funcs)}_functions"
        self.name = name

        self.return_intermediate_outputs = return_intermediate_outputs

        self.input_names, self.output_names = self._identify_inputs_and_outputs()

        if default_values is None:
            default_values = {}
        self.default_values = default_values

    def _identify_inputs_and_outputs(self):
        all_inputs = [set(f.input_names) for f in self.funcs]
        all_outputs = [set(f.output_names) for f in self.funcs]

        pipe_inputs, intermediate = set(), set()
        for f_inputs, f_outputs in zip(all_inputs, all_outputs):

            # The inputs that are not already in the set of intermediate variables
            # are inputs of the whole pipeline
            pipe_inputs = pipe_inputs.union(f_inputs - intermediate)

            intermediate = intermediate.union(f_outputs)

        pipe_outputs = intermediate.copy()
        if not self.return_intermediate_outputs:
            for f_inputs in all_inputs:
                pipe_outputs = pipe_outputs - f_inputs

        return list(pipe_inputs), list(pipe_outputs)

    def __or__(self, other):
        if isinstance(other, LabelledFunction):
            return pipeline(
                [*self.funcs, other],
                name=self.name,
                return_intermediate_outputs=self.return_intermediate_outputs,
                default_values={**self.default_values, **other.default_values},
            )
        elif isinstance(other, LabelledPipeline):
            return pipeline(
                [*self.funcs, *other.funcs],
                name=f"{self.name} | {other.name}",
                return_intermediate_outputs=self.return_intermediate_outputs or other.return_intermediate_outputs,
                default_values={**self.default_values, **other.default_values},
            )
        else:
            return NotImplemented

    def __ror__(self, other):
        if isinstance(other, LabelledFunction):
            return pipeline(
                [other, *self.funcs],
                name=self.name,
                return_intermediate_outputs=self.return_intermediate_outputs,
                default_values={**self.default_values, **other.default_values},
            )
        elif isinstance(other, LabelledPipeline):
            return pipeline(
                [*other.funcs, *self.funcs],
                name=f"{self.name} | {other.name}",
                return_intermediate_outputs=self.return_intermediate_outputs or other.return_intermediate_outputs,
                default_values={**self.default_values, **other.default_values},
            )
        else:
            return NotImplemented

    def __call__(self, **namespace):
        if self.default_values is not None:
            namespace = {**self.default_values, **namespace}

        superfluous_inputs = set(namespace.keys()) - set(self.input_names)
        if len(superfluous_inputs) > 0:
            raise TypeError(f"Pipeline got unexpected argument(s): {superfluous_inputs}")

        for f in self.funcs:
            namespace = f.apply_in_namespace(namespace)

        return {name: val for name, val in namespace.items() if name in self.output_names}

    def _graph(self):
        Edge = namedtuple('Edge', ['start', 'label', 'end'])

        pipe_inputs: Set[str] = set()
        pipe_outputs: Set[str] = set()
        edges: Set[Edge] = set()
        last_modified = {}  # variable name => function that returned it last

        for f in self.funcs:
            for var_name in f.input_names:
                if var_name in last_modified:  # This variable is the output of a previous function.
                    pipe_outputs -= {var_name}  # If it was a global output, it is not anymore.
                    edges.add(Edge(last_modified[var_name], var_name, f.name))
                else:
                    pipe_inputs.add(var_name)  # The variable must be a global input.
                    edges.add(Edge(None, var_name, f.name))

            for var_name in f.output_names:
                last_modified[var_name] = f.name
                pipe_outputs.add(var_name)

        for var_name in pipe_outputs:
            edges.add(Edge(last_modified[var_name], var_name, None))

        # Fuse several uses of the same start and label (i.e. outputs of the
        # same function used in several other functions)
        dummy_nodes = set()
        for ((start, label), similar_edges) \
                in groupby(lambda e: (e.start, e.label), edges).items():
            if start is not None and len(similar_edges) > 1:
                new_node_label = f"{start}_{label}"
                dummy_nodes.add(new_node_label)
                edges.add(Edge(start, label, new_node_label))
                for e in similar_edges:
                    edges.add(Edge(new_node_label, label, e[2]))
                    edges.remove(e)

        funcs_nodes = set((f.name for f in self.funcs))
        return pipe_inputs, pipe_outputs, funcs_nodes, dummy_nodes, edges
