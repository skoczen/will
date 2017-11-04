# Encryption Backends

## Overview
Encryption backends are what lets Will keep his thoughts private - safe from prying eyes, and would-be spies.

All of Will's short and long-term memory (`pubsub` and `storage`) are encrypted by default.

Will supports the following options for storage backend, and improvements and more backends are welcome:

- AES (`will.backends.storage.aes`) - uses AES in CBC mode to encrypt.
## Choosing a backend

Right now, your only option is AES.  So go with that! :)

## Setting your backend

To set your backend, in `config.py`, set:

```python
# Turn on/off encryption in pub/sub and storage (default is on).
# Causes a small speed bump, but secures messages in an untrusted environment.
# ENABLE_INTERNAL_ENCRYPTION = True
ENCRYPTION_BACKEND = "aes"
```

## Contributing a new backend

Writing a new encryption backend is easy (if you've got the encryption stuff sorted.) Just subclass `BaseStorageBackend`, and implement:

1. `encrypt_to_b64` - a method that take an arbitary python object, and returns an encrypted, base64 string.
2. `decrypt_from_b64` - a method that takes that base64 string, and returns a python object.
3. Provide a `bootstrap()` method that returns an instantiated EncryptionClass.

Here's an example: 

```python
from will.backends.storage.base import BaseStorageBackend


class MyGreatEncryption(WillBaseEncryptionBackend):

    @classmethod
    def encrypt_to_b64(cls, raw):
        return binascii.b2a_base64(my_encryption_method(pickle.dumps(raw, -1)))

    @classmethod
    def decrypt_from_b64(cls, raw_enc):
        return pickle_loads(binascii.a2b_base64(my_decryption_method(raw_enc)))

def bootstrap(settings):
    return MyGreatEncryption(settings)


```

From there, just test it out, and when you're ready, submit a [pull request!](https://github.com/skoczen/will/pulls)

That's Will's brain, end-to-end.  If you haven't already, dig into how to get him [deployed](/deploy.md)!