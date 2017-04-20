import shutil
import time
import logging

def run():
    i = 0
    with open('test.log', "ab+") as f:
        while True:
            i += 1
            f.write("{}\n".format(i))
            logging.info(i)
            time.sleep(10)
            if i == 5:
                f.flush()
                shutil.move('test.log', 'test_{}.log'.format(i))
                i = 0

if __name__ == "__main__":
    run()
