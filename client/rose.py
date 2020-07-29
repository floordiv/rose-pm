import sys

import commands
from rcore import Session


DEFAULT_PM_ADDR = ('127.0.0.1', 8888)


config = {
    'dest_path': 'installed',
    'reinstall': False,
    'pm_addr': DEFAULT_PM_ADDR
}

parse_args = (
    ('--reinstall', 'reinstall', lambda value: value == 'true'),
    ('--dest', 'dest_path', str),
    ('--server', 'pm_addr', lambda value: value.split(':'))
)


if __name__ == '__main__':
    args = sys.argv[1:]

    if not len(args):
        print('[ROSE] Usage: python3 rose.py <command> [args]')
        sys.exit(1)

    sess = Session((config['pm_addr'][0], int(config['pm_addr'][1])))
    command, *cmdargs = args

    for arg, dest_arg, key in parse_args:
        if arg in cmdargs:
            if cmdargs.index(arg) == len(cmdargs) - 1:  # just a flag
                config[dest_arg] = True
            else:
                val = cmdargs[cmdargs.index(arg) + 1]
                config[dest_arg] = key(val)
                
                cmdargs.remove(val)

            cmdargs.remove(arg)

    if command not in commands.__dict__:
        print('[ROSE] Unknown command:', command)
        sys.exit(1)

    command_function = commands.__dict__[command]
    command_function(sess, config, *cmdargs)
