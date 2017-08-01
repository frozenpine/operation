# -*- coding: UTF-8 -*-
import re


def CheckPrivilege(user, uri, method):
    match_pri = None
    for role in user.roles:
        for pri in role.privileges:
            if re.match(pri.uri, uri) and \
                    pri.HasMethod(method):
                if match_pri:
                    if len(pri.uri) >= len(match_pri.uri):
                        match_pri = pri
                else:
                    match_pri = pri
    return match_pri != None
