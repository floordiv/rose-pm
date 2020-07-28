import os
import shutil
import tarfile
from traceback import format_exc


def pack_dir(name, dirname, dist):
    arc_name = os.path.join(dist, name) + '.tar.gz'

    try:
        print(arc_name, os.getcwd())
        tar = tarfile.open(arc_name, 'x:gz')
        print(2)
        tar.add(dirname)
        print(3)
        tar.close()
        print('ok.')
    except FileExistsError:
        pass

    print('ahahah')

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
