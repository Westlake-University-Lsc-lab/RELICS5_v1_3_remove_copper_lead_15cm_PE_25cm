import argparse
import logging

import numpy as np
import polars as pl
from dtypes import flux_dtype, set_nan_defaults
from ROOT import TFile

logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser(description="Combine information of flux together")

parser.add_argument(
    "--InputFile",
    dest="InputFile",
    action="store",
    required=True,
    help="Input Geant4 ROOT file",
)

parser.add_argument(
    "--OutputFile",
    dest="OutputFile",
    action="store",
    required=True,
    help="Output .parquet file name",
)

args = parser.parse_args()

InputFile: str = args.InputFile
OutputFile: str = args.OutputFile

# Load input ROOT file

Infile = TFile(InputFile)
tree = Infile.Get("mcTree_flux")

eventN = int(tree.GetEntries())

logging.info(f"Loading: {InputFile}")
logging.info(f"Total event number = {eventN}")

totalTracks = 0
for i in range(eventN):
    tree.GetEntry(i)
    totalTracks += int(tree.nTracks)

flux = np.zeros(totalTracks, dtype=flux_dtype)
set_nan_defaults(flux)

fstart = 0
fend = 0
for i in range(eventN):
    tree.GetEntry(i)
    fend = fstart + int(tree.nTracks)
    flux[fstart:fend]["trackEnergy"] = list(tree.trackEnergy)
    flux[fstart:fend]["trackName"] = [str(s) for s in list(tree.trackName)]
    flux[fstart:fend]["trackParent"] = [str(s) for s in list(tree.trackParent)]
    flux[fstart:fend]["px"] = list(tree.px)
    flux[fstart:fend]["py"] = list(tree.py)
    flux[fstart:fend]["pz"] = list(tree.pz)
    flux[fstart:fend]["trackTime"] = list(tree.trackTime)
    flux[fstart:fend]["trackX"] = list(tree.trackX)
    flux[fstart:fend]["trackY"] = list(tree.trackY)
    flux[fstart:fend]["trackZ"] = list(tree.trackZ)
    fstart = fend
    if (i + 1) % 1000 == 0:
        logging.info(f"event {i + 1}/{eventN} processed.")

mm = 1.0
cm = 10 * mm

width_x = 200 * cm
width_y = 200 * cm
width_z = 250 * cm
thickness = 10 * cm

df = pl.from_numpy(
    flux, schema_overrides={"trackName": pl.String, "trackParent": pl.String}
)
df = df.filter(
    (df["trackX"] < -(width_x - thickness) / 2)
    | (df["trackX"] > (width_x - thickness) / 2)
    | (df["trackY"] < -(width_y - thickness) / 2)
    | (df["trackY"] > (width_y - thickness) / 2)
    | (df["trackZ"] < -(width_z - thickness) / 2)
    | (df["trackZ"] > (width_z - thickness) / 2)
)
logging.info(f"Effective flux track number = {len(df)}/{totalTracks}")

df.write_parquet(OutputFile, compression="gzip")

logging.info(f"Saving: {OutputFile}")
