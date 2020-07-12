import sys

import cmdargsparser as argparser
import syst.server as server


def start(args):
    server.worker()
