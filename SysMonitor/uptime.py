# coding=utf-8


def uptime():
    with open("/proc/uptime") as f:
        f_stream = f.read()
    result = f_stream.split(" ")[0]
    return result


if __name__ == "__main__":
    uptime()
