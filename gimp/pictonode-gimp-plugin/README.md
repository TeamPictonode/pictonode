# pictonode-gimp-plugin

This directory contains the GIMP plugin for pictonode. Unlike the rest of this project, it is built using C++ and the GIMP C API. It is intended to provide an interface to GIMP that allows one to run serialized image pipelines. It provides two separate interfaces:

- One that has a user interface that allows one to select a pipeline or build a pipeline that runs on the current layer/image.
- One that just runs a loaded pipeline on the current layer/image.

## Depends On

External: libgimp2.0

## Building

This code uses CMake as a build process. First, install CMake and the latest `libgimp2.0-dev`, and then run:

```
$ mkdir build
$ cd build
$ cmake ..
$ make
```
