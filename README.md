# sample-server

A basic `FastAPI` API for serving posterior samples for gravitational-wave observations.
The setup assumes that there is a directly containing HDF5 files downloaded from zenodo [here](https://zenodo.org/records/5546663) and [here](https://zenodo.org/records/6513631) and released under CC Attribution by the LIGO Scientific Collaboration and Virgo Collaboration and KAGRA Collaboration.

The specifiable quantities are:

- event name, this currently must be the long-form GW name. A full listing of events can also be queried.
- parameters to read as stored in the `PESummary` files.
- the model, e.g., `C01:IMRPhenomXPHM`.
- the number of samples to read.
- a random seed for reproducibility of which samples are taken.

## Deployment

The container builds directly in the GitHub CI and can be deployed from there an example deployment is

```console
$ docker run -it --rm --env-file .env.prod -p 8080:8000 --platform=linux/amd64 -v {EVENT_SAMPLE_DIRECTORY}:/events -v {INJECTION_DIRECTORY}:/injections ghcr.io/colmtalbot/sample-server:latest
```

### Environment specification

An example development configuration is

```
APP_MODULE=main:app
WORKERS=1
BIND=0.0.0.0:8000
TIMEOUT=60
LOG_LEVEL=debug
ACCESS_LOG=-
ERROR_LOG=-
```

and to deploy with Nginx

```
APP_MODULE=main:app
WORKERS=4
BIND=unix:/tmp/gunicorn.sock
TIMEOUT=60
LOG_LEVEL=error
ACCESS_LOG=/var/log/gunicorn-access.log
ERROR_LOG=/var/log/gunicorn-error.log
```

This also requires mounting the `/tmp` and `/var/log` directories.

### Building container locally

```console
$ docker build --tag sample-server:latest
```

### Finding data

The data files need to be stored locally on the machine running the server and can be downloaded from zenodo as described above.
The files should be in the following format

```
{EVENT_SAMPLE_DIRECTORY}/
├── GWTC-2.1/
│   ├── datafile_{GWYYMMDD_SUBDAY}_otherinfo_.h5
│   ├── datafile_{GWYYMMDD_SUBDAY}_otherinfo_.h5
│   └── ...
├── GWTC-3/
│   ├── datafile_{GWYYMMDD_SUBDAY}_otherinfo_.h5
│   ├── datafile_{GWYYMMDD_SUBDAY}_otherinfo_.h5
│   └── ...
├── OGC-3/
│   ├── datafile_{GWYYMMDD_SUBDAY}_otherinfo_.h5
│   ├── datafile_{GWYYMMDD_SUBDAY}_otherinfo_.h5
│   └── ...
└── ...

{INJECTION_DIRECTORY}/
├── LVK-O3-injections/
│   ├── {LABEL}-otherinfo.hdf5
│   ├── {LABEL}-otherinfo.hdf5
│   └── ...
├── LVK-O4-injections/
│   ├── {LABEL}-otherinfo.hdf5
│   ├── {LABEL}-otherinfo.hdf5
│   └── ...
└── ...
```

The important features are:
- the files must be two levels down from the specified directories.
- the full GW name for events.
- the dataset label (followed by hyphen) in the injection sets.

## Usage

While samples can be queried using raw HTTP requests, the recommended method is via the companion Python library [`gwsamplefind`](github.com/ColmTalbot/gwsamplefind) with example usage

```python
In [1]: from gwsamplefind.gwsamplefind import Client
client
In [2]: client = Client("https://gwsamples.duckdns.org")

In [3]: client.events()[:3]
Out[3]: ['GW150914_095045', 'GW190403_051519', 'GW191204_171526']

In [4]: client.samples("GW190403_051519", ["mass_1_source", "mass_2_source"], 10)
Out[4]: 
      mass_1_source  mass_2_source
9044      90.116100      15.778448
8764     101.865908      14.861801
3839     102.162218      13.492650
3913     107.222567      11.312127
801      112.729088      14.255726
6711     107.521088      20.129922
1471      83.982683      17.721773
4016      88.207093      26.552301
7884     110.588766      15.175171
1039      86.934782      10.078412
```
