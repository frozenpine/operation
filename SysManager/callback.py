# -*- coding: UTF-8 -*-

class CallBack():
    def on_host_failed(self, result):
        print "Connect to host({}) timeout.".format(result.destination)

    def on_invalid_login(self, result):
        print "Either username or password is invalid."

    def on_exec_succeed(self, result):
        print "Execution[{}] on {} succeed.".format(result.module, result.destination)
        for line in result.lines:
            print line

    def on_exec_failed(self, result):
        print "Execution[{}] on {} failed with return code {}".format(
            result.module, result.destination, result.return_code
        )
        for line in result.lines:
            print line
