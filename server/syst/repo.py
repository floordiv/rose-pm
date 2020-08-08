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
    assert user_exists(user) and exists(user, repo)

    return [version for version in os.listdir('repos/' + user + '/' + repo) if version.endswith('.tar.gz')]


def get_newest_version(user, repo):
    with open(f'repos/{user}/{repo}/.repo') as repo_info:
        repo_info = json.load(repo_info)

    return repo_info['last-version']


def exists(user, repo):
    return repo in get_repos(user)


def version_exists(user, repo, version):
    return (user_exists(user) and exists(user, repo) and version + '.tar.gz' in get_versions(user, repo)) or version == '&newest'


def user_exists(user):
    return user in get_users()


def get_repo_info(user, repo):
    with open(f'repos/{user}/{repo}/.repo') as repo_inf:
        return json.load(repo_inf)


def get_version(user, repo, version):
    version_name, _ = _get_version_path(user, repo, version)

    return version_name


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
    version_name, path_to_tar = _get_version_path(user, repo, version)

    with open(path_to_tar, 'rb') as file_source:
        return hashlib.sha256(file_source.read()).hexdigest()


def download(conn, user, repo, version):
    assert user_exists(user) and exists(user, repo) and version_exists(user, repo, version)

    target = _get_tar_version(user, repo, version)

    trnsmsn = transmission.UploadTransmission(conn, target)
    trnsmsn.start()


def _get_version_path(user, repo, version):
    assert user_exists(user) and exists(user, repo)

    if version == '&newest':
        repo_info = get_repo_info(user, repo)
        newest = repo_info['last-version']

        return newest, f'repos/{user}/{repo}/{newest}'

    return version, f'repos/{user}/{repo}/{version}'


def _get_tar_version(user, repo, version):
    version, dest_path = _get_version_path(user, repo, version)

    # I will remove this code later, when on upload, tar archive will create automatically
    if version + '.tar.gz' not in os.listdir(f'repos/{user}/{repo}'):
        tar.pack_dir(version, dest_path, f'repos/{user}/{repo}')

    return f'repos/{user}/{repo}/{version}.tar.gz'
