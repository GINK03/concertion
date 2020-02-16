from hashlib import sha224

def get_digest(x):
    if isinstance(x, str):
        return sha224(bytes(x, 'utf8')).hexdigest()[:24]
    elif isinstance(x, bytes):
        return sha224(x).hexdigest()[:24]
    else:
        raise Exception("Not Found Error")

