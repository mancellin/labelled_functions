
from .labels import Unknown, LabelledFunction


def pipeline(funcs, *, keep_intermediate_outputs=False, debug=False, default_values=None):
    funcs = [LabelledFunction(f) for f in funcs]

    for f in funcs:
        if f.output_names is Unknown:
            f.output_names = [f.name]

    all_inputs = [set(f.input_names) for f in funcs]
    all_outputs = [set(f.output_names) for f in funcs]

    pipe_inputs, intermediate = set(), set()
    for f_inputs, f_outputs in zip(all_inputs, all_outputs):

        # The inputs that are not already in the set of intermediate variables
        # are inputs of the whole pipeline
        pipe_inputs = pipe_inputs.union(f_inputs - intermediate)

        intermediate = intermediate.union(f_outputs)

    pipe_outputs = intermediate.copy()
    if not keep_intermediate_outputs:
        for f_inputs in all_inputs:
            pipe_outputs = pipe_outputs - f_inputs

    @LabelledFunction
    def pipe(**namespace):
        if default_values is not None:
            namespace = {**default_values, **namespace}

        superfluous_inputs = set(namespace.keys()) - pipe_inputs
        if len(superfluous_inputs) > 0:
            raise TypeError(f"Pipeline got unexpected argument(s): {superfluous_inputs}")

        for f in funcs:
            if debug:
                print(namespace.keys())
            namespace = f.apply_in_namespace(namespace)

        return {name: val for name, val in namespace.items() if name in pipe_outputs}

    pipe.input_names = list(pipe_inputs)
    pipe.output_names = list(pipe_outputs)
    return pipe


def compose(funcs, **kwargs):
    return pipeline(reversed(funcs, **kwargs))

