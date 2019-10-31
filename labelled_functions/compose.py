from labelled_functions.labels import Unknown, LabelledFunction
from toolz.itertoolz import groupby


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
                print(str(f))
            namespace = f.apply_in_namespace(namespace)

        return {name: val for name, val in namespace.items() if name in pipe_outputs}

    pipe.input_names = list(pipe_inputs)
    pipe.output_names = list(pipe_outputs)
    return pipe


def compose(funcs, **kwargs):
    return pipeline(reversed(funcs, **kwargs))


function_style = {'style': 'filled', 'shape': 'oval'}
input_style = {'shape': 'box'}
output_style = {'shape': 'box'}

def graph(funcs):
    funcs = [LabelledFunction(f) for f in funcs]

    from pygraphviz import AGraph
    G = AGraph(rankdir='LR', directed=True, strict=False)

    pipe_inputs = set()
    last_modified = {}  # variable name => function that returned it last
    pipe_outputs = set()
    for f in funcs:
        G.add_node(f.name, **function_style)
        for var_name in f.input_names:
            pipe_outputs -= {var_name}
            if var_name not in last_modified:
                if var_name not in pipe_inputs:
                    pipe_inputs.add(var_name)
                    G.add_node(var_name, **input_style)
                G.add_edge(var_name, f.name)
            else:
                G.add_edge(last_modified[var_name], f.name, label=var_name)
        for var_name in f.output_names:
            last_modified[var_name] = f.name
            if var_name not in pipe_inputs:
                pipe_outputs.add(var_name)

    for var_names in pipe_outputs:
        G.add_node(var_name, **output_style)
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

