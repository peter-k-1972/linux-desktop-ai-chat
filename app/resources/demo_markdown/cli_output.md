# CLI-Ausgabe

```
$ pytest tests/unit -q
..........                                                               [100%]
10 passed in 0.42s
```

```
ERROR: connection refused
  at WorkerThread.run (network.py:112)
  Caused by: ConnectionError: timed out
```

```
INFO  [docker] pulling image llama3:latest
WARN  [gpu] memory above 90%
```
