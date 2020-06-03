// ====== Component: Event =====================================================

Vue.component('event', {
    template: `
        <div class="event" :class="{dim: event.actions.length == 0}">
         <h1>
          <i class="zmdi zmdi-flash"></i>
          <b>{{event.source}}</b>.{{event.name}} [actions={{event.actions.length}}] [{{event.client}}] {{event.payload}}
          <span class="timestamp">{{event.created_timestamp|moment("YYYY-MM-DD, HH:mm:ss")}}</span>
         </h1>

         <div v-for="action in event.actions" class="action" :title="action.uuid">
          <h2>
           <i class="zmdi zmdi-label-alt"></i>
           {{action.actor}}.{{action.method}}({{action.args}})
           <span class="timestamp">{{action.created_timestamp|moment("YYYY-MM-DD, HH:mm:ss")}}</span>
           <span class="message" v-if="action.message">{{action.message}}, {{action.completed_timestamp|moment("YYYY-MM-DD, HH:mm:ss")}}</span>
          </h2>
          <!-- <h3 ><i class="zmdi zmdi-circle"></i>{{action.executed}}, {{action.success}}, </h3> -->
         </div>
        </div>`,
    props: ['event'],
    computed: {}
});


// ====== Component: Event log =================================================

Vue.component('event-log', {
    template: `
        <div class="log" v-bar>
         <div>
          <event v-for="event in events" :event="event" :key="event.uuid" />
         </div>
        </div>`,
    props: ['events'],
    computed: {}
});


// ====== Component: Actors ====================================================

Vue.component('actor', {
    template: `
        <div class="actor-wrapper">
         <div class="actor" 
           @click="$emit('actor-select')"
           :class="[
                actor.name.toLowerCase(), 
                {active: isActive},
                {focused: isFocused}
            ]">
          <h1>{{actor.alias}}</h1>
          <span>{{actor.name}}: {{stateLabel}}</span>
         </div>

         <div :class="" class="dropdown">
           <li v-for="item in exportedEvents">
            <div class="actor-event" @click="selectEvent(item.event)">
             <i class="zmdi" :class="getEventIcon(item)"></i> {{item.label}}
            </div>
           </li>
          </ul>
         </div>
        </div>
    `,
    props: ['actor', 'isFocused'],
    computed: {
        metadata: function() {
            return this.actor.metadata;
        },
        isActive: function() {
            // if (this.metadata.state_active && this.metadata.state_active.length > 0) {    
            //     let obj = this.actor;
            //     this.metadata.state_active.forEach(function(state) {
            //         console.log(state)
            //         let arr = state.split('.');
            //         while (arr.length && (obj = obj[arr.shift()]));
            //         console.log(obj)
            //         if (!obj) {
            //             return false;
            //         }
            //     });
            //     return true;
            // }
            return this.actor.state.running;
        },
        exportedEvents: function() {
            if (this.metadata && this.metadata.web && this.metadata.web.exported_events) {
                console.log(this.metadata.web.exported_events)
                return this.metadata.web.exported_events;
            }
            return [];
        },
        stateLabel: function() {
            if (this.metadata && this.metadata.web && this.metadata.web.state_label) {
                let obj = this.actor;
                let arr = this.metadata.web.state_label.split('.');
                while (arr.length && (obj = obj[arr.shift()]));
                return obj;
            }
            return (this.actor.state.running ? "Active" : "Not active");
        }
    },
    methods: {
        selectEvent: function(event_name) {
            // this.$emit('event', event_name);
            console.log('EMIT', event_name)
            this.$socket.emit('event', {
                name: event_name
                // source: 'tellstick',
                // name: 'on.button'
            });

            this.$emit('click-inside');
        },
        getEventIcon: function(event) {
            return 'zmdi-' + (event.icon ? event.icon : 'circle');
        }
    }
});


Vue.component('actors', {
    template: `
        <div class="actors" v-click-outside="hideDropdown">
         <ul>
          <li v-for="actor in instances">
           <actor 
             :actor="actor"
             :is-focused="(focusedActor == actor.alias)" 
             @actor-select="toggleDropdown(actor)"
             @click-inside="hideDropdown" />
          </li>
         </ul>
        </div>`,
    props: ['instances'],
    data() { 
        return {
            focusedActor: '',
        }; 
    },
    methods: {
        hideDropdown: function() {
            this.focusedActor = '';
            console.log('!!!!!!!!')
        },
        toggleDropdown: function(actor) {
            // console.log('TD', actor)
            if (this.focusedActor && this.focusedActor == actor.alias) {
                this.focusedActor = '';
            } else {
                this.focusedActor = actor.alias;
            }
        }
    }
});