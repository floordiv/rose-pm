import os
import json
import hashlib


def parse_packages(packages):
    parsed = []

    for package in packages:
        if ':' not in package:
            author, package_name = 'floordiv', package   # by default, you are downloading packages from project's author
        else:
            author, package_name = package.split(':')

        parsed.append((author, package_name))

    return parsed


def isinstalled(dest_path, repo):
    return os.path.exists(dest_path) and repo in os.listdir(dest_path)


def load_version_info(repo_path):
    with open(repo_path + '/.version') as version_info:
        return json.load(version_info)


def getversion(dest_path, repo):
    repo_path = dest_path + '/' + repo
    assert isinstalled(dest_path, repo) and '.version' in os.listdir(repo_path)

    return load_version_info(repo_path)['version']


def getauthor(dest_path, repo):
    assert isinstalled(dest_path, repo)

    return load_version_info(dest_path + '/' + repo)['author']


def gethash(dest_path, repo):
    assert isinstalled(dest_path, repo)

    files = os.listdir(dest_path + '/' + repo)

    if files:
        # yes, I just copypasted this from server-side

        hashes = {}

        for file in files:
            with open(file, 'rb') as file_source:
                hashes[file] = hashlib.sha256(bytes(file_source)).hexdigest()

        total_hash = hashlib.sha256(bytes(''.join(hashes.values()).encode())).hexdigest()

        return hashes, total_hash
