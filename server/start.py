import os
import sys

import cmdargsparser as argparser
import syst.server as server
import syst.tar as tar


change_dir = os.path.dirname(sys.argv[0])

if change_dir:
    os.chdir(change_dir)


tar.pack_dir('repos/floordiv/repos_docs/anyversion1')

tar.unpack_dir('tmp/anyversion1.tar.gz', 'tmp/extracted', 'floordiv', 'repos_docs', 'anyversion1')
# server.worker()
