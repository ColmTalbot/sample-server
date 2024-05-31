import re
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

from load_event_samples import load_samples, find_variables

app = FastAPI()

app.add_middleware(GZipMiddleware, minimum_size=1000)

result_dir = Path("/home/sample-user/samples")


class SampleDict(BaseModel):
    model: str
    idxs: list[int]
    samples: dict[str, list[float]]


EVENTS = [
    re.findall(r"GW[\d]{6}_[\d]+", str(fname))[0]
    for fname in result_dir.iterdir() if "GW" in str(fname)
]
EVENTS.sort()
FILENAMES = {
    str(re.findall(r"GW[\d]{6}_[\d]+", str(fname))[0]): fname
    for fname in result_dir.iterdir() if "GW" in str(fname)
}


@app.get("/events")
async def list_events(request: Request) -> list[str]:
    return EVENTS


@app.get("/events/{event}/")
async def read_samples(
    request: Request,
    event: str,
    variable: Annotated[list[str] | None, Query()] = None,
    n_samples: int = -1,
    model: str = "C01:IMRPhenomXPHM",
    seed: int | None = None,
) -> SampleDict | list[str]:
    filename = FILENAMES.get(event, None)

    if filename is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Sample file {filename} for {event} not found. "
                f"Available values are {', '.join(EVENTS)}. "
                f"{FILENAMES}",
            ),
        )

    if variable is None:
        return find_variables(filename, model)

    return await _read_samples(
        filename=filename,
        model=model,
        variables=variable,
        n_samples=n_samples,
        seed=seed,
    )


async def _read_samples(
    filename: Path | None,
    variables: list[str],
    n_samples: int = -1,
    model: str = "C01:IMRPhenomXPHM",
    seed: int | None = None,
):
    if filename is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown file {filename}: {', '.join(FILENAMES.keys())}",
        )
    try:
        data = await load_samples(
            filename=filename,
            model=model,
            variables=variables,
            n_samples=n_samples,
            seed=seed,
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e).strip('"'))

    return data


