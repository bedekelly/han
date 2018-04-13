import re
import copy
from collections import deque
from .path import get_components


def value_at(tree, path="$"):
    "Read the state at the given JSON path."
    components = get_components(path)
    data = tree
    for component in components:
        data = data[component]
    return data


def _mutable_set_value_at(mutable_tree, path, new_data):
    "Set the value of `mutable_tree` at `path` to `new_data`."
    container = mutable_tree
    next_components = deque(get_components(path))

    # Early-exit if we can just replace the whole thing!
    if len(next_components) == 0:
        return new_data

    # Descend to the nearest containing object.
    while len(next_components) > 1:
        next_component = next_components.popleft()
        container = container[next_component]

    # Add the new value to the containing object.
    final_component = next_components.popleft()
    assert len(next_components) == 0
    container[final_component] = new_data

    # We've been mutating the original tree, so no return needed!
    return None


def set_value_at(tree, path, new_data):
    """
    Return a copy of 'tree' with the value at 'path' replaced by 'new_data'.
    """
    print(tree)
    new_tree = copy.deepcopy(tree)
    _mutable_set_value_at(new_tree, path, new_data)
    return new_tree
