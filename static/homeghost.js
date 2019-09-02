Vue.use(new VueSocketIO({
    debug: false,
    connection: 'http://192.168.1.15:8880'
}));
Vue.use(Vuebar);
Vue.use(vueMoment);


Vue.component('actors', {
    props: ["item"],
    data() {
        return {
            isOpen: false,
            active: false,
            navList: [
                {
                    url: "#",
                    name: 'harmony',
                    label: 'Listen Chromecast',
                    children: [
                        {
                            url: "https://twitter.com/andrejsharapov",
                            name: "Twitter",
                            target: "_blank"
                        }, {
                            url: "https://dribbble.com/andrejsharapov",
                            name: "Dribbble",
                            target: "_blank"
                        },
                    ]
                },
                {
                    url: "#",
                    name: 'tellstick',
                    label: '9 devices',
                }
            ]
        };
    },
    template: `
        <ul>
         <li v-for="item in navList">
          <template v-if="item.children">
           <div class="actor" @click="isOpen = !isOpen, active = !active" :class="{ active }">
            <h1>{{item.name}}</h1>
            {{item.label}}
           </div>
           <div :class="{ isOpen }" class="dropdown">
            <ul>
             <li v-for="{ url, name, index, target } in item.children" :key="index">
              <a target="target">{{ name }}</a>
             </li>
            </ul>
           </div>
          </template>
          <template v-else>
           <div class="actor">
            <h1>{{item.name}}</h1>
            {{item.label}}
           </div>
          </template>
         </li>
        </ul>`
});




var app = new Vue({
    el: '#app',
    // delimiters: ['[[', ']]'],
    data: {
        is_connected: false,
        actors: [],
        events: [],
    },
    created() {},
    mounted: function() {
        console.log(this.$socket)
        // this.$socket.connect();
        // 
        // this.$socket.emit('', {});
    },
    methods: {
        on: function() {
            this.$socket.emit('event', {
                source: 'web',
                name: 'on'
            });
        },
        off: function() {
            this.$socket.emit('event', {
                source: 'web',
                name: 'off'
            });
        },
        dim: function() {
            this.$socket.emit('event', {
                source: 'web',
                name: 'dim'
            });
        },
        toggle_connection: function() {
            if (this.is_connected) {
                this.$socket.disconnect();
            } else {
                this.$socket.connect();
            }
        }
    },
    computed: {},
    sockets: {
        connect: function () {
            console.log('CONNECTED');
            this.$socket.emit('pingtest', {hey: true});
            this.is_connected = true;
            this.events = [];

            let data = this;

            // Status
            this.$http.get('/status/')
                .then((response) => {
                    console.log(response.body);

                    // Actors
                    data.actors = response.body.actors;

                    // Backlog
                    response.body.backlog.forEach(function(event) {
                        data.events.unshift(event);
                    });
                })
                .catch((err) => {
                    console.log('!!!!!!!')
                    console.log(err);
                });
        },
        event: function(data) {
            console.log('------EVNT-----------------------------------:');
			console.log(data);
            console.log(data.actions);
            this.events.unshift(data);
        },
        result: function(result) {
            console.log('------RSLT-----------------------------------:');
            console.log(result);

            this.events.forEach(function(event) {
                event.actions.forEach(function(action) {
                    if (action.uuid === result.uuid) {
                        action.completed_timestamp = result.completed_timestamp;
                        action.success = result.success;
                        action.message = result.message;
                    }
                });
            });
        },
        disconnect: function() {
            console.log('DISCONNECTED');
            this.is_connected = false;
        }
    }
});