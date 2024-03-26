"""Router"""
import logging


def router(state):
    '''Router'''
    logging.info("\nWe are inside ROUTER: ")
    logging.info(state, '\n')
    return state["next"]
