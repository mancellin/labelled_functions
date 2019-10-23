
from .labels import Unknown, LabelledFunction

def compose(funcs):
    return pipeline(reversed(funcs))

def pipeline(funcs, keep_all_internals=False):
    funcs = [LabelledFunction(f) for f in funcs]

    for f in funcs:
        if f.output_names is Unknown:
            f.output_names = [f.name]

    all_inputs = [set(f.input_names) for f in funcs]
    all_outputs = [set(f.output_names) for f in funcs]

    pipe_inputs, available = set(), set()
    for f_inputs, f_outputs in zip(all_inputs, all_outputs):
        pipe_inputs = pipe_inputs.union(f_inputs - available)
        available = available.union(f_outputs)

    pipe_outputs = available.copy()
    if not keep_all_internals:
        for f_inputs in all_inputs:
            pipe_outputs = pipe_outputs - f_inputs

    @LabelledFunction
    def pipe(**namespace):
        for f in funcs:
            namespace = f.apply_in_namespace(namespace)
        return {name: val for name, val in namespace.items() if name in pipe_outputs}

    pipe.input_names = list(pipe_inputs)
    pipe.output_names = list(pipe_outputs)
    return pipe
