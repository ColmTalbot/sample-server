import h5py
import numpy as np

YEAR = 365.25 * 24 * 60 * 60


def load_injections(
    filename: str,
    variables: list[str],
    n_samples: int,
    ifar_threshold: float = 1,
    seed: int | None = None,
):
    output = dict(model="injections")
    output["metadata"] = dict(filename=filename.name)
    with h5py.File(filename, "r") as ff:
        if "injections" not in ff:
            raise KeyError("Injections not found in file.")
        
        data = ff["injections"]

        output["metadata"]["analysis_time"] = float(data.attrs["analysis_time_s"] / YEAR)
        output["metadata"]["total_generated"] = float(data.attrs["total_generated"])

        keep = np.zeros(len(data["sampling_pdf"]), dtype=bool)
        for key in data:
            if "ifar" in key:
                keep |= data[key][()] > ifar_threshold

        total_n_samples = sum(keep)
        output["metadata"]["n_found"] = int(total_n_samples)
        if n_samples > total_n_samples:
            raise ValueError(
                f"Insufficient found injections available in {filename}. "
                f"{n_samples} requested and {total_n_samples} available."
            )
        elif n_samples == -1:
            idxs = np.arange(len(keep))[keep]
        else:
            rng = np.random.default_rng(seed)
            idxs = rng.choice(np.where(keep)[0], n_samples, replace=False)
            idxs = np.sort(idxs)

        output["idxs"] = idxs.tolist()
        output["samples"] = dict()
        for variable in variables:
            try:
                output["samples"][variable] = data[variable][()][idxs].tolist()
            except ValueError:
                raise KeyError(
                    f"Variable {variable} not found in the injections. "
                    f"Available variables are: {data.keys()}"
                )
    return output
