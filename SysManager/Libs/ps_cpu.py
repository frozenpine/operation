# -*- coding: UTF-8 -*-
import powershell

def run(client, module):
    '''
    mod = {
        'ps_script': """\
$counters = new-object 'System.Diagnostics.PerformanceCounter[]' ([System.Environment]::ProcessorCount)
for($i=0; $i -lt $counters.Length; $i++){
    $counters[$i] = new-object System.Diagnostics.PerformanceCounter("Processor", "% Processor Time",$i)
}
for($i=0; $i -lt 2; $i++){
    $total = 0;
    for($j=0; $j -lt $counters.Length; $j++){
        $idle = 100 - $counters[$j].NextValue();
        if($idle -ne 100) {
            "cpu"+$j+":"+$idle;
            $total += $idle;
        }
    }
    if($total -gt 0){
        "all:" + $total/$counters.Length;
    }
    sleep(1)
}
        """
    }
    '''
    mod = {
        'ps': 'Get-WmiObject win32_processor | select LoadPercentage  |fl'
    }
    return powershell.run(client, mod)
