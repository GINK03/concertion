import codecs
import base64
import pickle
def pickle_base64_stringify(obj):
    return codecs.encode(pickle.dumps(obj), "base64").decode().strip()

def string_base64_pickle(obj):
    return pickle.loads(codecs.decode(obj.encode(), "base64"))


if __name__ == '__main__':
    code = pickle_base64_stringify({'i love':'mao'})
    recover = string_base64_pickle(code)
    assert recover == {'i love':'mao'}, "エンコード・デコードがうまく行っていません" 
    print(code)
    print(recover)
