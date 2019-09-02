from loguru import logger

logger.add('homeghost.log', enqueue=True, level='INFO')