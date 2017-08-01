# -*- coding: UTF-8 -*-
import powershell


def run(client, module):
    mod = {
        'ps': """\
gwmi win32_logicaldisk -filter "drivetype=3" | \
select-object DeviceID, @{Name="Size";Expression={$_.Size/1KB}}, @{Name="FreeSpace";Expression={$_.FreeSpace/1KB}} | \
format-table | out-string -stream | select-string -Pattern "^-|^$" -NotMatch
        """
    }
    return powershell.run(client, mod)
