#!/usr/bin/env python
# coding: utf-8

from typing import Set
from collections import namedtuple
from toolz.itertoolz import groupby
from toolz.dicttoolz import merge, keyfilter

from labelled_functions.abstract import AbstractLabelledCallable
from labelled_functions.labels import Unknown, label, LabelledFunction

# API
# Builders

def compose(funcs, **kwargs):
    return LabelledPipeline(list(reversed(funcs)), **kwargs)

def pipeline(funcs, **kwargs):
    return LabelledPipeline(funcs, **kwargs)

# Tools

def let(**kwargs):
    name = "let " + ", ".join((f"{name}={value}" for name, value in kwargs.items()))
    return LabelledFunction(lambda: tuple(kwargs.values()), name=name, input_names=[], output_names=list(kwargs.keys()))

def relabel(old, new):
    def identity(**kwargs):
        return {new: kwargs[old]}
    lf = LabelledFunction(identity, name=f"relabel {old} as {new}", input_names=[old], output_names=[new])
    return lf

def show(*names):
    def showing(**kwargs):
        showed = {name: kwargs[name] for name in names}
        print(showed)
        return showed
    lf = LabelledFunction(showing, name="showing " + " ".join(names), input_names=names, output_names=names)
    return lf


# INTERNALS

class LabelledPipeline(AbstractLabelledCallable):
    def __init__(self,
                 funcs, *,
                 name=None, default_values=None, hidden_inputs=None,
                 return_intermediate_outputs=False
                 ):

        self.funcs = [label(f) for f in funcs]
        self.return_intermediate_outputs = return_intermediate_outputs

        if name is None:
            name = " | ".join([f.name for f in self.funcs])

        if any(f.output_names is Unknown for f in self.funcs):
            raise AttributeError("Cannot build a pipeline with a function whose outputs are unknown.")

        pipe_inputs, sub_default_values, pipe_outputs, *_ = self._graph()

        if hidden_inputs is None:
            hidden_inputs = set()

        if default_values is None:
            sub_default_values = sub_default_values
        else:
            sub_default_values = {**sub_default_values, **default_values}

        def function(**namespace):
            for f in self.funcs:
                namespace = f.apply_in_namespace(namespace)
            result = {name: val for name, val in namespace.items() if name in self.output_names}
            return result

        super().__init__(
            function=function,
            name=name,
            input_names=list(pipe_inputs),
            output_names=list(pipe_outputs),
            default_values=sub_default_values,
            hidden_inputs=hidden_inputs,
        )

    def __or__(self, other):
        if isinstance(other, LabelledFunction):
            return pipeline(
                [*self.funcs, other],
                name=self.name,
                return_intermediate_outputs=self.return_intermediate_outputs,
                default_values=_merge_default_values(self, other),
            )
        elif isinstance(other, LabelledPipeline):
            return pipeline(
                [*self.funcs, *other.funcs],
                name=f"{self.name} | {other.name}",
                return_intermediate_outputs=self.return_intermediate_outputs or other.return_intermediate_outputs,
                default_values=_merge_default_values(self, other),
            )
        else:
            return NotImplemented

    def __ror__(self, other):
        if isinstance(other, LabelledFunction):
            return pipeline(
                [other, *self.funcs],
                name=self.name,
                return_intermediate_outputs=self.return_intermediate_outputs,
                default_values=_merge_default_values(other, self),
            )
        elif isinstance(other, LabelledPipeline):
            return pipeline(
                [*other.funcs, *self.funcs],
                name=f"{self.name} | {other.name}",
                return_intermediate_outputs=self.return_intermediate_outputs or other.return_intermediate_outputs,
                default_values=_merge_default_values(other, self),
            )
        else:
            return NotImplemented

    def _graph(self):
        Edge = namedtuple('Edge', ['start', 'label', 'end'])

        pipe_inputs: Set[str] = set()
        pipe_outputs: Set[str] = set()
        edges: Set[Edge] = set()
        last_modified = {}  # variable name => function that returned it last
        default_values = {}

        for f in self.funcs:
            for var_name in f.input_names:
                if var_name in last_modified:  # This variable is the output of a previous function.
                    if not self.return_intermediate_outputs:
                        pipe_outputs -= {var_name}  # If it was a global output, it is not anymore.
                    edges.add(Edge(last_modified[var_name], var_name, f.name))
                else:
                    pipe_inputs.add(var_name)  # The variable must be a global input.
                    if var_name in f.default_values:
                        default_values[var_name] = f.default_values[var_name]
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
        return (pipe_inputs, default_values, pipe_outputs,
                funcs_nodes, dummy_nodes, edges)

def _merge_default_values(first, second):
    return {
        **first.default_values,
        **{name: value for name, value in second.default_values.items() if name not in first.output_names},
    }
