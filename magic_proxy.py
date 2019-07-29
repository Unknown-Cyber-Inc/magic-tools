import os
import sys
import json

from cythereal_cli.api_client import ApiClient, ApiException
from cythereal_cli.util.hashing import hash_path
from collections import namedtuple

MagicStatus = namedtuple("MagicStatus", "sha1 result message data")

class MAGIC (object):

    class MagicResult(MagicStatus):
        """ Internal class for storing result of uploading a single file.
        Attributes
        ----------
        sha1: str
        result: str
            One of: 'success' | 'error'
        message: str
            The message returned by the API.
        data: dict
        """
    def get_binary_genomics (self, sha1):
        magic_op = ApiClient().get_binary_genomics
        return self.magic_get(magic_op, sha1, {})

    def magic_get (self, magic_op, sha1, params):
        try:
            params = {}
            response = magic_op(sha1, **params)
        except ApiException as exc:
            # If we have a response, try and get the response's message.
            # Fall back onto the exception's stored reason if needed.
            message = None
            if exc.body and hasattr(exc.body, 'message'):
                message = exc.body.message
            message = message or exc.reason

            result = MagicStatus(sha1=sha1, result='error', message=message, data=None)
            return result

        # Get the status
        if response.code == 200:
            status = 'success'
        else:
            status = 'error'

        result = MagicStatus(sha1=sha1, result=status, message=response.message, data=response.data)
        return result

real_magic = MAGIC()

class MAGICProxy (object):
    def __init__(self, proxy_store="magic_cache", refresh=True):
        self.proxy_store = proxy_store

    def make_filepath (self, filename):
        return os.path.join(self.proxy_store, filename)

    def get_binary_genomics (self, binary_id):
        """Get genomics data of a binary"""
        filename = binary_id
        try:
            return self.fetch_from_cache(filename)
        except:
            print >>sys.stderr, "[%s]: Genomics not in cache" % binary_id; sys.stderr.flush()
            print >>sys.stderr, "[%s]: Fetching genomics from MAGIC" % binary_id; sys.stderr.flush()
            result = real_magic.get_binary_genomics (binary_id)
            self.update_cache (filename, result)
            return eval(str(result))

    def update_cache (self, filename, result):
        filepath = self.make_filepath (filename)
        dirname = os.path.dirname (filepath)
        if not os.path.exists (dirname):
            os.makedirs(dirname)

        fp = open (filepath, "w")
        fp.write (str(result))
        fp.close ()

    def fetch_from_cache (self, filename):
        filename = self.make_filepath (filename)
        fp = open(filename) 
        try:
            data = fp.read()
            result = eval(data)
        except:
            import traceback
            traceback.print_exc(file=sys.stderr)
            result = ast.literal_eval (data)
        fp.close()
        return result
