# -*- coding: UTF-8 -*-
import powershell


def run(client, module):
    mod = {
        'ps': 'Get-WmiObject win32_processor | select LoadPercentage |fl'
    }
    return powershell.run(client, mod)
