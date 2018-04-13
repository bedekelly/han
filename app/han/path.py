import re
from collections import deque
from functools import lru_cache

# Extract the components from a simple object-path syntax.
# e.g. "$.a.b[2]" => ['a', 'b', 2]
path_components = re.compile("(?:\.(\w+))|(?:\[(\w+)\])")


def get_components(path):
    "Retrieve the attribute accesses for a request."
    component_pairs = path_components.findall(path)
    for (dot, array) in component_pairs:
        if array:
            yield int(array)
        else:
            yield dot


@lru_cache(256)
def mutual_contains(path1, path2):
    "Test if one path is a subpath of the other."
    components_one = get_components(path1)
    components_two = get_components(path2)

    for (component1, component2) in zip(components_one, components_two):
        if component1 != component2:
            return False
    return True
