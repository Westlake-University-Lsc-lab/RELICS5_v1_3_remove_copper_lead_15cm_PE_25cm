#!/bin/bash
#SBATCH -J runMuon           # 设置作业名称
#SBATCH -o /public/home/yyy/RELICS5各个版本/RELICS5_v1/RELICS5_v1_3_remove_copper_lead_15cm_PE_25cm/result/muon_out/runMuon_2.out       # 标准输出文件
#SBATCH -e /public/home/yyy/RELICS5各个版本/RELICS5_v1/RELICS5_v1_3_remove_copper_lead_15cm_PE_25cm/result/muon_out/runMuon_2.err       # 错误输出文件
#SBATCH -n 1                 # 总任务数（由 runMuon.sh 自行控制并行任务）
#SBATCH -c 27                # 每个任务分配的 CPU 核心数（根据服务器总核数调整）
#SBATCH --mem=85000          # 每个任务的内存分配（单位 MB）
#SBATCH -p compute           # 指定分区
#SBATCH -w node02            # 指定在 node02 上运行

# 激活 conda 环境
source /public/apps/anaconda3/etc/profile.d/conda.sh
conda activate relics3

# 运行脚本
BASE_RUN=1000 ./runMuon.sh -j 27 -f 100 -e 1000