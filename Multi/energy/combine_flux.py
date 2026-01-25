import argparse
import logging

import h5py
import numpy as np
from dtypes import flux_dtype, set_nan_defaults
from ROOT import TFile  # pyright: ignore[reportAttributeAccessIssue]

logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser(description="Combine information of flux together")

parser.add_argument(
    "--InputFiles",
    dest="InputFiles",
    action="store",
    required=True,
    type=str,
    help="Input .root file names parser (e.g., gamma_%%07g_gamma_ON_SIDE.root)",
)

parser.add_argument(
    "--OutputFile",
    dest="OutputFile",
    action="store",
    required=True,
    help="Output .h5 file name",
)

parser.add_argument(
    "-N",
    dest="N",
    type=int,
    action="store",
    required=True,
    help="Number of .root file name",
)

# 新增参数：BASE_RUN，控制文件序号起始值（默认0，兼容原有逻辑）
parser.add_argument(
    "--BASE_RUN",
    dest="BASE_RUN",
    type=int,
    action="store",
    default=0,
    help="Base run number for file sequence (default: 0, e.g., 10000 for starting from 10001)",
)

args = parser.parse_args()

InputFiles: str = args.InputFiles
OutputFile: str = args.OutputFile
N: int = args.N
BASE_RUN: int = args.BASE_RUN  # 读取BASE_RUN参数

total_eventN = 0
TFile_list = []

# 核心修改：循环范围从 BASE_RUN+1 到 BASE_RUN+N（匹配Makefile的序号生成逻辑）
# range是左闭右开，因此结束值为 BASE_RUN + N + 1
for n in range(BASE_RUN + 1, BASE_RUN + N + 1):
    file = InputFiles % n
    logging.info(f"Loading: {file}")
    Infile = TFile(file)
    TFile_list.append(Infile)
    tree = Infile.Get("mcTree")
    total_eventN += int(tree.GetEntries())

logging.info(f"{total_eventN} events in these files")

flux = np.zeros(total_eventN, dtype=flux_dtype)
set_nan_defaults(flux)

fstart = 0
fend = 0
for Infile in TFile_list:
    tree = Infile.Get("mcTree")
    eventN = int(tree.GetEntries())
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

with h5py.File(OutputFile, "w") as opt:
    opt.create_dataset("flux", data=flux, compression="gzip")

logging.info(f"Saving: {OutputFile}")
