import os
import hashlib


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
        return [f'repos/{user}/{repo}/{version}/{file}' for file in os.listdir(f'repos/{user}/{repo}/{version }')]


def exists(user, repo):
    return repo in get_repos(user)


def version_exists(user, repo, version):
    return user_exists(user) and exists(user, repo) and version in get_versions(user, repo)


def user_exists(user):
    return user in get_users()


def gethash(user, repo, version):
    files = get_version(user, repo, version)

    if files:
        hashes = {}

        for file in files:
            with open(file, 'rb') as file_source:
                hashes[file] = hashlib.sha256(bytes(file_source)).hexdigest()

        total_hash = hashlib.sha256(bytes(''.join(hashes.values()).encode())).hexdigest()

        return hashes, total_hash

