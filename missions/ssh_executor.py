import paramiko

def ssh2(ip, port, username, password, commands):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, username, password, timeout=5)
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            out = stdout.readlines()
            for o in out:
                print o,
        ssh.close()
    except:
        print "%s\tError\n" % ip

if __name__=='__main__':
    cmd = ['echo hello!']
    username = 'qdp'
    password = 'qdp'
    ssh2('192.168.101.152', 22, username, password, cmd)
