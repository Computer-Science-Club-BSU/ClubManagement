import os, sys
from base64 import b64decode, b64encode

def is_safe_path(basedir, path, follow_symlinks=True):
    base = os.path.abspath(basedir)
    # resolves symbolic links
    if follow_symlinks:
        matchpath = os.path.realpath(path)
    else:
        matchpath = os.path.abspath(path)
    return basedir == os.path.commonpath((base, matchpath))


def save_doc_attachment(token, file_data):
    with open(f'src/interface/uploads/{token}', 'wb') as f:
        f.write(b64decode(b64decode(file_data)))


def get_doc_attachment(token):
    with open(f'src/interface/uploads/{token}', 'rb') as f:
        return f.read()