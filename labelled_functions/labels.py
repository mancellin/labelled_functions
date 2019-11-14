#!/usr/bin/env python
# coding: utf-8

from typing import List
from inspect import Parameter, Signature, getsource
from functools import update_wrapper

import parso

from .abstract import AbstractLabelledCallable


# API

def label(f=None, **kwargs):
    if f is None:  # For use as a decorator.
        def label_to_be_applied(f):
            return LabelledFunction(f, **kwargs)
        return label_to_be_applied
    else:
        return LabelledFunction(f, **kwargs)


# INTERNALS

Unknown = None


class LabelledFunction(AbstractLabelledCallable):
    """A class wrapping a function and storing names for its inputs and outputs.

    Parameters
    ----------
    f: Function
        A Python function.

    Attributes
    ----------
    name: str
        The name of the function.
    input_names: List[str]
        The names of the inputs.
    output_names: List[str]
        The names of the outputs.
    default_values: Dict[str, Any]
        The default values of the optional inputs.

    Function are assumed to always return the same type of output, in
    particular, the same number of output variables.

    Positional-only arguments are not supported (since their name is irrelevant,
    they are not suited for labelled functions).
    
    The constructor `LabelledFunction` is idempotent:
    >>> lf = LabelledFunction(f)
    >>> llf = LabelledFunction(lf)
    >>> lf is llf
    True

    """

    def __new__(cls, f, **kwargs):
        if isinstance(f, AbstractLabelledCallable):
            return f  # No need to create a new object, the function has already been labelled.
        else:
            return super().__new__(cls)

    def __init__(self, f, *, name=None, output_names=Unknown):
        if isinstance(f, AbstractLabelledCallable):
            pass  # Do not rerun __init__ when idempotent call.
        else:
            self.function = f
            update_wrapper(self, f)

            if name is None:
                try:
                    name = f.__name__
                except AttributeError:
                    pass
            self.name = name

            self._signature = Signature.from_callable(f)

            # INPUT
            self.input_names = [name for name in self._signature.parameters]

            self.default_values = {name: self._signature.parameters[name].default for name in self._signature.parameters if self._signature.parameters[name].default is not Parameter.empty}

            # OUTPUT
            self._has_never_been_run = True

            if output_names is Unknown:
                if self._signature.return_annotation is not Signature.empty:
                    if isinstance(self._signature.return_annotation, (tuple, list)):
                        output_names = list(self._signature.return_annotation)
                    else:
                        output_names = [self._signature.return_annotation]

                else:
                    try:
                        source = getsource(self.function)
                        output_names = _get_output_names_from_source(source)
                    except (ValueError, TypeError):
                        pass
            self.output_names = output_names

    def __str__(self):
        input_str = ", ".join(self.input_names) if len(self.input_names) > 0 else ""
        output_str = ", ".join(self.output_names) if len(self.output_names) > 0 else ""
        return f"{self.name}({input_str}) -> ({output_str})"

    def __call__(self, *args, **kwargs):
        result = self.function.__call__(*args, **kwargs)

        if self._has_never_been_run:
            self._has_never_been_run = False
            if self.output_names is Unknown:
                self.output_names = self._guess_output_names_from(result)
            else:
                self._check_output_consistency(result)
        return result

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

    def graph(self):
        from pygraphviz import AGraph
        graph = AGraph(rankdir='LR', directed=True, strict=False)
        graph.add_node(self.name, **self.graph_function_style)
        for input_name in self.input_names:
            graph.add_node(input_name, **self.graph_output_style)
            graph.add_edge(input_name, self.name)
        for output_name in self.output_names:
            graph.add_node(output_name, **self.graph_output_style)
            graph.add_edge(self.name, output_name)
        return graph



# HELPER FUNCTIONS

def _get_output_names_from_source(source: str) -> List[str]:
    content = parso.parse(source)
    return_stmt = _find_return_in_tree(content)
    if return_stmt is None:
        return []  # The function has no return statement.
    names = _parse_returned_expression(return_stmt.children[-1])
    if names is not None:
        # Strip space and newlines (when using \ at the end of the line)
        return [n.strip(' \\\n') for n in names]
    else:
        raise ValueError("A return statement has been found, "
                         "but it is not a simple expression or a typle")

def _find_return_in_tree(tree):
    # Recursively go through the syntax tree to find a return statement.
    if tree.type == "return_stmt":
        # Found!
        return tree
    elif hasattr(tree, 'children'):
        # Go through the children, starting with the end.
        for s in reversed(tree.children):
            found = _find_return_in_tree(s)
            if found is not None:
                return found

def _parse_returned_expression(tree):
    # Look for a single expression, or a tuple of expressions.
    if tree.type in {"name", "term", "arith_expr", "atom_expr"}:
        return [tree.get_code()]
    elif tree.type == "testlist":
        return [o.get_code() for o in tree.children if not o.type == "operator"]
    elif tree.type == "atom" and "(" in tree.children[0].get_code():
        return _parse_returned_expression(tree.children[1])

