# -*- coding: UTF-8 -*-
import shell

def run(client, module):
    mod = {
        'shell': """
            df | grep "%" | 
            grep -iv tmpfs | 
            awk 'BEGIN{
                printf("%s %s %s %s %s\\n","Path","Total","Used","Available","Use%")
            }
            FNR==1{next}
            {
                printf("%s %s %s %s %s\\n",$NF,$(NF-4),$(NF-3),$(NF-2),$(NF-1))
            }' | column -t
        """
    }
    return shell.run(client, mod)
