import argparse
import logging

import polars as pl

logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser(description="Combine h5 files together")

parser.add_argument(
    "--InputFiles",
    dest="InputFiles",
    action="store",
    required=True,
    type=str,
    help="Input .parquet file names parser (e.g., ./flux_%%07g_CRN.parquet)",
)

parser.add_argument(
    "--OutputFile",
    dest="OutputFile",
    action="store",
    required=True,
    help="Output .parquet file name",
)

parser.add_argument(
    "-N",
    dest="N",
    type=int,
    action="store",
    required=True,
    help="Number of .parquet file name",
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

flux_list: list[pl.DataFrame] = []

# 核心修改：循环范围从 BASE_RUN+1 到 BASE_RUN+N（匹配Makefile的序号生成逻辑）
# range是左闭右开，因此结束值为 BASE_RUN + N + 1
for n in range(BASE_RUN + 1, BASE_RUN + N + 1):
    file = InputFiles % n
    df = pl.read_parquet(file)
    flux_list.append(df)

flux = pl.concat(flux_list)
flux.write_parquet(OutputFile, compression="gzip")

logging.info(f"{OutputFile} saved")
logging.info(f"{len(flux)} tracks in the file")
