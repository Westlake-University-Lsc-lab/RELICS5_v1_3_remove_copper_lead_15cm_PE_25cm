import argparse

import h5py
import numpy as np
from dtypes import event_dtype, primary_dtype
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Combine h5 files together")

parser.add_argument(
    "--InputFiles",
    dest="InputFiles",
    action="store",
    required=True,
    type=str,
    help="Input .h5 file names parser (e.g., ./events_%%07g_CRN.h5)",
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
    help="Number of .h5 file name",
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

InputFiles = args.InputFiles
OutputFile = args.OutputFile
N = args.N
BASE_RUN = args.BASE_RUN  # 读取BASE_RUN参数

events = []
primaries = []
# clusters = []

# 核心修改：循环范围从 BASE_RUN+1 到 BASE_RUN+N（匹配Makefile的序号生成逻辑）
# range是左闭右开，因此结束值为 BASE_RUN + N + 1
for n in tqdm(range(BASE_RUN + 1, BASE_RUN + N + 1)):
    file = InputFiles % n
    with h5py.File(file, "r", libver="latest", swmr=True) as ipt:
        events.append(np.array(ipt["events"]))
        primaries.append(np.array(ipt["primaries"]))
        # clusters.append(np.array(ipt['clusters']))

events = np.hstack(events).astype(event_dtype)
primaries = np.hstack(primaries).astype(primary_dtype)
# clusters = np.hstack(clusters).astype(cluster_dtype)

with h5py.File(OutputFile, "w") as opt:
    opt.create_dataset("events", data=events, compression="gzip")
    opt.create_dataset("primaries", data=primaries, compression="gzip")
    # opt.create_dataset('clusters', data=primaries, compression='gzip')  # 原代码笔误：应改为clusters

print(f"{OutputFile} saved")
print(f"{len(events)} events in the file")
