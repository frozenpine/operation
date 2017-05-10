# -*- coding: UTF-8 -*-

def run(client, module):
    command = module.get('shell')
    args = module.get('args')
    if args and args.has_key('chdir'):
        base_dir = args.get('chdir')
        command = """
            export PATH=$PATH:.:/bin:/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin;
            cd "{}";{}
        """.format(base_dir, command)
    else:
        command = """
            export PATH=$PATH:.:/bin:/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin;
            {}
        """.format(command)
    #return client.exec_command(command)
    stdin, stdout, stderr = client.exec_command(command)
    stdout.read = change_read_encoding(stdout.read)
    stdout.readlines = change_readlines_encoding(stdout.read)
    stderr.read = change_read_encoding(stderr.read)
    stderr.readlines = change_readlines_encoding(stderr.read)
    return stdin, stdout, stderr

def change_read_encoding(func):
    def _read():
        encoding_list = ["gbk", "utf-8"]
        for each in encoding_list:
            try:
                return func().decode(each).encode('utf-8').replace('\r\n', '\n')
            except UnicodeDecodeError:
                pass
    return _read

def change_readlines_encoding(func):
    def _readlines():
        for line in func().split('\n'):
            if line != "":
                yield line
    return _readlines
