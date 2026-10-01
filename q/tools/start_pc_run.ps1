# Start the Route (C) local run (user request 2026-10-01: 4 threads max while gaming).
# sched.py with 4 slots + tracker loop, both pinned to logical CPUs 12-15 (mask 0xF000), BelowNormal priority.
# Child processes inherit the affinity mask and the BelowNormal class (sched.py also launches children with BELOW_NORMAL).
$lab = 'C:\Users\RESEARCHER\Desktop\c2_experimental'
$mask = [IntPtr]0xF000
$os = Get-CimInstance Win32_OperatingSystem
'RAM free {0:N1} GB of {1:N1} GB' -f ($os.FreePhysicalMemory / 1MB), ($os.TotalVisibleMemorySize / 1MB)

$already = Get-CimInstance Win32_Process -Filter "Name like 'python%'" | Where-Object { $_.CommandLine -match 'sched\.py' }
if ($already) { 'sched.py already running (PID ' + ($already.ProcessId -join ',') + '): not starting a second one'; exit 1 }

$s = Start-Process -FilePath "$lab\.venv\Scripts\python.exe" -ArgumentList 'scripts\sched.py', '4' -WorkingDirectory $lab -WindowStyle Hidden -PassThru
$s.ProcessorAffinity = $mask; $s.PriorityClass = 'BelowNormal'
$t = Start-Process -FilePath 'C:\Program Files\Git\bin\bash.exe' -ArgumentList 'scripts/tracker_loop.sh' -WorkingDirectory $lab -WindowStyle Hidden -PassThru
$t.ProcessorAffinity = $mask; $t.PriorityClass = 'BelowNormal'
'started sched.py PID {0} (affinity 0x{1:X}, {2}) and tracker_loop PID {3}' -f $s.Id, [int64]$s.ProcessorAffinity, $s.PriorityClass, $t.Id
