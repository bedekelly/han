// Han's interactive debugger.

const debugApi = route => `http://localhost:8000/debug/${route}`

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


const app = new Vue({
    el: "#app",
    data: {
        states: [],
    }
});


Vue.component('snapshot', {
    props: ['state', 'active'],
    template: `
        <article class="snapshot {{ active ? 'active' : ''}}">
            <span class="action-name">
                <a class="state-button" href="#" v-on:click="changeState(state.id)">
                    {{ state.action.type }}
                </a>
            </span>
            <span class="diff-path">{{ state.diff.path }}</span>
            <pre class="diff-data">{{ state.diff.data }}</pre>
        </article>
    `,
    methods: {
        changeState: id => {
            postData(debugApi("state"), {id})
                .then(console.log)
                .catch(console.error)
        }
    }
});

function postData(url, data) {
    return fetch(url, {
        body: JSON.stringify(data),
        cache: 'no-cache',
        headers: {'Content-Type': 'application/json'},
        method: 'POST',
        mode: 'cors',
        redirect: 'follow',
        referrer: 'no-referrer',
    })
    .then(response => response.json()) // parses response to JSON
}


function updateStates() {
    fetch(debugApi("states"))
        .then(response => {
            return response.json();
        })
        .then(json => {
            app.states = json.states;
        })
        .catch(console.error)
}

updateStates();
han.use("localhost:8000");
han.onChange("$", updateStates);
