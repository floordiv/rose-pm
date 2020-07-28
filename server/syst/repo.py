import os
import json
import hashlib

import syst.tar as tar
import syst.transmission as transmission


def get_users():
    return [user for user in os.listdir('repos') if not os.path.isfile(user)]


def get_repos(user):
    return [file for file in os.listdir('repos/' + user) if not os.path.isfile(file)]


def get_versions(user, repo):
    if not user_exists(user) or not exists(user, repo):
        return None

    return os.listdir('repos/' + user + '/' + repo)


def get_version(user, repo, version):
    if version_exists(user, repo, version):
        version, version_path = _get_version_path(user, repo, version)

        return [f'{version_path}/{file}' for file in os.listdir(version_path)]


def get_newest_version(user, repo):
    with open(f'repos/{user}/{repo}/.repo') as repo_info:
        repo_info = json.load(repo_info)

    return repo_info['last-version']


def exists(user, repo):
    return repo in get_repos(user)


def version_exists(user, repo, version):
    return (user_exists(user) and exists(user, repo) and version in get_versions(user, repo)) or version == '&newest'


def user_exists(user):
    return user in get_users()


def get_repo_info(user, repo):
    with open(f'repos/{user}/{repo}/.repo') as repo_inf:
        return json.load(repo_inf)


def get_version_info(user, repo, version):
    assert user_exists(user) and exists(user, repo) and version_exists(user, repo, version)

    repo_info = get_repo_info(user, repo)

    version_hash = repo_info['versions-hashes'][version]
    version_is_the_newest = repo_info['last-version'] == version
    version_size = 0

    for dirpath, dirnames, filenames in os.walk(f'repos/{user}/{repo}/{version}'):
        for file in filenames:
            file_path = os.path.join(dirpath, file)

            # skip if it is symbolic link
            if not os.path.islink(file_path):
                version_size += os.path.getsize(file_path)

    return {'info': repo_info,
            'hash': version_hash,
            'is-the-newest': version_is_the_newest,
            'size': version_size}


def gethash(user, repo, version):
    files = get_version(user, repo, version)

    if files:
        hashes = {}

        for file in files:
            with open(file, 'rb') as file_source:
                hashes[file] = hashlib.sha256(bytes(file_source)).hexdigest()

        total_hash = hashlib.sha256(bytes(''.join(hashes.values()).encode())).hexdigest()

        return hashes, total_hash


def download(conn, user, repo, version):
    assert user_exists(user) and exists(user, repo) and version_exists(user, repo, version)
    print('oka')

    target = _get_tar_version(user, repo, version)
    print('why')

    trnsmsn = transmission.UploadTransmission(conn, target)
    print('ok, but...')
    trnsmsn.start()


def _get_version_path(user, repo, version):
    assert user_exists(user) and exists(user, repo)

    if version == '&newest':
        with open(f'repos/{user}/{repo}/.repo') as repo_info:
            repo_info = json.load(repo_info)

        newest = repo_info['last-version']
        return f'repos/{user}/{repo}/{newest}'

    return version, f'repos/{user}/{repo}/{version}'


def _get_tar_version(user, repo, version):
    version, dest_path = _get_version_path(user, repo, version)
    print('btw')

    # I will remove this code later, when on upload, tar archive will create automatically
    if version + '.tar.gz' not in os.listdir(f'repos/{user}/{repo}'):
        print('nano!')
        tar.pack_dir(version, dest_path, f'repos/{user}/{repo}')
        print('olololo')

    print('lol?')
    return f'repos/{user}/{repo}/{version}.tar.gz'
