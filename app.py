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
        {'class': TellstickActor, 'alias': 'tellstick'},
        {'class': HarmonyActor, 'alias': 'harmony', 'config': {'host': '192.168.1.6'}},
        # {'actor': KodiActor, 'alias': 'stue', 'host': '192.168.1.4', 'port': 1234}
    ],
    'macros': [
        # {'events': ['web.off'], 'actions': [
        #     # ('tellstick', 'off', 101),
        #     # ('tellstick', 'off', 102),
        #     ('tellstick', 'off', 103),
        #     # ('tellstick', 'off', 104),
        # ]},
        {'events': ['web.on'], 'actions': [
            # ('tellstick', 'on', 101),
            # ('tellstick', 'on', 102),
            ('tellstick', 'on', 103),
            # ('tellstick', 'on', 104),
        ]},
        {'events': ['web.dim'], 'actions': [
            # ('tellstick', 'dim', 101),
            # ('tellstick', 'dim', 102),
            # ('tellstick', 'dim', 104, 50),
            # ('tellstick', 'dim', 203, 50),
            ('tellstick', 'off', 103),
        ]},

        {'events': ['tellstick.on.button'], 'actions': [
            # ('tellstick', 'on', 203),
            # ('tellstick', 'on', 202),
            # ('tellstick', 'on', 201),
            # ('tellstick', 'on', 101),
            # ('tellstick', 'on', 102),
            ('tellstick', 'on', 103),
            # ('tellstick', 'on', 104),
            ('harmony', 'start_activity', 27000842),
        ]},
        {'events': ['tellstick.off.button', 'web.off'], 'actions': [
            # ('tellstick', 'off', 101),
            # ('tellstick', 'off', 102),
            # ('tellstick', 'off', 103),
            # ('tellstick', 'off', 104),
            # ('tellstick', 'off', 201),
            # ('tellstick', 'off', 202),
            # ('tellstick', 'off', 203),
            ('harmony', 'command', 45627582, 'Play'),
        ]},
    ]
}


# Main
if __name__ == '__main__':
    aioreloader.start()
    Core(config).run()