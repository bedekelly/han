let han = {};


han.use = function(url) {
    han.API = path => `ws://${url}/${path}`;
    han._dispatchSocket = new WebSocket(han.API("action"));

    han.dispatch = function(type, props = {}) {
        const action = {type, ...props};
        han._dispatchSocket.send(JSON.stringify(action));
    }

    han.onChange = function(path, callback) {
        let eventSocket = new WebSocket(han.API("state/" + path));
        eventSocket.onmessage = event => callback(event.data);
    }
}
