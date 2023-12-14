# Maxar Canonical Video

The canonical video format (canv for short) is a simple and straight-forward file format for the management of 
Full Motion Video attributed with camera medatadata for each image.

This Python package helps an integrator with the task of reading and/or creating canv videos.

The package both provides programmatic support and a CLI:

```console
$ python -m maxar_canv -h
usage: python -m canv [-h] [--validate-ims SOURCE_PATH]
                      [--validate-canv SOURCE_PATH] [--probe-canv SOURCE_PATH]
                      [--slice-canv SOURCE_PATH TARGET_PATH]
                      [--range FROM_FRAME TO_FRAME]
                      [--image-size WIDTH HEIGHT]

optional arguments:
  -h, --help            show this help message and exit
  --validate-ims SOURCE_PATH
                        Validate a standalone Ims-file
  --validate-canv SOURCE_PATH
                        Validate a Canv-file (and its linked Ims-file)
  --probe-canv SOURCE_PATH
                        Probe a Canv-file (and its linked Ims-file)
  --slice-canv SOURCE_PATH TARGET_PATH
                        Slice a Canv-file (and its linked Ims-file)
  --range FROM_FRAME TO_FRAME
                        The range of frames for slicing (optional)
  --image-size WIDTH HEIGHT
                        New image size for slicing (optional)
```

## Canonical Video File Format

The canonical format is using two name suffixes, .canv for video metadata and .ims for video imagery.
The file with the suffix .canv is the "master" file for a canonical video.

See the P3DR Integration Guide for further details.