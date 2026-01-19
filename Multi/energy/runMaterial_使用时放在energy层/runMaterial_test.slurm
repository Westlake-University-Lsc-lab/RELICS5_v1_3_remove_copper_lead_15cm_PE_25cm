#!/bin/bash
#SBATCH -J runCRN_test           # 设置作业名称
#SBATCH -o /public/home/yyy/RELICS5各个版本/RELICS5_v1/RELICS5_v1_3_remove_copper各个版本/RELICS5_v1/RELICS5_v1_1_PE_in/result/Material_test_out/runMaterial_test.out       # 标准输出文件
#SBATCH -e /public/home/yyy/RELICS5各个版本/RELICS5_v1/RELICS5_v1_3_remove_copper各个版本/RELICS5_v1/RELICS5_v1_1_PE_in/result/Material_test_out/runMaterial_test.err       # 错误输出文件
#SBATCH -n 1                 # 总任务数（由 runCRN_test.sh 自行控制并行任务）
#SBATCH -c 14                # 每个任务分配的 CPU 核心数（根据服务器总核数调整）
#SBATCH --mem=85000          # 每个任务的内存分配（单位 MB）
#SBATCH -p compute           # 指定分区
#SBATCH -w node01            # 指定在 node01 上运行

# 激活 conda 环境
source /public/apps/anaconda3/etc/profile.d/conda.sh
conda activate relics3

# 运行脚本
BASE_RUN=2700 ./runMaterial_test.sh -j 10 -f 1 -e 1