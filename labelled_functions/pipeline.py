#!/usr/bin/env python
# coding: utf-8

from typing import Set
from collections import namedtuple, defaultdict
from toolz.itertoolz import groupby
from toolz.dicttoolz import merge, keyfilter

from labelled_functions.abstract import AbstractLabelledCallable
from labelled_functions.labels import Unknown, label, LabelledFunction

# API

def pipeline(funcs, **kwargs):
    return LabelledPipeline(funcs, **kwargs)

def compose(funcs, **kwargs):
    return LabelledPipeline(list(reversed(funcs)), **kwargs)


# INTERNALS

class LabelledPipeline(AbstractLabelledCallable):
    def __init__(self,
                 funcs, *,
                 name=None, default_values=None,
                 return_intermediate_outputs=False
                 ):

        self.funcs = [label(f) for f in funcs]
        self.return_intermediate_outputs = return_intermediate_outputs

        if name is None:
            name = " | ".join([f.name for f in self.funcs])

        if any(f.output_names is Unknown for f in self.funcs):
            raise AttributeError("Cannot build a pipeline with a function whose outputs are unknown.")

        self._graph_data = self._graph()
        pipe_inputs, sub_default_values, pipe_outputs, *_ = self._graph_data

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

    def _which_input_is_used_by_this_function(self):
        _, _, _, _, _, edges = self._graph_data
        inputs_used_by = defaultdict(set)
        for e in edges:
            if e.start is None:
                inputs_used_by[e.end].add(e.label)
        return inputs_used_by

    def fix(self, **names_to_fix):
        inputs_used_by = self._which_input_is_used_by_this_function()

        fixed_funcs = []
        for f in self.funcs:
            fixable_names = {k: v for k, v in names_to_fix.items() if k in inputs_used_by[f.name]}
            if len(fixable_names) > 0:
                fixed_funcs.append(f.fix(**fixable_names))
            else:
                fixed_funcs.append(f)

        return LabelledPipeline(
            funcs=fixed_funcs,
            name=self.name,
            default_values={n: v for n, v in self.default_values.items() if n not in names_to_fix.keys()},
            return_intermediate_outputs=self.return_intermediate_outputs,
        )

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
