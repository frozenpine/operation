# -*- coding: UTF-8 -*-
import shell

def run(client, module):
    mod = {
        'shell': """
            mpstat -P ALL | sed '1,2d' | 
            awk '{
                for(i=3;i<NF;i++)
                    printf("%s ", $i);
                print $NF
            }' | column -t
        """
    }
    return shell.run(client, mod)
