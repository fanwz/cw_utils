import redis
import json
import threading
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode, urlsafe_b64decode


def generate_key():
    # generate by chatgpt-4
    # generate Fernet key
    return Fernet.generate_key()


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

    def publish_data(self, channel, data):
        ret = self.s.publish(channel, data)
        if ret > 0:
            print("publish {} client success!".format(ret))
        else:
            print("publish fail!")

    def subscribe(self, channel, callback):
        pubsub = self.s.pubsub()
        pubsub.subscribe(
            **{channel: lambda message: callback(message["data"])})

        def run_pubsub(pubsub_instance):
            pubsub_instance.run_in_thread(sleep_time=0.001)

        pubsub_thread = threading.Thread(target=run_pubsub, args=(pubsub,))
        pubsub_thread.start()

    def subscribe_decorator(self, channel):
        def decorator(f):
            def wrapper(*args, **kwargs):
                self.subscribe(channel, f)
            return wrapper
        return decorator


if __name__ == "__main__":
    print(generate_key())
