from actors.tellstick.actor import TellstickActor
from actors.harmony.actor import HarmonyActor


# Config
config = {
    'server': {'host': '0.0.0.0', 'port': 8880},
    'actors': [
        {'class': TellstickActor, 'alias': 'tellstick', 'metadata': {
            'web': {
                'exported_events': [
                    {'label': 'On', 'event': 'tellstick.web.on', 'icon': 'brightness-7'},
                    {'label': 'Dim', 'event': 'tellstick.web.dim', 'icon': 'brightness-6'},
                    {'label': 'Off', 'event': 'tellstick.web.off', 'icon': 'brightness-2'}
                ],
            }
        }},
        {'class': HarmonyActor, 'alias': 'harmony', 'config': {'host': '192.168.1.6'}, 'metadata': {
            'web': {
                'state_label': 'state.current_activity',
                'exported_events': [
                    {'label': 'Mute', 'event': 'harmony.web.mute', 'icon': 'audio'}
                ],
            }
        }},
        # {'actor': KodiActor, 'alias': 'stue', 'host': '192.168.1.4', 'port': 1234}
    ],
    'macros': [
        {'events': ['socket.tellstick.web.off'], 'actions': [
            ('tellstick', 'off', 101),
            ('tellstick', 'off', 102),
            ('tellstick', 'off', 103),
            ('tellstick', 'off', 104),
        ]},
        {'events': ['socket.tellstick.web.on'], 'actions': [
            ('tellstick', 'on', 101),
            ('tellstick', 'on', 102),
            ('tellstick', 'on', 103),
            ('tellstick', 'on', 104),
        ]},
        {'events': ['socket.tellstick.web.dim'], 'actions': [
            ('tellstick', 'dim', 101),
            ('tellstick', 'dim', 102),
            ('tellstick', 'dim', 104, 50),
            # ('tellstick', 'dim', 203, 50),
            # ('tellstick', 'off', 103),
        ]},
        {'events': ['socket.harmony.web.mute'], 'actions': [
            ('harmony', 'command', 45627581, 'Mute'),
            # ('harmony', 'command', 45627582, 'Play'),
        ]},
        {'events': ['http.iamhome', 'tellstick.on.button'], 'actions': [
            ('harmony', 'start_activity', 27000842),
            ('tellstick', 'all_on', [999]),
        ]},
        {'events': ['tellstick.off.button', 'web.off'], 'actions': [
            ('harmony', 'start_activity', -1),
            ('tellstick', 'all_off', [999]),
        ]},
    ]
}