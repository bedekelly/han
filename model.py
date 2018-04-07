from . import han
import mongo


han.save_with(mongo.save_states)
han.get_states_with(mongo.get_states)


han.state = {
    "number": 0,
    "posts": []
}
