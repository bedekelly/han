import json
import copy
import flask

from uuid import uuid4

from collections import namedtuple
from queue import Queue

from flask_sockets import Sockets

from .tree import value_at, set_value_at
from .path import mutual_contains


def uuid():
    return str(uuid4())


def initial_state_entry(identifier, initial_state):
    return StateEntry(
        identifier,
        {"type": "Initial State"},
        initial_state,
        "$",
        initial_state,
        {}
    )


class Han:
    def __init__(self, flask_app, initial_state, debug=False):
        self.current_state_key = key = uuid()
        self.state_entries = [initial_state_entry(key, initial_state)]
        self.handlers = {}
        self.state_updates = []
        self.sockets = Sockets(flask_app)
        self.add_api()
        if debug:
            self.add_debug_api(flask_app)

    def add_api(self):
        "Add the websocket routes to let Han communicate with the frontend."
        self.sockets.route("/state/<path>")(self.state_updates_route)
        self.sockets.route("/action")(self.actions_route)

    def add_debug_api(self, app):
        app.route("/debug")(self.debug_route)
        app.route("/debug/states")(self.return_states_route)
        app.route("/debug/state", methods=["POST"])(self.set_state_route)

    @property
    def state_entry(self):
        "Getter for the 'state_entry' property."
        for state_entry in self.state_entries:
            if state_entry.key == self.current_state_key:
                return state_entry
        raise KeyError("Current state doesn't exist!")

    @property
    def state(self):
        return self.state_entry.state

    @staticmethod
    def debug_route():
        "Send the Debug HTML page."
        return flask.send_file("han/debug/debug.html")

    def set_state_route(self):
        "Debug route for setting the current state."
        data = flask.request.get_json(force=True)
        self.current_state_key = data["id"]
        entry = self.state_entry
        self.update_all_clients(entry.path, entry.new_data)
        return flask.jsonify({"message": "Done!"})

    def update_all_clients(self, path, new_state):
        "Send a state update to all clients."
        for update_queue in self.state_updates:
            update_queue.put(StateUpdate(path, new_state))

    def return_states_route(self):
        "Return a list of states, along with the actions which caused them."
        return flask.jsonify({
            "states": [
                {
                    "state": entry.state,
                    "action": entry.action,
                    "id": entry.key,
                    "diff": {
                        "path": entry.path,
                        "data": entry.new_data,
                        "old_data": entry.old_data
                    }
                }
                for entry in self.state_entries
            ]
        })

    def dispatch_action(self, action):
        "Dispatch an action to a handler, if there is one. Update our state."
        properties = {k: v for (k, v) in action.items() if k != "type"}
        handler, input_path, output_path = self.handlers[action["type"]]
        input_data = value_at(self.state, input_path)
        output_data = handler(input_data, **properties)
        self.update_all_clients(output_path, output_data)
        self.set_state_at(output_path, output_data, action)

    def set_state_at(self, path, new_data, action):
        "Write `data` to the state at the given JSON path."

        # What happens if the current state isn't the last entry?
        if self.state_entries[-1].key != self.current_state_key:
            raise NotImplementedError("Illegal state: write some branch logic!")

        # Store the data.
        old_data = value_at(self.state, path)

        # Set, or completely replace, the current state.
        if path == "$":
            new_state = new_data
        else:
            new_state = set_value_at(self.state, path, new_data)

        # Create a new state entry with the data changes.
        new_id = uuid()
        self.state_entries.append(StateEntry(
            new_id, action, new_state, path, new_data, old_data
        ))
        self.current_state_key = new_id

    def state_updates_route(self, socket, path):
        "Send state updates over a websocket connection."
        updates = Queue()
        self.state_updates.append(updates)

        # Send an initial state.
        socket.send(json.dumps(value_at(self.state, path)))

        while not socket.closed:
            state_update = updates.get()
            if mutual_contains(path, state_update.path):
                socket.send(json.dumps(value_at(self.state, path)))

    def actions_route(self, socket):
        "Receive actions over a websocket connection."
        while not socket.closed:
            action = socket.receive()
            if action:
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
StateEntry = namedtuple("StateEntry", "key, action, state, path, new_data, old_data")
