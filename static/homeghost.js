// Vue.use(Vuex);
// Vue.use(Vuebar);
Vue.use(vueMoment);


const socket = io('http://{0}:{1}/'.format(document.domain, '8880'), { 
    autoConnect: true
});


// ====== Store ================================================================
const store = new Vuex.Store({
    state: {
        isConnected: false,
        socketId: undefined,
        // status: {},
        events: [],
        actors: [],
    },
    mutations: {
        SOCKET_CONNECT: (state) => {
            console.log('Connected to socket server');
            state.isConnected = true;
            state.socketId = socket.id;
        },
        SOCKET_CONNECT_ERROR(state, test) {
            console.log('Could not connect to socket server');
            state.isConnected = false;
            state.socketId = null;
        },
        SOCKET_DISCONNECT(state) {
            console.log('Disconnected from socket server');
            state.isConnected = false;
            state.socketId = null;
        },
        SOCKET_STATUS: (state, data) => {
            console.log('Server status received');
            // state.status = 

            // Actors
            state.actors = data.actors;

            // Event backlog
            state.events = [];
            
            data.backlog.forEach(function(event) {
                state.events.unshift(event);
            });
        },
        SOCKET_EVENT: (state, event) => {
            console.log('Event received', event);
            // Add event
            state.events.unshift(event);
        },
        SOCKET_RESULT: (state, result) => {
            // Update event results
            state.events.forEach(function(event) {
                event.actions.forEach(function(action) {
                    if (action.uuid === result.uuid) {
                        action.completed_timestamp = result.completed_timestamp;
                        action.success = result.success;
                        action.message = result.message;
                    }
                });
            });
        },
        SOCKET_STATE: (state, update) => {
            console.log('State update received', update);
            state.actors.forEach(function(actor) {
                if (actor.name == update.name && actor.alias == update.alias) {
                    actor.state[update.state.prop] = update.state.value;
                }
            });
        },
    },
    actions: {
        // clearRequestsLog({commit}) {
        //     console.log('Clearing requests log');
        //     commit('REQUESTS_LOG_CLEARED');
        // }
    }
});


Vue.use(VueSocketIOExt, socket, { store });



// ====== Router ===============================================================
Vue.use(VueRouter)

const router = new VueRouter({
  routes: [
      { path: '/', component: Dashboard },
      { path: '/config', component: Config },
    ],
});


// ====== App ==================================================================
var app = new Vue({
    router,
    store,
    data: {
        currentMenuKey: '/',
        actors: [],
    },
    computed: {
        isConnected() { return store.state.isConnected; },
        socketId() { return store.state.socketId; },
    },
    watch: {
        '$route' (to, from) {
            console.log('Routing from '+from.path+' to '+to.path);

            // if (to.params.category != this.currentCategory) {
            //     this.setCategory(to.params.category);
            // }
        }
    },
    methods: {
        handleMenuClick(e) {
            console.log(e.key, this.currentMenuKey)
            if (e.key != this.currentMenuKey) {
                this.currentMenuKey = e.key;
                // console.log('click', e)
                // console.log(e.item.active);
                router.push(e.key);
            }
        },
        toggleConnection: function() {
            if (this.isConnected) {
                this.$socket.disconnect();
            } else {
                this.$socket.connect();
            }
        }
    },
    created() {
        this.currentMenuKey = this.$route.path;
    },
    mounted: function() {
        
    },
}).$mount('#app');