#!/bin/bash
#SBATCH -J runall_gamma_R           # 设置作业名称
#SBATCH -o /public/home/yyy/result_yyy_soild/gamma/output/runMuon_%j.out       # 标准输出文件
#SBATCH -e /public/home/yyy/result_yyy_soild/gamma/output/runMuon_%j.err       # 错误输出文件
#SBATCH -n 1                 # 总任务数（由 runMuon.sh 自行控制并行任务）
#SBATCH -c 45                # 每个任务分配的 CPU 核心数（根据服务器总核数调整）原本为50，它过大会导致资源不够
#SBATCH --mem=85000         # 每个任务的内存分配（单位 MB）（原为85000）
#SBATCH -p compute          # 指定分区（原为compute）
#SBATCH -w node02            # 指定在 node02 上运行

# 激活 conda 环境
source /public/apps/anaconda3/etc/profile.d/conda.sh
conda activate relics3

# 运行脚本 #先来55000万个即5.5亿个看看情况，然后改变-f为550模拟55亿个确定之
./runall_gamma_R.sh -j 45 -f 550 -e 1000