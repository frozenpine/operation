# -*- coding: UTF-8 -*-
from paramiko import SSHClient

def run(client, module):
    dest = module.get('customLog')
    key_words = module.get('key_words')
    if key_words:
        if isinstance(key_words, dict):
            key_words = '|'.join(key_words.values())
        elif isinstance(key_words, list):
            key_words = '|'.join(key_words)
        else:
            raise Exception("Invalid module define.")
    else:
        raise Exception("Invalid module define.")
    if isinstance(client, SSHClient):
        import grep
    else:
        import wingrep as grep
    mod = {
        'grep': dest,
        'args': {
            'pattern': key_words
        }
    }
    return grep.run(client, mod)
