from typing import List, Dict, Union, Any
from copy import copy
from abc import ABC, abstractmethod

import xarray as xr

class AbstractLabelledCallable:
    """Common code between all labelled function classes."""

    # The attributes below should be defined in each instances of inheriting classes.
    input_names: List[str]
    output_names: List[str]
    default_values: Dict[str, Any]  # with keys in input_names

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass

    def _check_output_consistency(self, result):
        if result is None:
            assert len(self.output_names) == 0
        elif isinstance(result, (list, tuple)) and len(result) > 1:
            assert len(result) == len(self.output_names)
        elif isinstance(result, dict):
            assert set(result.keys()) == set(self.output_names)
        # TODO: Handle named tuples
        else:
            assert len(self.output_names) == 1

    def _output_as_dict(self, result) -> Dict[str, Any]:
        if result is None:
            return {}
        elif isinstance(result, dict):
            return result
        elif len(self.output_names) == 1:
            if isinstance(result, (tuple, list)):
                return {self.output_names[0]: result[0]}
            else:
                return {self.output_names[0]: result}
        else:
            return {name: val for name, val in zip(self.output_names, result)}

    def set_default(self, **kwargs):
        f = copy(self)
        f.default_values = {**self.default_values, **kwargs}
        return f

    def recorded_call(self, *args, **kwargs) -> Dict[str, Any]:
        """Call the function and return a dict with its inputs and outputs.

        Examples
        --------
        >>> LabelledFunction(round).recorded_call(1.6)
        {'number': 1.6, 'round': 2}

        >>> LabelledFunction(pow).recorded_call(2, 3)
        {'x': 2, 'y': 3, 'pow': 8}

        >>> def cube(x):
                return (12*x, 6*x**2, x**3)
        >>> LabelledFunction(cube).recorded_call(5)
        {'x': 5, 'cube[0]': 60, 'cube[1]': 150, 'cube[2]': 125}

        >>> def cube(x) -> ('length', 'area', 'volume'):
                return (12*x, 6*x**2, x**3)
        >>> LabelledFunction(cube).recorded_call(5)
        {'x': 5, 'length': 60, 'area': 150, 'volume': 125}
        """
        inputs = {**self.default_values, **{name: val for name, val in zip(self.input_names, args)}, **kwargs}
        outputs = self._output_as_dict(self.__call__(*args, **kwargs))
        return {**inputs, **outputs}

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
        'color': color_scheme['yellow']['main'],
        'fontcolor': color_scheme['yellow']['dark'],
        'fillcolor': color_scheme['yellow']['light'],
    }
    graph_optional_input_style = {
        'shape': 'box', 'style': 'filled',
        'color': color_scheme['gray']['main'],
        'fontcolor': color_scheme['gray']['dark'],
        'fillcolor': color_scheme['gray']['light'],
    }
    graph_output_style = {
        'shape': 'box', 'style': 'filled',
        'color': color_scheme['red']['main'],
        'fontcolor': color_scheme['red']['dark'],
        'fillcolor': color_scheme['red']['light'],
    }

    @abstractmethod
    def _graph(self, **kwargs):
        pass

    def graphviz(self):
        inputs_nodes, output_nodes, function_nodes, dummy_nodes, edges = self._graph()

        from graphviz import Digraph
        G = Digraph(strict=False)
        G.attr(rankdir='LR')

        for f_name in function_nodes:
            G.node(f_name, **self.graph_function_style)
        for var_name in inputs_nodes:
            if var_name in self.default_values.keys():
                G.node(var_name, **self.graph_optional_input_style)
            else:
                G.node(var_name, **self.graph_input_style)
        for var_name in output_nodes:
            G.node(var_name, **self.graph_output_style)
        for dn in dummy_nodes:
            G.node(dn, shape='point')

        for e in edges:
            if e.start is None and e.label in inputs_nodes:
                G.edge(e.label, e.end)
            elif e.end is None and e.label in output_nodes:
                G.edge(e.start, e.label)
            elif e.start in dummy_nodes:
                G.edge(e.start, e.end)
            else:
                G.edge(e.start, e.end, label=e.label)

        return G

    def pygraphviz(self):
        inputs_nodes, output_nodes, function_nodes, dummy_nodes, edges = self._graph()

        from pygraphviz import AGraph
        G = AGraph(rankdir='LR', directed=True, strict=False)

        for f_name in function_nodes:
            G.add_node(f_name, **self.graph_function_style)
        for var_name in inputs_nodes:
            if var_name in self.default_values:
                G.add_node(var_name, **self.graph_optional_input_style)
            else:
                G.add_node(var_name, **self.graph_input_style)
        for var_name in output_nodes:
            G.add_node(var_name, **self.graph_output_style)
        for dn in dummy_nodes:
            G.add_node(dn, shape='point')

        for e in edges:
            if e.start is None and e.label in inputs_nodes:
                G.add_edge(e.label, e.end)
            elif e.end is None and e.label in output_nodes:
                G.add_edge(e.start, e.label)
            elif e.start in dummy_nodes:
                G.add_edge(e.start, e.end)
            else:
                G.add_edge(e.start, e.end, label=e.label)

        return G
