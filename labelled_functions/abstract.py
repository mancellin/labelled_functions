from typing import Dict, Union
from abc import ABC, abstractmethod

import xarray as xr

class AbstractLabelledCallable:
    """Common code between all labelled function classes."""

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

    def _output_as_dict(self, result):
        if result is None:
            return {}
        elif isinstance(result, dict):
            return result
        elif len(self.output_names) == 1:
            return {self.output_names[0]: result}
        else:
            return {name: val for name, val in zip(self.output_names, result)}

    def recorded_call(self, *args, **kwargs):
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

    def apply_in_namespace(self, namespace: Union[Dict, xr.Dataset]) -> Union[Dict, xr.Dataset]:
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

    graph_function_style = {'style': 'filled', 'shape': 'oval'}
    graph_input_style = {'shape': 'box'}
    graph_output_style = {'shape': 'box'}

    @abstractmethod
    def graph(self, **kwargs):
        pass

