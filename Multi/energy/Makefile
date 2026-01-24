# # 在 Makefile 开头定义 Python 解释器路径
# CONDA_PYTHON := /public/apps/anaconda3/envs/relics3/bin/python3

# 在Makefile开头添加默认值定义
BASE_RUN ?= 0  # 若未通过环境变量传递BASE_RUN，默认值为0

SHELL:=bash
fileN:=$(FILEN)
eventN:=$(EVENTN)
folder:=$(FOLDER)
geo:=$(GEO)
suffix:=$(SUFFIX)
mode:=$(PMODE)
relicssim:=$(RELICSSIM)
analysis:=$(ANALYSIS)

format:=07g
# 核心修改：序号起始=BASE_RUN+1，结束=BASE_RUN+fileN（如BASE_RUN=10000、fileN=1 → 10001→10001 → 0010001）
filenum:=$(shell seq -f '%$(format)$(suffix)' $$(($(BASE_RUN) + 1)) $$(($(BASE_RUN) + $(fileN))))
json:=$(filenum:%=$(folder)/params_%.json)
combine:=$(folder)/$(mode)$(suffix).root

# 1. 计算起始序号（BASE_RUN + 1，十进制）
first_seq_dec := $(shell echo $$(($(BASE_RUN) + 1)))
# 2. 计算结束序号（BASE_RUN + fileN，十进制）
last_seq_dec := $(shell echo $$(($(BASE_RUN) + $(fileN))))
# 3. 格式化为7位前导零（和文件序号格式%07g一致）
first_seq := $(shell printf "%07d" $(first_seq_dec))
last_seq := $(shell printf "%07d" $(last_seq_dec))
# 4. 拼接最终文件名：events_后缀_起始序号_结束序号.h5
collection:=$(folder)/events$(suffix)_$(first_seq)_$(last_seq).h5

.PHONY : all

all : $(collection)

$(folder)/params_%.json :
	@mkdir -p $(dir $@); \
	[ -z "$(geo)" ] && cp $(relicssim)/config/geo_params.json $@ || cp $(geo) $@

# 暂时取消采用py生成xml
$(folder)/cevns_%.xml : $(folder)/params_%.json
	@mkdir -p $(dir $@)
#	 python3 $(relicssim)/scripts/relics_xml.py $< -o $@ --run_number $(shell echo $* | cut -d'_' -f 1) --gen $(mode)
# 	原逻辑：--run_number $(shell echo $* | cut -d'_' -f 1)
# 	新逻辑：基于BASE_RUN计算，$*为文件索引（如1,2,...）
#	修正：改用单层shell脚本计算，避免嵌套解析失效，新增调试输出
	@num_raw=$$(echo $* | cut -d'_' -f 1); \
	 num_dec=$$((10#$$num_raw)); \
	 run_num=$$(( num_dec )); \
	 echo "文件标识：$* -> 原始序号：$$num_raw -> 十进制：$$num_dec -> 最终run_number: $$run_num"; \
	 python3 $(relicssim)/scripts/relics_xml.py $< -o $@ --run_number $$run_num --gen $(mode) --enable_track --disable_energy_depo

# 提取带前导零的原始序号（如0000008）
# 强制转为十进制（0000008 → 8）
# 与BASE_RUN相加（十进制计算）
# 此时runall命令变化如下：
# 通过环境变量给每个runall.sh传递唯一的BASE_RUN，例如在终端分别执行
# # 第一个实例：BASE_RUN=0
# BASE_RUN=0 ./runall.sh -f 100 -j 50 ... &

# # 第二个实例：BASE_RUN=10000
# BASE_RUN=10000 ./runall.sh -f 100 -j 50 ... &

include $(mode).mk

# 改动1：绝对路径确保新序号（0010001）的文件精准匹配，保留原有注释
$(folder)/events_%.h5 : $(folder)/$(mode)_%.root
	@mkdir -p $(dir $@)
	OMP_NUM_THREADS=2 python3 $(analysis)/Sorting.py --InputFile $(abspath $<) --OutputFile $(abspath $@) > $(abspath $@).log 2>&1

$(collection) : $(patsubst $(folder)/params_%.json,$(folder)/events_%.h5,$(json))
	@mkdir -p $(dir $@)
	OMP_NUM_THREADS=2 python3 $(analysis)/Combine.py --InputFiles $(folder)/events_%$(format)$(suffix).h5 --OutputFile $(abspath $@) -N $(fileN) --BASE_RUN $(BASE_RUN) > $(abspath $@).log 2>&1

# 改动3：-f强制覆盖+绝对路径，适配新序号体系，保留原有注释
$(combine) : $(patsubst $(folder)/params_%.json,$(folder)/$(mode)_%.root,$(json))
	@mkdir -p $(dir $@)
	hadd -f $(abspath $(combine)) $^

clean :
	rm -rf $(folder)/*$(suffix)*

.DELETE_ON_ERROR: 

.SECONDARY: