

from labelled_functions.labels import LabelledFunction


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

