# -*- coding: UTF-8 -*-
import shell


def run(client, module):
    mod = {
        'shell': """
            mpstat -P ALL 1 2 | grep "Average" | 
            awk '{
                for(i=2;i<NF;i++)
                    printf("%s ", $i);
                print $NF
            }' | column -t
        """
    }
    return shell.run(client, mod)
