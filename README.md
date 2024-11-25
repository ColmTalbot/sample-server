# sample-server

A basic `FastAPI` API for serving posterior samples for gravitational-wave observations.
The setup assumes that there is a directly containing HDF5 files downloaded from zenodo [here](https://zenodo.org/records/5546663) and [here](https://zenodo.org/records/6513631) and released under CC Attribution by the LIGO Scientific Collaboration and Virgo Collaboration and KAGRA Collaboration.

The specifiable quantities are:

- event name, this currently must be the long-form GW name. A full listing of events can also be queried.
- parameters to read as stored in the `PESummary` files.
- the model, e.g., `C01:IMRPhenomXPHM`.
- the number of samples to read.
- a random seed for reproducibility of which samples are taken.

## Usage

A basic `Python` client to read the samples is below

```python
import requests
from functools import cache

import pandas as pd


class Client:

    _cache = dict()

    def __init__(self, host="https://gwsamples.duckdns.org"):
        self.host = host

    @classmethod
    def clear_cache(cls):
        cls._cache = dict()

    @cache
    def events(self):
        return requests.get(f"{self.host}/events").json()

    def samples(self, event, parameters, n_samples=-1, model="C01:IMRPhenomXPHM"):
        hash_ = f"{event}-{'&'.join(parameters)}-{n_samples}-{model}"
        if self._cache.get(hash_, None) is None:
            samples = self.get_samples(
                event=event,
                parameters=parameters,
                n_samples=n_samples,
                model=model,
            )
            self._cache[hash_] = samples
        return self._cache[hash_]

    def get_samples(self, event, parameters, n_samples=-1, model="C01:IMRPhenomXPHM"):
        var = "&".join([f"variable={par}" for par in parameters])
        request = f"{self.host}/events/{event}/?n_samples={n_samples}&{var}"
        result = requests.get(request, verify=True)
        if result.status_code == 502:
            # retry on timeout error
            result = requests.get(request, verify=True)

        if result.status_code != 200:
            print(result.content, event)
            return None
        data = result.json()
        posteriors = pd.DataFrame(data["samples"], index=data["idxs"])
        return posteriors
```

with example usage

```python
In [1]: from client import Client
client
In [2]: client = Client()

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
