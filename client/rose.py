import sys

import commands
from rcore import Session


DEFAULT_PM_ADDR = ('127.0.0.1', 8888)


if __name__ == '__main__':
    args = sys.argv[1:]

    if not len(args):
        print('[ROSE] Usage: python3 rose.py <command> [args]')
        sys.exit(1)

    sess = Session()
    command, *cmdargs = args

    if command not in commands.__dict__:
        print('[ROSE] Unknown command:', command)
        sys.exit(1)

    command_function = commands.__dict__[command]
    command_function(sess, 'installed', *cmdargs)
