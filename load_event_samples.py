import h5py
import numpy as np


def load_samples(
    filename: str,
    model: str,
    variables: list[str],
    n_samples: int,
    seed: int | None = None,
):
    output = dict()
    with h5py.File(filename, "r") as ff:
        if model not in ff:
            raise KeyError(
                f"Model {model} not present in {filename}. "
                f"Available models are {', '.join(ff.keys())}"
            )

        data = ff[model]["posterior_samples"]

        total_n_samples = len(data)
        if n_samples > total_n_samples:
            raise ValueError(
                f"Insufficient samples available for {model} in {filename}. "
                f"{n_samples} requested and {total_n_samples} available."
            )
        elif n_samples == -1:
            idxs = np.arange(total_n_samples)
        else:
            rng = np.random.default_rng(seed)
            idxs = rng.choice(total_n_samples, n_samples, replace=False)

        output["idxs"] = list(idxs)
        output["samples"] = dict()
        for variable in variables:
            try:
                output["samples"][variable] = list(data[variable][()][idxs])
            except ValueError:
                raise KeyError(
                    f"Variable {variable} not found in the posterior samples. "
                    f"Available variables are: {data.dtype}"
                )
    output["model"] = model
    output["metadata"] = dict(filename=filename.name)
    return output


def find_variables(filename, model):
    with h5py.File(filename, "r") as ff:
        if hasattr(ff[model], "posterior_samples"):
            data = ff[model]["posterior_samples"]
            return data.dtype.names
        else:
            data = ff[model]
            return list(data.keys())
        
