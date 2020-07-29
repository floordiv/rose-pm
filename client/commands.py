import utils
from transmission import DownloadTransmission, UploadTransmission


def install(session, config, *packages):
    packages_to_install = utils.parse_packages(packages)
    dest_path = config['dest_path']

    for author, package in packages_to_install:
        if utils.isinstalled(dest_path, package) and utils.getauthor(dest_path, package) == author\
                and not config['reinstall']:
            print(f'[ROSE] Error: package already installed. Try to use --reinstall or "rose update {author}:{package}"')
            continue

        print(f'[ROSE] Installing package: {author}:{package}')

        version = session.request('get-newest-version', login=author, repo=package)

        if version['type'] == 'succ':
            version = version['data']
        else:
            return print(f'[ROSE] Failed to fetch the newest version of {author}:{package}: {version["data"]}')

        session.request('download', False, login=author, repo=package, version=version)

        # wow! Transmission is so easy to-do!
        trnsmsn = DownloadTransmission(session, author, package, version, dest_path)
        trnsmsn.start()


def reinstall(session, config, *packages):
    # this installs modules, but ignores previously installed versions
    config['reinstall'] = True

    install(session, config, *packages)
