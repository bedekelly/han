from flask import request
from . import app, han
from .actions import increment, decrement, new_post, count_posts


@han.dle(increment)
def increment(state):
    "Manually increment the state's number."
    return {
        "number": state["number"] + 1,
        "posts": state["posts"]
    }


@han.dle(decrement, "$.number")
def decrement(number):
    "Manually decrement the state's number."
    return number - 1


@han.dle(new_post, "$.posts")
def new_post(posts, message=None):
    "Add a new post."
    return posts + [message]


@han.dle(count_posts, "$.posts", "$.number")
def count_posts(posts):
    "Set the state's number to the number of posts."
    return len(posts)
