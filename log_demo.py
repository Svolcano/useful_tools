import logging
from lib.log.log_config import setup_logging


setup_logging()

logger = logging.getLogger('root')

logger.info("123")


logger_my = logging.getLogger("my_module")
logger_my.error("kkk")