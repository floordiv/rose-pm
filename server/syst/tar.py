import os
import shutil
import tarfile


def pack_dir(dirname):
    arc_name = 'tmp/' + os.path.basename(dirname) + '.tar.gz'

    try:
        tar = tarfile.open(arc_name, 'x:gz')
        tar.add(dirname)
        tar.close()
    except FileExistsError:
        os.remove(arc_name)
        return pack_dir(dirname)

    return arc_name


def unpack_dir(name, to_dir, author, repo_name, version):
    if not os.path.exists(to_dir):
        os.mkdir(to_dir)

    tar = tarfile.open(name)
    tar.extractall(to_dir)

    if not os.path.exists(to_dir + '/' + repo_name):
        os.mkdir(to_dir + '/' + repo_name)

    shutil.move(f'{to_dir}/repos/{author}/{repo_name}/{version}', to_dir)
    os.rename(to_dir + '/' + version, to_dir + '/' + repo_name)
    shutil.rmtree(to_dir + '/repos')
