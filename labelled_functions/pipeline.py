#!/usr/bin/env python
# coding: utf-8

from labelled_functions.abstract import AbstractLabelledCallable
from labelled_functions.labels import Unknown, LabelledFunction
from toolz.itertoolz import groupby
from toolz.dicttoolz import merge

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

    def graph(self):
        from pygraphviz import AGraph
        G = AGraph(rankdir='LR', directed=True, strict=False)

        pipe_inputs = set()
        last_modified = {}  # variable name => function that returned it last
        pipe_outputs = set()
        for f in self.funcs:
            G.add_node(f.name, **graph_function_style)
            for var_name in f.input_names:
                pipe_outputs -= {var_name}
                if var_name not in last_modified:
                    if var_name not in pipe_inputs:
                        pipe_inputs.add(var_name)
                        G.add_node(var_name, **graph_input_style)
                    G.add_edge(var_name, f.name)
                else:
                    G.add_edge(last_modified[var_name], f.name, label=var_name)
            for var_name in f.output_names:
                last_modified[var_name] = f.name
                if var_name not in pipe_inputs:
                    pipe_outputs.add(var_name)

        for var_names in pipe_outputs:
            G.add_node(var_name, **graph_output_style)
            G.add_edge(last_modified[var_name], var_name)

        # Fuse several uses of the same function output
        for begin, edges in groupby(lambda e: e[0], G.edges()).items():
            if begin in [f.name for f in funcs]:
                for label, edges_with_label in groupby(lambda e: e.attr['label'], edges).items():
                    if len(edges_with_label) > 1:
                        G.delete_edges_from(edges_with_label)
                        node_name = begin + '_' + label
                        G.add_node(node_name, shape='point')
                        G.add_edge(begin, node_name, arrowhead='none', label=label)
                        for edge in edges_with_label:
                            G.add_edge(node_name, edge[1])

        G.draw('/home/ancellin/test.png', prog='dot')
        return G

