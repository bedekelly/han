# Han Example App

Han is a full-stack implementation of the Elm Architecture. This app
is a somewhat simplistic example of how it might be used.

## Back End & State

The state in this app is comprised of a number and a list of posts:

```python
# model.py

{
    "number": 0,
    "posts": []
}
```

Four [actions](actions.py) can be used to change this state:

- "Increment": increment the number
- "Decrement": decrement the number
- "New Post": add to the list of posts
- "Count Posts": set the number to the length of 'posts'

An action can look like this:

```python
{
    "type": "Count Posts"
}
```

or like this:

```python
{
    "type": "New Post",
    "text": "..."
}
```

Actions always have a `"type"` key with a value of the Action name. This is
so that Han knows which handlers to use.

They can also have any number of other attributes, like "text" in the example
above.

#### Defining Actions

Actions are defined using the `Action` class:

```python
# actions.py

increment   = Action("Increment")
decrement   = Action("Decrement")
new_post    = Action("New Post", "message")
count_posts = Action("Count Posts")
```

Notice that `new_post` uses a second parameter. Any number of parameters can
be used. For example, an action to create a new address might look like this:

```python
new_address = Action("New Address",
                     "house_number",
                     "street",
                     "city",
                     "county",
                     "country"
                     "postcode")
```

#### Handling Actions

To [handle these actions](update.py) in this app, the `han.dle` decorator is used.

```python
# update.py

@han.dle(increment)
def add_one(state):
    "Manually increment the state's number."
    return {
        number: state["number"] + 1
    }
```

The `add_one` function is chosen to handle `increment` actions. This means that
whenever the `increment` action is received, `add_one` will be called.

`add_one` accepts one argument, which is the current state of the app. Its
return value will be used as the next state for the app. Any connected client
will be sent the new state via their websocket connection – see more about this
in the front-end section!

#### More Specific Handlers

It's also possible for an action handler to specify which bit of the state it's
interested in.

```python
# update.py

@han.dle(decrement, "$.number")
def take_one(number):
    "Manually decrement the state's number."
    return number - 1
```

In the code above, the `han.dle` decorator is given a second argument, which
describes the parts of the state it needs to know about. It's using a syntax
called [JSON Path](https://invalid.invalid) to specify that it should only be
given the "number" part of the state, instead of the whole thing.

To read more about JSON Path, read the [documentation]() or [this easy guide]().

Here, the `take_one` function has specified that it only needs to know about
the `"number"` part of the state. By default, this means that it only needs
to return a new value for that number – not the whole state.

#### Even _More_ Specific Handlers

Sometimes, you might like to use one part of the state and change another.
The example we're using here is to set the `'number'` field based on the
number of posts.

While this is possible to do with a handler which takes and returns the entire
state, it's a good idea to be as specific as possible. For one thing, it
reduces the amount of boilerplate code needed to extract data from the old
state and build a new state. But even more importantly, you'll cut down on
the number of state updates being sent to clients where it's not necessary.

```python
# update.py

@han.dle(count_posts, "$.posts", "$.number")
def count_posts(posts):
    "Set the state's number to the number of posts."
    return len(posts)
```

In the code above, our handler function `count_posts` has specified that it
reads information from the `'posts'` field and returns the new value for the
`'number'` field.

#### Actions with Data

Finally, it's possible to add data to actions. For example, in this app we'd
like to be able to add to the list of posts!

```python
# update.py

@han.dle(new_post, "$.posts")
def new_post(posts, message=None):
    "Add a new post."
    return posts + [message]
```

Again, this action only affects the `'posts'` field, so the `"$.posts"` JSON
path has been used to specify that our handler function should only deal with
that value.

The `new_post` function here accepts a keyword argument of `message`. Han will
use the parameters defined in the `Action` to pass in this keyword argument.
This is a useful type-checking tool to ensure that your handler is only called
when all the required values are present.

#### Using Action Data with Specific Handlers

*Todo*: How does the API for JSON Path construction using request data work?
* `$.posts["user-{username}"]` example


## Front End

Nothing's on the front-end just yet :)
