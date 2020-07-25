from time import time
from rcore import Session


session = Session()

begin = time()
print(session.request('get-version-hash', login='floordiv', repo='repos_docs', version='anyversion1'))
end = time()

print('Time went:', end - begin, 'secs')
