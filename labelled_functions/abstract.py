#!/usr/bin/env python
# coding: utf-8

from typing import Callable, Set, List, Dict, Union, Any
from copy import copy
from abc import ABC, abstractmethod

import xarray as xr

Unknown = object()

class AbstractLabelledCallable(ABC):
    """Common code between all labelled function classes."""

    def __init__(self,
                 function: Callable,
                 name: str,
                 input_names: List[str],
                 output_names: List[str],
                 default_values: Dict[str, Any],
                 ):

        self.function = function
        self.name = name
        self.__name__ = name
        self.input_names = input_names
        self.output_names = output_names

        self.default_values = default_values
        assert set(self.default_values.keys()) <= set(self.input_names)

        self._has_never_been_run = True

    # SETTING ATTRIBUTES
    def rename(self, name):
        f = copy(self)
        f.name = name
        return f

    def set_default(self, **names_and_values):
        f = copy(self)
        f.default_values = {**self.default_values, **names_and_values}
        return f

    def reset_default(self, *names):
        f = copy(self)
        for name in names:
            del f.default_values[name]
        return f

    @abstractmethod
    def fix(self, **names_and_values):
        pass

    def hide(self, *hidden_names):
        unhiddable_names = set(hidden_names) - set(self.default_values.keys())
        if len(unhiddable_names) > 0:
            raise AttributeError(f"Trying to hide an input with no default value: {unhiddable_names}")
        return self.fix(**{n: v for n, v in self.default_values.items() if n in hidden_names})

    def hide_all_but(self, *not_hidden_names):
        return self.hide(*set(self.input_names) - set(not_hidden_names))


    # CALLS

    def _preprocess_inputs(self, args, kwargs):
        passed_as_positional = self.input_names[:len(args)]

        # Remove from the default values the parameters that have been passed
        # as positional arguments.
        actual_default_values = {name: value for name, value in self.default_values.items()
                                 if name not in passed_as_positional}

        kwargs = {**actual_default_values, **kwargs}

        passed = set(passed_as_positional) | set(kwargs.keys())
        required = set(self.input_names)

        missing_inputs = required - passed
        if len(missing_inputs) > 0:
            raise TypeError(f"{self.__class__.__name__} {self.name} is missing argument(s): {missing_inputs}")

        superfluous_inputs = passed - required
        if len(superfluous_inputs) > 0:
            raise TypeError(f"{self.__class__.__name__} {self.name} got unexpected argument(s): {superfluous_inputs}")

        return args, kwargs

    def _guess_output_names_from(self, result):
        if result is None:
            return []
        elif isinstance(result, (list, tuple)) and len(result) > 1:
            return [f"{self.name}[{i}]" for i in range(len(result))]
        elif isinstance(result, dict):
            return list(result.keys())
        # TODO: Handle named tuples
        else:
            return [self.name]

    def _output_as_dict(self, result) -> Dict[str, Any]:
        if result is None:
            return {}
        elif isinstance(result, dict):
            return result
        elif len(self.output_names) == 1 and not isinstance(result, tuple):
            return {self.output_names[0]: result}
        else:
            return {name: val for name, val in zip(self.output_names, result)}

    def _postprocess_outputs(self, result):
        if self._has_never_been_run:
            self._has_never_been_run = False
            if self.output_names is Unknown:
                self.output_names = self._guess_output_names_from(result)
            if set(self._output_as_dict(result).keys()) != set(self.output_names):
                raise TypeError(f"Inconsistent output in {self.name}!")
        return result

    def __call__(self, *args, **kwargs):
        args, kwargs = self._preprocess_inputs(args, kwargs)
        result = self.function(*args, **kwargs)
        return self._postprocess_outputs(result)

    def apply_in_namespace(self, namespace: Union[Dict[str, Any], xr.Dataset]) -> Union[Dict[str, Any], xr.Dataset]:
        """Call the functions using the relevant variables in the namespace as
        inputs and adding the outputs to the namespace (in-place).

        Examples
        --------
        >>> LabelledFunction(round).apply_in_namespace({'number': 4.2, 'other': 'a'})
        {'number': 4.2, 'other': 'a', 'round': 4}
        """
        if isinstance(namespace, xr.Dataset):
            keys = set(namespace.coords) | set(namespace.data_vars)
        else:
            keys = namespace.keys()
        inputs = {name: namespace[name] for name in keys if name in self.input_names}
        outputs = self._output_as_dict(self.__call__(**inputs))
        namespace.update(outputs)
        return namespace

    # GRAPH

    color_scheme = {
        'blue':   {'light': '#88BBBB', 'main': '#226666', 'dark': '#003333'},
        'red':    {'light': '#FFAAAA', 'main': '#113939', 'dark': '#550000'},
        'yellow': {'light': '#FFE3AA', 'main': '#AA8439', 'dark': '#553900'},
        'gray':   {'light': '#EEEEEE', 'main': '#777777', 'dark': '#222222'},
    }
    graph_function_style = {
        'shape': 'oval', 'style': 'filled',
        'color': color_scheme['blue']['main'],
        'fontcolor': color_scheme['blue']['dark'],
        'fillcolor': color_scheme['blue']['light'],
    }
    graph_input_style = {
        'shape': 'box', 'style': 'filled',
        'color': color_scheme['red']['main'],
        'fontcolor': color_scheme['red']['dark'],
        'fillcolor': color_scheme['red']['light'],
    }
    graph_optional_input_style = {
        'shape': 'box', 'style': 'filled',
        'color': color_scheme['gray']['main'],
        'fontcolor': color_scheme['gray']['dark'],
        'fillcolor': color_scheme['gray']['light'],
    }
    graph_output_style = {
        'shape': 'box', 'style': 'filled',
        'color': color_scheme['yellow']['main'],
        'fontcolor': color_scheme['yellow']['dark'],
        'fillcolor': color_scheme['yellow']['light'],
    }

    @abstractmethod
    def _graph(self, **kwargs):
        pass

    def graph(self, backend='graphviz', rankdir='TB'):
        inputs_nodes, default_values, output_nodes, function_nodes, dummy_nodes, edges = self._graph()

        if backend == 'graphviz':
            from graphviz import Digraph
            G = Digraph(strict=False)
            G.attr(rankdir=rankdir)
            add_node = G.node
            add_edge = G.edge
        elif backend == 'pygraphviz':
            from pygraphviz import AGraph
            G = AGraph(rankdir=rankdir, directed=True, strict=False)
            add_node = G.add_node
            add_edge = G.add_edge

        def format_node_label(name, value):
            if value is None:
                return f"{name}=None"
            elif isinstance(value, (int, float, bool)):
                return f"{name}={str(value)}"
            elif isinstance(value, str) and len(value) < 10:
                return f"{name}=\"{str(value)}\""
            else:
                return f"{name}=..."

        for f_name in function_nodes:
            add_node(f_name, **self.graph_function_style)
        for var_name in inputs_nodes:
            if var_name in self.default_values.keys():
                add_node("input__" + var_name,
                       label=format_node_label(var_name, self.default_values[var_name]),
                       **self.graph_optional_input_style,
                )
            else:
                add_node("input__" + var_name, label=var_name, **self.graph_input_style)
        for var_name in output_nodes:
            add_node("output__" + var_name, label=var_name, **self.graph_output_style)
        for dn in dummy_nodes:
            add_node(dn, shape='point')

        for e in edges:
            if e.start is None and e.label in inputs_nodes:
                add_edge("input__" + e.label, e.end)
            elif e.end is None and e.label in output_nodes:
                add_edge(e.start, "output__" + e.label)
            elif e.start in dummy_nodes:
                add_edge(e.start, e.end)
            elif e.end in dummy_nodes:
                add_edge(e.start, e.end, label=e.label, arrowhead='none')
            else:
                add_edge(e.start, e.end, label=e.label)

        return G

    def save_graph(self, filepath=None):
        from pathlib import Path
        if filepath is None:
            filepath = Path.cwd() / (self.name + ".pdf")
        self.graph(backend='pygraphviz', rankdir='TB').draw(str(filepath), prog='dot')

    def show_graph(self):
        import IPython.display as display
        return display.SVG(data=self.graph().pipe(format="svg"))

