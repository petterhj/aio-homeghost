// ====== Component: Event =====================================================

Vue.component('event', {
    template: `
        <div class="event" :class="{dim: event.actions.length == 0}">
         <h1>
          <i class="zmdi zmdi-flash"></i>
          {{event.source}}.{{event.name}} [{{event.actions.length}}] {{event.payload}}
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
           :class="[actor.actor.toLowerCase(), {
             active: isActive
           }]">
          <h1>{{actor.alias}}</h1>
          <span>{{actor.web.label}}</span>
         </div>

         <div :class="" class="dropdown">
          <ul>
           <li v-for="item in actor.web.menu">
            <div class="actor-event" @click="selectEvent(item.event)">
             <i class="zmdi" :class="getEventIcon(item)"></i> {{item.label}}
            </div>
           </li>
          </ul>
         </div>
        </div>
    `,
    props: ['actor', 'isActive'],
    methods: {
        selectEvent: function(event_name) {
            // this.$emit('event', event_name);
            console.log('EMIT', event_name)
            // this.$socket.emit('event', {
            //     event: event_name
            //     // source: 'tellstick',
            //     // name: 'on.button'
            // });

            this.$emit('click-inside');
        },
        getEventIcon: function(event) {
            return 'zmdi-' + (event.icon ? event.icon : 'circle');
        }
    }
});

/*
@click=""
*/

Vue.component('actors', {
    template: `
        <div class="actors" v-click-outside="hideDropdown">
         <ul>
          <li v-for="actor in instances">
           <actor 
             :actor="actor"
             :is-active="(activeActor == actor.alias)" 
             @actor-select="toggleDropdown(actor)"
             @click-inside="hideDropdown" />
          </li>
         </ul>
        </div>`,
    props: ['instances'],
    data() { 
        return {
            activeActor: '',
        }; 
    },
    methods: {
        hideDropdown: function() {
            this.activeActor = '';
            console.log('!!!!!!!!')
        },
        toggleDropdown: function(actor) {
            // console.log('TD', actor)
            if (this.activeActor && this.activeActor == actor.alias) {
                this.activeActor = '';
            } else {
                this.activeActor = actor.alias;
            }
        }
    }
});