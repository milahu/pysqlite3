# opensubs

loop 130GB sqlite database opensubs.db

```
$(which time) -v mprof run --nopython $(which python) ./scripts/opensubs.py

Command being timed: "mprof run --nopython /nix/store/k66bpzvfzpdjq4np05k5xzn11mb002zf-python3-3.10.9-env/bin/python ./scripts/opensubs.py"
User time (seconds): 12261.33
System time (seconds): 1486.15
Percent of CPU this job got: 92%
Elapsed (wall clock) time (h:mm:ss or m:ss): 4:08:49
Average shared text size (kbytes): 0
Average unshared data size (kbytes): 0
Average stack size (kbytes): 0
Average total size (kbytes): 0
Maximum resident set size (kbytes): 56248
Average resident set size (kbytes): 0
Major (requiring I/O) page faults: 1192
Minor (reclaiming a frame) page faults: 1299215
Voluntary context switches: 221815
Involuntary context switches: 9172351
Swaps: 0
File system inputs: 258490544
File system outputs: 15824
Socket messages sent: 0
Socket messages received: 0
Signals delivered: 0
Page size (bytes): 4096
Exit status: 0
```

average memory usage per `mprof` is around 30MB

## python is slow

probably we are wasting lots of CPU time for unpacking structs in python

in C (or C++) (or Rust), we would allocate a struct, read the database file to memory, done.
C structs provide a "zero cost" structured view of memory.
in python, this would require native bindings, which partially defeats the purpose of python (avoid compilation).
