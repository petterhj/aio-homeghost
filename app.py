# Imports
import aioreloader

from logger import logger
from core import Core
from config import config


# Main
if __name__ == '__main__':
    aioreloader.start()
    Core(config).run()
