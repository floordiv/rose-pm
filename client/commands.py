import utils
from transmission import DownloadTransmission, UploadTransmission


def install(session, dest_path, *packages, reinstall_package=False):
    packages_to_install = utils.parse_packages(packages)

    for author, package in packages_to_install:
        if utils.isinstalled(dest_path, package) and utils.getauthor(dest_path, package) == author:
            print(f'[ROSE] Error: package already installed. Try to "rose update {author}:{package}" or "rose reinstall {author}:{package}"')
            continue

        print(f'[ROSE] Installing package: {author}:{package}')

        session.request('download', login=author, repo=package, version='&newest')

        # wow! Transmission is so easy to-do!
        trnsmsn = DownloadTransmission(session, author, package, '&newest', dest_path)
        trnsmsn.start()


def reinstall(session, dest_path, *packages):
    # this installs modules, but ignores previously installed versions

    install(session, dest_path, *packages, reinstall_package=True)
