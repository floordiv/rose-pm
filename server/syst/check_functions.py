import syst.repo as repo

from traceback import format_exc


def repo_functions():
    try:
        repo.get_users()
        repo.user_exists('floordiv')
        repo.exists('floordiv', 'repos_docs')
        repo.version_exists('floordiv', 'repos_docs', 'anyversion1')
        repo.get_repos('floordiv')
        repo.get_versions('floordiv', 'repos_docs')
        repo.get_version('floordiv', 'repos_docs', 'anyversion2')
        repo.gethash('floordiv', 'repos_docs', 'anyversion2')

        return True
    except:
        return format_exc()
