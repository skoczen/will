import logging
import os
import time

from will.utils import sizeof_fmt
from .base import BaseStorageBackend


class FileStorageException():
    """
    A condition that should not occur happened in the FileStorage module
    """
    pass


class FileStorage(BaseStorageBackend):
    required_settings = [
        {
            "name": "FILE_DIR",
            "obtain_at": """You must supply a FILE_DIR setting that is a path to a directory.

Examples:

 * /var/run/will/settings/
 * ~will/settings/""",
        },
    ]

    """
    A storage backend using a local filesystem directory.

    Each setting is its own file.

    You must supply a FILE_DIR setting that is a path to a directory.

    Examples:

     * /var/run/will/settings/
     * ~will/settings/
    """
    def __init__(self, settings):
        self.verify_settings(quiet=True)
        self.dirname = os.path.abspath(os.path.expanduser(settings.FILE_DIR))
        self.dotfile = os.path.join(self.dirname, ".will_settings")
        logging.debug("Using %s for local setting storage", self.dirname)

        if not os.path.exists(self.dirname):
            # the directory doesn't exist, try to create it
            os.makedirs(self.dirname, mode=0o700)
        elif not os.path.exists(self.dotfile):
            # the directory exists, but doesn't have our dot file in it
            # if it has any other files in it then we bail out since we want to
            # have full control over wiping out the contents of the directory
            if len(self._all_setting_files()) > 0:
                raise FileStorageException("%s is not empty, "
                                           "will needs an empty directory for "
                                           "settings" % (self.dirname,))

        # update our dir & dotfile
        os.chmod(self.dirname, 0o700)
        with open(self.dotfile, 'a'):
            os.utime(self.dotfile, None)

    def _all_setting_files(self):
        return [
            os.path.join(self.dirname, f)
            for f in os.listdir(self.dirname)
            if os.path.isfile(os.path.join(self.dirname, f))
        ]

    def _key_paths(self, key):
        key_path = os.path.join(self.dirname, key)
        expire_path = os.path.join(self.dirname, '.' + key + '.expires')
        return key_path, expire_path

    def do_save(self, key, value, expire=None):
        key_path, expire_path = self._key_paths(key)
        with open(key_path, 'w') as f:
            f.write(value)

        if expire is not None:
            with open(expire_path, 'w') as f:
                f.write(str(int(time.time() + expire)))
        elif os.path.exists(expire_path):
            os.unlink(expire_path)

    def clear(self, key):
        key_path, expire_path = self._key_paths(key)
        if os.path.exists(key_path):
            os.unlink(key_path)
        if os.path.exists(expire_path):
            os.unlink(expire_path)

    def clear_all_keys(self):
        for filename in self._all_setting_files():
            os.unlink(filename)

    def do_load(self, key):
        key_path, expire_path = self._key_paths(key)

        if os.path.exists(expire_path):
            with open(expire_path, 'r') as f:
                expire_at = f.read()
            if time.time() > int(expire_at):
                # the current value has expired
                self.clear(key)
                return

        if os.path.exists(key_path):
            with open(key_path, 'r') as f:
                return f.read()

    def size(self):
        return sizeof_fmt(sum([
            os.path.getsize(filename)
            for filename in self._all_setting_files()
        ]))


def bootstrap(settings):
    return FileStorage(settings)
