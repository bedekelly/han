from .tree import *
from .path import *


def test_value_at():
    assert value_at({"a": 123}, "$.a") == 123
    assert value_at({"a": {"b": 123}}, "$.a.b") == 123
    assert value_at({"a": {"b": 123, "c": 432}}, "$.a.c") == 432

    assert value_at({
        "a": [1, 2, 3]
    }, "$.a[0]") == 1

    assert value_at({
        "a": [1, 2, 3]
    }, "$.a[1]") == 2

    assert value_at({
        "a": {"b": [1, 2, 3]}
    }, "$.a.b[1]") == 2


    assert value_at({
        "state": [
            {
                "a": 123
            },
            {
                "a": 456
            },
            {
                "a": {
                    "b": 789
                }
            }
        ]
    }, "$.state[2].a") == {"b": 789}


def test_get_components():
    assert list(get_components("$.a.b.c[1][2].d[3]")) == [
        'a', 'b', 'c', 1, 2, 'd', 3
    ]

def test_components_root():
    assert list(get_components("$")) == []


def test_set_value_at():
    tree = {
        "a": [1, 2, 3],
        "b": [4, 5, {"number": {
            "names": ["six", "Sixx"]
        }}]
    }

    new_tree = set_value_at(tree, "$.b[2].number.names[1]", "Six")
    assert new_tree == {
        "a": [1, 2, 3],
        "b": [4, 5, {"number": {
            "names": ["six", "Six"]
        }}]
    }

    assert tree == {
        "a": [1, 2, 3],
        "b": [4, 5, {"number": {
            "names": ["six", "Sixx"]
        }}]
    }


def test_mutual_contains():
    assert mutual_contains("$.a.b.c", "$.a.b")
    assert mutual_contains("$.a.b.c", "$.a.b.c.d")
    assert mutual_contains("$.a.b", "$.a.b")
    assert not mutual_contains("$.a.b.c", "$.a.b.d")
    assert not mutual_contains("$.number", "$.posts")
