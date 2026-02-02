#!/usr/bin/env python3
import argparse

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
    help="Output .db file name",
)

args = parser.parse_args()

InputFile: str = args.InputFile
OutputFile: str = args.OutputFile

pl.read_parquet(InputFile).write_database(
    "samples", f"sqlite:///{OutputFile}", if_table_exists="replace"
)
