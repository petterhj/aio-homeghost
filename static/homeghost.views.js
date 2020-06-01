// ====== View: Dashboard ======================================================
const Dashboard = { 
    template: `
        <div class="view">
         <actors :instances="actors" />

         <event-log :events="events" />
        </div>
    `,
    data: function() {
        return { }
    },
    computed: {
        actors() { return store.state.actors; },
        events() { return store.state.events; }
    }
};


// ====== View: Config =========================================================
const Config = { 
    template: `
        <div class="view">
         <div v-for="actor in actors">
          <b>{{actor.alias}}</b><br>
          -STATE:{{actor.state}}<br>
          -DATA:{{actor.data}}<br><br>
         </div>
        </div>
    `,
    computed: {
        actors() { return store.state.actors; },
    }
};
