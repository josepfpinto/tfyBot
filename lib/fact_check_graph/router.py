"""Router"""
from lib import logger

this_logger = logger.configure_logging('ROUTER')


def router(state):
    '''Router'''
    this_logger.info("\n\nWe are inside ROUTER: ")
    this_logger.info('%s\n', state)
    return state["next"]
