import sys

from rcore import Session


DEFAULT_PM_ADDR = ('127.0.0.1', 8888)


class Commands:
    @staticmethod
    def install(session, *packages_list):
        packages = parse_packages(packages_list)

    @staticmethod
    def update(session, *packages_list):
        packages = parse_packages(packages_list)

    @staticmethod
    def installed_packages(session):
        ...

    @staticmethod
    def available_packages(session):
        ...


def parse_packages(packages):
    parsed = []

    for package in packages:
        if ':' not in package:
            author, package_name = 'floordiv', package   # by default, you are downloading packages from project's author
        else:
            author, package_name = package.split(':')

        parsed.append((author, package_name))

    return parsed


def transmission(session):
    """
    This is a transmission protocol

    Transmission steps:
        Client receives a packet with information about downloading version
    """

    ...


if __name__ == '__main__':
    args = sys.argv[1:]

    if not len(args):
        print('[ROSE] Usage: python3 rose.py <command> [args]')
        sys.exit(1)

    sess = Session()
    command, *cmdargs = args

    if not hasattr(Commands, command):
        print('[ROSE] Unknown command:', command)
        sys.exit(1)

    command_function = getattr(Commands, command)
    command_function(sess, *args)
