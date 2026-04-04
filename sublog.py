import logging

# logger = logging.getLogger(__name__)
logger = logging.getLogger('sublog')
# logger.setLevel(logging.DEBUG)


def nepsub():
    logger.debug('this is debug')
    logger.info('this is info')
