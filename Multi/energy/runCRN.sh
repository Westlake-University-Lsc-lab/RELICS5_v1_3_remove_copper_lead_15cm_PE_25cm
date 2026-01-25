#!/bin/bash

if [[ -z "${GEO}" ]]; then
    echo "Using default geometry setting"
else
    echo "Using customized geometry setting $GEO"
fi

export ANALYSIS=${RELICSSIM}/Multi/energy   # Need update
# export PYTHONPATH="$RELICSSIM/scripts:$PYTHONPATH"

# 运行命令示例：
# BASE_RUN=0 ./runall.sh -f 100 -j 50 ... &
parallel=50
files=1000
events=10000
clean=''
justprint=''

while getopts f:e:j:cn flag
do
    case "${flag}" in
        j) parallel=${OPTARG};;
        f) files=${OPTARG};;
        e) events=${OPTARG};;
        c) clean='-c';;
        n) justprint='-n';;
    esac
done

norm='norm.json'
jq -n ".N=$(expr $files \* $events)" > $norm



# CRN induced neutron and gamma
export FOLDER=${RELICSSIM}/result/CRN_300M  # Need update
export SUFFIX="_CRN"
jq ".$SUFFIX=1000" $norm | sponge $norm
./run.sh -m CRN -f $(expr $files \* 10) -j $parallel -e $(expr $events \* 100) $clean $justprint


python3 genNormalize.py --InputFile $norm --paramsFile "$RELICSSIM/config/geo_params.json" --GeoFile "$RELICSSIM/config/cevns.json" --OutputFile normalization.json
#python3 genNormalize.py --InputFile $norm --GeoFile $RELICSSIM/config/cevns.json --OutputFile normalization.json

# if [ -z $justprint ]
# then
#     python3 genTemplate.py --InputFolder $HOME/results --InputNorm normalization.json --OutputFile templateSim.npz
# fi



# ignore this particles

# # Neutron when reactor ON and OFF
# export FOLDER=$HOME/results/neutron
# reactors="ON OFF"
# topsides="TOP SIDE"
# for reactor in $reactors; do
#     for topside in $topsides; do
#         export SUFFIX="_neutron_${reactor}_${topside}"
#         jq ".$SUFFIX=100" $norm | sponge $norm
#         ./run.sh -m neutron -r $reactor -s $topside -f $(expr $files \* 10) -j $parallel -e $(expr $events \* 10) $clean $justprint
#     done
# done

# # Gamma when reactor ON
# export FOLDER=$HOME/results/gamma
# reactors="ON"
# topsides="SIDE"
# for reactor in $reactors; do
#     for topside in $topsides; do
#         export SUFFIX="_gamma_${reactor}_${topside}"
#         jq ".$SUFFIX=1000" $norm | sponge $norm
#         ./run.sh -m gamma -r $reactor -s $topside -f $(expr $files \* 100) -j $parallel -e $(expr $events \* 10) $clean $justprint
#     done
# done