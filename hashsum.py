import hashlib

def _md5hash(string):
    m = hashlib.md5()
    m.update((string))
    return m.hexdigest()
