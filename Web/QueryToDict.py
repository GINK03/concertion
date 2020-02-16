
def query_to_dict(query):
    ret = {}
    for pair in query.split('&'):
        try:
            key, value = pair.split('=')
        except Exception as exc:
            print(exc)
            raise Exception(exc)
        ret[key] = value
    return ret
