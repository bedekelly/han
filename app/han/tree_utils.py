def value_at(tree, path="$"):
    "Read the state at the given JSON path."

    def maybe_int(i):
        try:
            return int(i)
        except ValueError:
            return i

    components = path.split(".")
    path_components = (maybe_int(comp) for comp in components)
    data = tree

    for component in path_components:
        if component in ("$", ""):
            continue
        data = data[component]

    return data
