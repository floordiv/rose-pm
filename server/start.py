import os
import sys

import cmdargsparser as argparser
import syst.server as server


change_dir = os.path.dirname(sys.argv[0])

if change_dir:
    os.chdir(change_dir)


def start():
    server.worker()


start()
