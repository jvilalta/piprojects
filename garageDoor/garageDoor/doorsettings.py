import os
import ConfigParser
import logging


config = ConfigParser.RawConfigParser()

def initialize(path):
    logging.debug("initializing config")
    logging.debug("reading config from %s",path)
    config.read(path)

    