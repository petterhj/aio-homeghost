# Imports
import aioreloader

from logger import logger
from core import Core
from actors.tellstick import TellstickActor
from actors.harmony import HarmonyActor



# Config
config = {
    'server': {'host': '0.0.0.0', 'port': 8880},
    'actors': [
        {'class': TellstickActor, 'alias': 'tellstick',
        	# 'web': {'menu': [
        	# 	{'label': 'On', 'event': 'tellstick.web.on', 'icon': 'brightness-7'},
        	# 	{'label': 'Dim', 'event': 'tellstick.web.dim', 'icon': 'brightness-6'},
        	# 	{'label': 'Off', 'event': 'tellstick.web.off', 'icon': 'brightness-2'}
        	# ]}
       	},
        {'class': HarmonyActor, 'alias': 'harmony', 
        	'config': {'host': '192.168.1.6'},
        	# 'web': {'menu': [
        	# 	{'label': 'Mute receiver', 'event': 'harmony.web.mute', 'icon': 'cast-connected'},
         #        {'label': 'Watch Chromecast', 'event': 'harmony.web.chromecast', 'icon': 'cast-connected'},
        	# 	{'label': 'Listen Chromecast', 'event': 'harmony.web.chromecast.audio', 'icon': 'audio'},
        	# 	{'label': 'Off', 'event': 'harmony.web.off', 'icon': 'power'}
        	# ]}
        },
        # {'actor': KodiActor, 'alias': 'stue', 'host': '192.168.1.4', 'port': 1234}
    ],
    'macros': [
        {'events': ['tellstick.web.off'], 'actions': [
            ('tellstick', 'off', 101),
            ('tellstick', 'off', 102),
            ('tellstick', 'off', 103),
            ('tellstick', 'off', 104),
        ]},
        {'events': ['tellstick.web.on'], 'actions': [
            # ('tellstick', 'on', 101),
            # ('tellstick', 'on', 102),
            ('tellstick', 'on', 103),
            # ('tellstick', 'on', 104),
        ]},
        {'events': ['tellstick.web.dim'], 'actions': [
            ('tellstick', 'dim', 101),
            ('tellstick', 'dim', 102),
            ('tellstick', 'dim', 104, 50),
            # ('tellstick', 'dim', 203, 50),
            # ('tellstick', 'off', 103),
        ]},
        {'events': ['harmony.web.mute'], 'actions': [
            ('harmony', 'command', 45627582, 'Play'),
        ]},
        {'events': ['harmony.web.off'], 'actions': [
            # ('harmony', 'start_activity', -1),
            ('tellstick', 'dim', 101),
        ]},
        {'events': ['tellstick.on.button'], 'actions': [
            # ('tellstick', 'on', 203),
            # ('tellstick', 'on', 202),
            # ('tellstick', 'on', 201),
            # ('tellstick', 'on', 101),
            # ('tellstick', 'on', 102),
            # ('tellstick', 'on', 103),
            # ('tellstick', 'on', 104),
            ('harmony', 'start_activity', 27000843),
        ]},
        {'events': ['tellstick.off.button', 'web.off'], 'actions': [
            # ('tellstick', 'off', 101),
            # ('tellstick', 'off', 102),
            # ('tellstick', 'off', 103),
            # ('tellstick', 'off', 104),
            # ('tellstick', 'off', 201),
            # ('tellstick', 'off', 202),
            # ('tellstick', 'off', 203),
            # ('harmony', 'command', 45627582, 'Play'),
            ('harmony', 'start_activity', -1),
        ]},
    ]
}



# Main
if __name__ == '__main__':
    aioreloader.start()
    Core(config).run()