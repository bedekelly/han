import json
import copy

from collections import namedtuple
from queue import Queue

from flask_sockets import Sockets

from .tree import value_at, set_value_at
from .path import mutual_contains


class Han:
    def __init__(self, flask_app, initial_state):
        self.states = [initial_state]
        self.handlers = {}
        self.state_updates = []
        self.sockets = Sockets(flask_app)
        self.add_api()

    def add_api(self):
        "Add the websocket routes to let Han communicate with the frontend."
        self.sockets.route("/state/<path>")(self.state_updates_route)
        self.sockets.route("/action")(self.actions_route)

    @property
    def state(self):
        return self.states[-1]

    @state.setter
    def state(self, new_state):
        self.states.append(new_state)

    def dispatch_action(self, action):
        "Dispatch an action to a handler, if there is one. Update our state."
        properties = {k: v for (k, v) in action.items() if k != "type"}
        handler, input_path, output_path = self.handlers[action["type"]]
        input_data = value_at(self.state, input_path)
        output_data = handler(input_data, **properties)
        for update_queue in self.state_updates:
            update_queue.put(StateUpdate(output_path, output_data))
        self.set_state_at(output_path, output_data)

    def set_state_at(self, path, new_data):
        "Write `data` to the state at the given JSON path."
        if path == "$":
            self.state = new_data
        else:
            self.state = set_value_at(self.state, path, new_data)

    def state_updates_route(self, socket, path):
        "Send state updates over a websocket connection."
        updates = Queue()
        self.state_updates.append(updates)

        while not socket.closed:
            state_update = updates.get()
            if mutual_contains(path, state_update.path):
                socket.send(json.dumps(value_at(self.state, path)))

    def actions_route(self, socket):
        "Receive actions over a websocket connection."
        while not socket.closed:
            action = socket.receive()
            self.dispatch_action(json.loads(action))

    def dle(self, action, input_path="$", output_path=None):
        "Return something which maps a given function to an action."
        def map_action_to(function):
            """
            When `action` is dispatched, we should call `function` with
            arguments `state[input_path]` and any properties in the action.
            Then take the result, and assign it to `state[output_path]`.
            """
            out_path = output_path or input_path
            self.handlers[action.name] = ActionHandler(
                function, input_path, out_path
            )
            return function
        return map_action_to


class Action:
    def __init__(self, name, *properties):
        self.name = name
        self.properties = properties


ActionHandler = namedtuple("ActionHandler", "handler, input_path, output_path")
StateUpdate = namedtuple("StateUpdate", "path, data")
