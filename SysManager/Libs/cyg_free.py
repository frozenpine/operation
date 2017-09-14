# -*- coding: UTF-8 -*-
import shell


def run(client, module):
    mod = {
        'shell': """
            lines=`free | wc -l`;
            if [ ${lines} -ne 4 ]; then
                free | 
                awk '
                    BEGIN{print "Name Total Free"}
                    FNR==2 || FNR==3{
                        gsub(":","",$1);
                        print tolower($1)" "$2" "$NF
                    }' | column -t;
            else
                free | 
                awk '
                    BEGIN{print "Name Total Free"}
                    FNR==2 || FNR==4{
                        gsub(":","",$1);
                        print tolower($1)," "$2" "$NF+$(NF-1)+$(NF-3)
                    }' | column -t;
            fi
        """
    }
    return shell.run(client, mod)
