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
    repos = utils.parse_packages(repos)

    for author, repo in repos:
        if not utils.isinstalled(config['dest_path'], repo, author):
            print(f'[ROSE] {author}:{repo}: not installed')
            continue

        with open(config['dest_path'] + '/' + repo + '/.version') as repo_version:
            repo_info = json.load(repo_version)

        version = repo_info['version']

        if repo_info['author'] != author:
            print(f'[ROSE] Failed to check {author}:{repo}: another author given')
            continue

        local_hash = utils.gethash(config['dest_path'], repo)[1]
        server_response = session.request('get-version-hash', login=author, repo=repo, version=version)
        newest_version = session.request('get-version-hash', login=author, repo=repo, version='&newest')

        if server_response['type'] != 'succ' or newest_version['type'] != 'succ':
            print(f'[ROSE] Failed to check {repo}: {server_response["data"]}')
            continue

        server_hash = server_response['data'][1]

        if server_hash == local_hash:
            print(f'[ROSE] {author}:{repo}: ok')
        else:
            print(f'[ROSE] hashes do not match')

        if newest_version['data'][1] != local_hash:
            print(f'[ROSE] {author}:{repo}: updates are available ({version} -> {newest_version["data"]})')
        else:
            print(f'[ROSE] {author}:{repo}: you have the newest version installed ({version})')


def update(session, config, *repos):
    repos = utils.parse_packages(repos)

    for author, repo in repos:
        get_newest_version = session.request('get-newest-version', login=author, repo=repo)

        if get_newest_version['type'] == 'succ':
            version = get_newest_version['data']
        else:
            print(f'[ROSE] Failed to fetch the newest version of {author}:{repo}: {get_newest_version["data"]}')
            continue

        local_version = utils.load_version_info(config['dest_path'], repo)

        if local_version['version'] == version:
            print(f'[ROSE] {author}:{repo}: you have the newest version installed ({version})')
            continue

        print(f'[ROSE] {author}:{repo}: updating ({local_version} -> {version})')

        session.request('download', False, login=author, repo=repo, version=version)
        trnsmsn = DownloadTransmission(session, author, repo, version, config['dest_path'])
        trnsmsn.start()

