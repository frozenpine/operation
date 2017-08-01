# -*- coding: UTF-8 -*-
import re

import powershell


def run(client, module):
    dest = module.get('grep')
    args = module.get('args')
    param = ""
    if args:
        pattern = args.get('pattern')
        if not pattern or pattern == '':
            pattern = '.+'
        ignoreCase = args.get('ignore_case')
        if ignoreCase:
            if (isinstance(ignoreCase, str) and
                    re.match(r'[n|N](o)?|[F|f]alse', ignoreCase)) or \
                    (isinstance(ignoreCase, bool) and ignoreCase):
                param += " -CaseSensitive"
        revers = args.get('reverse_match')
        if revers:
            if (isinstance(revers, str) and
                    re.match(r'[y|Y](es)?|[T|t]rue', revers)) or \
                    (isinstance(revers, bool) and revers):
                param += " -NotMatch"
        mod = {
            'ps': """\
cat {} | select-string -Pattern "{}" {}\
            """.format(dest, pattern, param)
        }
        return powershell.run(client, mod)
