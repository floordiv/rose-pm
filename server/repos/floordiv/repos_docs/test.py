import hashlib
with open('anyversion2.tar.gz', 'rb') as test:
    print(hashlib.sha256(test.read()).hexdigest())
