# -*- coding: UTF-8 -*-
import shell
from SysManager import logging

def run(client, module):
    mod = {
        'shell': """
            cat /proc/uptime | 
            awk -F. '{{
                run_days=$1/86400;
                run_hour=($1%86400)/3600;
                run_minute=($1 % 3600)/60;
                run_second=$1%60;
                printf("%d Days %d hours %d minutes %d seconds",run_days,run_hour,run_minute,run_second)
            }}'
        """
    }
    return shell.run(client, mod)
