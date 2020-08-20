import os
import sys

import syst.server as server

change_dir = os.path.dirname(sys.argv[0])

if change_dir:
    os.chdir(change_dir)


mainserver = server.MainServer()
mainserver.init()
mainserver.start()
