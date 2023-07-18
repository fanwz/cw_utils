import redis
import json
import threading
import time
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode, urlsafe_b64decode


def generate_key():
    # generate by chatgpt-4
    # generate Fernet key
    return Fernet.generate_key()

def encrypt_str_data(str_data, key):
    # generate by chatgpt-4
    # encrypt string data
    f = Fernet(key)
    str_bytes = str_data.encode("utf-8")
    encrypted_str = f.encrypt(str_bytes)
    return encrypted_str

def decrypt_str_data(encrypted_str, key):
    # generate by chatgpt-4
    # decrypt string data
    f = Fernet(key)
    decrypted_str_bytes = f.decrypt(encrypted_str)
    decrypted_str = decrypted_str_bytes.decode("utf-8")
    return decrypted_str

def encrypt_json_data(json_data, key):
    # generate by chatgpt-4
    # encrypt json data,also string
    f = Fernet(key)
    json_str = json.dumps(json_data)
    json_bytes = json_str.encode("utf-8")
    encrypted_json = f.encrypt(json_bytes)
    return encrypted_json


def decrypt_json_data(encrypted_json, key):
    # generate by chatgpt-4
    # decrypt data
    f = Fernet(key)
    # encrypted_json must be bytes not str!!!
    decrypted_json_bytes = f.decrypt(encrypted_json)
    decrypted_json_str = decrypted_json_bytes.decode("utf-8")
    decrypted_json_data = json.loads(decrypted_json_str)
    return decrypted_json_data


class RedisApi():
    '''
    {
        "host": "127.0.0.1",
        "port": 7777,
        "user": "test_rw",
        "psw": "test123",
        "db": 0,
        "channel": "test_chn"
    }
    '''

    def __init__(self, config: dict) -> None:
        # decode_responses=self.encrypt the Fernet en de should input bytes!
        self.s = redis.Redis(host=config["host"],
                             port=config["port"],
                             username=config['user'],
                             password=config['password'],
                             db=0)

    def check_connection(self):
        try:
            return self.s.ping()
        except redis.ConnectionError:
            return False

    def publish_data(self, channel, data):
        ret = self.s.publish(channel, data)
        if ret > 0:
            print("publish {} client success!".format(ret))
        else:
            print("publish fail!")

    def subscribe(self, channel, callback, sleep=0.001):
        pubsub = self.s.pubsub()
        pubsub.subscribe(
            **{channel: lambda message: callback(message["data"])})

        def run_pubsub(pubsub_instance):
            pubsub_instance.run_in_thread(sleep_time=sleep)

        pubsub_thread = threading.Thread(target=run_pubsub, args=(pubsub,))
        pubsub_thread.start()

    def subscribe(self, channel, callback, stop_event, sleep=0.001):
        pubsub = self.s.pubsub()
        pubsub.subscribe(
            **{channel: lambda message: callback(message["data"])})

        def run_pubsub(pubsub_instance):
            while not stop_event.is_set():
                message = pubsub_instance.get_message()
                if message:
                    callback(message['data'])
                time.sleep(sleep)

        pubsub_thread = threading.Thread(target=run_pubsub, args=(pubsub,))
        pubsub_thread.daemon = True
        pubsub_thread.start()

    def subscribe_decorator(self, channel):
        def decorator(f):
            def wrapper(*args, **kwargs):
                self.subscribe(channel, f)
            return wrapper
        return decorator

    def update_hashtable(self, hash, key, value):
        ret = self.s.hset(hash, key, value)
        if ret != 1 and ret != 0:
            print("update hashtable error!ret={},hash={},key={},value={}".format(
                ret, hash, key, value))

    def get_from_hashtable(self, hash, *keys):
        if len(keys) == 1:
            return self.s.hget(hash, keys[0])
        elif len(keys) > 1:
            return self.s.hmget(hash, *keys)
        else:
            return self.s.hgetall(hash)

    def get_hash_keys(self, hash):
        return self.s.hkeys(hash)

    def delete_hashtable(self, hash):
        ret = self.s.delete(hash)
        if ret != 1:
            print("delete hash fail!ret={},hash={}".format(ret, hash))

    def delete_from_hashtable(self, hash, *keys):
        if len(keys) == 1:
            ret = self.s.hdel(hash, keys[0])
        elif len(keys) > 1:
            ret = self.s.hdel(hash, *keys)
        else:
            ret = self.s.delete(hash)

        if ret == 0:
            print("nothing delete.hash={},keys={}".format(hash, keys))

    def polling_hashtable(self, hashtable, callback, stop_event, sleep=1):
        def run_polling(api, hashtable):
            while not stop_event.is_set():
                try:
                    message = api.get_from_hashtable(hashtable)
                    if message:
                        callback(message, True)
                except Exception as e:
                    msg = "redis get hashtable fail!({})".format(e)
                    callback({"msg": msg, "ts": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime())}, False)
                time.sleep(sleep)

        polling_thread = threading.Thread(
            target=run_polling, args=(self, hashtable,))
        polling_thread.daemon = True
        polling_thread.start()


if __name__ == "__main__":
    print(generate_key())
