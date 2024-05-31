import re
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

from load_event_samples import load_samples, find_variables

app = FastAPI()

app.add_middleware(GZipMiddleware, minimum_size=1000)


class SampleDict(BaseModel):
    model: str
    idxs: list[int]
    samples: dict[str, list[float]]


SAMPLEDIR = Path("/home/sample-user/samples")
EVENT_FILENAMES = dict()
for sample_set in (SAMPLEDIR / "events").iterdir():
    if not sample_set.is_dir():
        continue
    for fname in sample_set.iterdir():
        name = re.findall(r"GW[\d]{6}_[\d]+", str(fname))[0]
        EVENT_FILENAMES[name] = fname
EVENTS = list(EVENT_FILENAMES.keys())
EVENTS.sort()
INJECTION_FILENAMES = dict()
for sample_set in (SAMPLEDIR / "injections").iterdir():
    if not sample_set.is_dir():
        continue
    for fname in sample_set.iterdir():
        name = fname.name.split("-")[0]
        INJECTION_FILENAMES[name] = fname
INJECTION_FILES = list(INJECTION_FILENAMES.keys())
INJECTION_FILES.sort()


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
    filename = EVENT_FILENAMES.get(event, None)

    if filename is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Sample file {filename} for {event} not found. "
                f"Available values are {', '.join(EVENTS)}. "
                f"{EVENT_FILENAMES}",
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
            detail=f"Unknown file {filename}: {', '.join(EVENT_FILENAMES.keys())}",
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


@app.get("/injections")
async def list_events(request: Request) -> list[str]:
    return INJECTION_FILES
