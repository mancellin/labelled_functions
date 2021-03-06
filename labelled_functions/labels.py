#!/usr/bin/env python
# coding: utf-8

from typing import List
from copy import copy
from inspect import Parameter, Signature, getsource
from collections import namedtuple
from functools import update_wrapper, partial

import parso

from labelled_functions.abstract import Unknown, AbstractLabelledCallable


# API

def label(f=None, *,
          name=None, output_names=Unknown,
          default_values=None,
          ):

    if f is None:  # For usage as a decorator.
        def label_decorator(f):
            return label(f,
                         name=name, output_names=output_names,
                         default_values=default_values,
                         )
        return label_decorator

    elif isinstance(f, AbstractLabelledCallable):
        # Edit the labelled object instead of return a new one
        if name is not None:
            f.name = name
        if output_names is not Unknown:
            f.output_names = output_names
        if default_values is not None:
            f.default_values = default_values
        return f

    else:
        return LabelledFunction(f,
                                name=name, output_names=output_names,
                                default_values=default_values,
                                )


# INTERNALS

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

    def __init__(self,
                 function,
                 name=None,
                 input_names=None,
                 output_names=Unknown,
                 default_values=None,
                 ):

        if name is None:
            try:
                name = function.__name__
            except AttributeError:
                name = "unnamed_function"

        if input_names is None or default_values is None or output_names is None:
            _signature = Signature.from_callable(function)

        # INPUT
        if input_names is None:
            input_names = [name for name in _signature.parameters]

        if default_values is None:
            p = _signature.parameters
            default_values = {name: p[name].default for name in p
                              if p[name].default is not Parameter.empty}

        # OUTPUT
        if output_names is Unknown and function.__name__ != "<lambda>":
            # try:
            source = getsource(function)
            output_names = _get_output_names_from_source(source)
            # except (ValueError, TypeError):
            #     pass

        update_wrapper(self, function)
        super().__init__(
            function,
            name=name,
            input_names=input_names,
            output_names=output_names,
            default_values=default_values,
        )

    def __copy__(self):
        copied = LabelledFunction(
            self.function,
            name=self.name,
            input_names=copy(self.input_names),
            output_names=copy(self.output_names),
            default_values=copy(self.default_values),
        )
        return copied

    def __or__(self, other):
        if isinstance(other, LabelledFunction):
            from labelled_functions.pipeline import pipeline
            return pipeline([self, other])
        else:
            return NotImplemented

    def __ror__(self, other):
        if isinstance(other, LabelledFunction):
            from labelled_functions.pipeline import pipeline
            return pipeline([other, self])
        else:
            return NotImplemented

    def __repr__(self):
        input_str = ", ".join(self.input_names) if len(self.input_names) > 0 else ""
        output_str = ", ".join(self.output_names) if len(self.output_names) > 0 else ""
        return f"{self.name}({input_str}) -> ({output_str})"

    def fix(self, **names_to_fix):
        return LabelledFunction(
            function=partial(self.function, **names_to_fix),
            name=self.name,
            input_names=[n for n in self.input_names if n not in names_to_fix.keys()],
            output_names=self.output_names,
            default_values={n: v for n, v in self.default_values.items() if n not in names_to_fix.keys()}
        )

    def _graph(self):
        Edge = namedtuple('Edge', ['start', 'label', 'end'])

        edges = set([Edge(None, ivar, self.name) for ivar in self.input_names])
        edges |= set([Edge(self.name, ovar, None) for ovar in self.output_names])
        return set(self.input_names), self.default_values, set(self.output_names), set([self.name]), set(), edges


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
                         "but it is not a simple expression or a tuple:\n"
                         f"{return_stmt.children[-1]}")

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
    elif tree.type in {"testlist", "testlist_star_expr"}:
        return [o.get_code() for o in tree.children if not o.type == "operator"]
    elif tree.type == "atom" and "(" in tree.children[0].get_code():
        return _parse_returned_expression(tree.children[1])

