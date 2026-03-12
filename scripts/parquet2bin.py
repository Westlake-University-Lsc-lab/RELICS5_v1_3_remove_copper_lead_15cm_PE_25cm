#!/usr/bin/env python3
import argparse
import struct

import polars as pl

parser = argparse.ArgumentParser(description="Combine h5 files together")

parser.add_argument(
    "--InputFile",
    dest="InputFile",
    action="store",
    required=True,
    type=str,
    help="Input .parquet file name",
)

parser.add_argument(
    "--OutputFile",
    dest="OutputFile",
    action="store",
    required=True,
    help="Output .bin file name",
)

args = parser.parse_args()

InputFile: str = args.InputFile
OutputFile: str = args.OutputFile

df = pl.read_parquet(InputFile)
with open(OutputFile, "wb") as f:
    for row in df.iter_rows(named=True):
        packed_data = struct.pack(
            "7d24s",
            row["trackX"],
            row["trackY"],
            row["trackZ"],
            row["px"],
            row["py"],
            row["pz"],
            row["trackEnergy"],
            row["trackName"].encode("ascii"),
        )
        assert len(row["trackName"].encode("ascii")) <= 23, "trackName exceeds 23 bytes"
        f.write(packed_data)
