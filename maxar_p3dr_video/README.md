# Maxar P3DR Video

This Python package provides an integrator with a programmatic interface to the P3DR Video Server, and
a CLI for georegistration of Canonical Video (canv):

```console
$ python -m maxar_p3dr_video -h
usage: python -m maxar_p3dr_video [-h] -s SERVER -r REFERENCE [REFERENCE ...]
                                  -o OUTPUT DIRECTORY [-n OUTPUT NAME]
                                  [-l SEVERITY] [-f FRAMES IN FLIGHT]
                                  Canv-File

positional arguments:
  Canv-File             Maxar Canv-file for georegistration

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        TCP url or file path to video server
  -r REFERENCE [REFERENCE ...], --in-references REFERENCE [REFERENCE ...]
                        Reference dataset(s) for the georegistration
  -o OUTPUT DIRECTORY, --out-dir OUTPUT DIRECTORY
                        Directory where to put the registered Canv-file
  -n OUTPUT NAME, --out-name OUTPUT NAME
                        Name of registered Canv-file (if not set, it inherits
                        input name)
  -l SEVERITY, --log SEVERITY
                        Log severity for the video server {debug, info,
                        warning, error}
  -f FRAMES IN FLIGHT, --in-flight FRAMES IN FLIGHT
                        Threshold for the max number of simultaneous frames in
                        flight
```

