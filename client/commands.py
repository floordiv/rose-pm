import json

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


def check(session, config, *repos):
    for repo in repos:
        if not utils.isinstalled(config['dest_path'], repo):
            print(f'[ROSE] {repo}: not installed')

        with open(config['dest_path'] + '/' + repo + '/.version') as repo_version:
            repo_info = json.load(repo_version)

        version = repo_info['version']
        author = repo_info['author']

        local_hash = utils.gethash(config['dest_path'], repo)[1]
        server_response = session.request('get-version-hash', login=author, repo=repo, version=version)
        newest_version = session.request('get-version-hash', login=author, repo=repo, version='&newest')

        if server_response['type'] != 'succ' or newest_version['type'] != 'succ':
            return print(f'[ROSE] Failed to check {repo}: {server_response["data"]}')

        server_hash = server_response['data'][1]

        if server_hash == local_hash:
            print(f'[ROSE] {repo}: ok')
        else:
            print(f'[ROSE] hashes do not match')
            print(server_hash, local_hash)

        if newest_version['data'][1] != local_hash:
            print(f'[ROSE] {repo}: updates are available')
