// ====== View: Event log ======================================================
Vue.component('event-log', {
    template: `
        <div class="log" v-bar>
         <div>
          <div class="event" v-for="event in events"
            :class="{dim: event.actions.length == 0}" >
           <h1>{{event.source}}.{{event.name}} [{{event.actions.length}}]</h1>
           <div v-for="action in event.actions" class="action" :title="action.uuid">
            <h2>
             {{action.actor}}.{{action.method}}({{action.args}})
             <span class="uuid">{{action.created_timestamp|moment("YYYY-MM-DD, HH:mm:ss")}}</span>
             <span class="message" v-if="action.message">{{action.message}}, {{action.completed_timestamp|moment("YYYY-MM-DD, HH:mm:ss")}}</span>
            </h2>
            <!-- <h3 ><i class="zmdi zmdi-circle"></i>{{action.executed}}, {{action.success}}, </h3> -->
           </div>
          </div>
         </div>
        </div>`,
    props: ['events'],
    computed: {}
});


// ====== View: Actors =========================================================
Vue.component('actors', {
    template: `
        <div class="actors" v-click-outside="hideDropdown">
         <ul>
          <li v-for="actor in instances">
           <template v-if="actor.events">
            <div class="actor" 
                :class="[actor.actor.toLowerCase(), {active: activeActor == actor.alias}]" 
                @click="toggleDropdown(actor)" >
             <h1>{{actor.alias}}</h1>
             <span>{{actor.state.label}}</span>
            </div>
            <div :class="" class="dropdown">
             <ul>
              <li v-for="event in actor.events">
               <div class="actor-event" @click="selectEvent(event.event)">
                <i class="zmdi" :class="getEventIcon(event)"></i> {{event.label}}
               </div>
              </li>
             </ul>
            </div>
           </template>
           <template v-else>
            <div class="actor">
             <h1>{{actor.alias}}</h1>
             <span>{{actor.state.label}}</span>
            </div>
           </template>
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
            // console.log('!!!!!!!!')
        },
        toggleDropdown: function(actor) {
            if (this.activeActor && this.activeActor == actor.alias) {
                this.activeActor = '';
            } else {
                this.activeActor = actor.alias;
            }
        },
        selectEvent: function(event_name) {
            // this.$emit('event', event_name);
            console.log('EMIT', event_name)
            this.$socket.emit('event', {
                event: event_name
                // source: 'tellstick',
                // name: 'on.button'
            });

            this.hideDropdown();
        },
        getEventIcon: function(event) {
            return 'zmdi-' + (event.icon ? event.icon : 'circle');
        }
    }
});