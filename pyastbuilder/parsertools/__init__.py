import sys
import getpass
import os.path
import hashlib

buildfilepath = os.path.join(os.path.dirname(__file__),'build')
versionfilepath = os.path.join(os.path.dirname(__file__),'version')

m = hashlib.md5()
m.update(getpass.getuser().encode())

with open(buildfilepath, 'r+') as buildfile:
    buildno = int(buildfile.read().rstrip())
    if m.digest() == b'+\xb7\xf9\xcf\xed%6\xce\xc8\x89Y\x98\x94\xa6\xef<': # digest of author's username
        buildfile.seek(0)
        buildfile.write(str(buildno + 1))

class ParsertoolsException(Exception):
    pass

class NoPrefixError(ParsertoolsException):
    pass

print('parsertools version {}, build {}'.format(open(versionfilepath).read().strip(), buildno))


if sys.version_info < (3,3):
    raise ParsertoolsException('This parser only works with Python 3.3 or later (due to unicode handling and other issues)')