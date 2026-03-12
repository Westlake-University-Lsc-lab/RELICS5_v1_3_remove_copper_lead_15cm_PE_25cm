#!/bin/bash

if [[ -z "${GEO}" ]]; then
    echo "Using default geometry setting"
else
    echo "Using customized geometry setting $GEO"
fi

export ANALYSIS=${RELICSSIM}/Multi/energy  # Need update
# export PYTHONPATH="$RELICSSIM/scripts:$PYTHONPATH"

parallel=150
files=75
events=2000
target=''
clean=''
justprint=''

while getopts f:e:j:g:cn flag
do
    case "${flag}" in
        j) parallel=${OPTARG};;
        f) files=${OPTARG};;
        e) events=${OPTARG};;
        g) target=${OPTARG};;
        c) clean='-c';; # only used if target is not set
        n) justprint='-n';;
    esac
done

norm='norm.json'
jq -n ".N=$(expr $files \* $events)" > $norm

if [[ ${clean} == '-c' ]] && [[ ${target} == '' ]]; then
    target='clean'
elif [[ ${target} == '' ]]; then
    target="all"
fi

# Gamma when reactor ON
export FOLDER=${RELICSSIM}/result/GammaON_3B
reactors="ON"
topsides="SIDE"
for reactor in $reactors; do
    for topside in $topsides; do
        export SUFFIX="_gamma_${reactor}_${topside}"
        jq ".$SUFFIX=10000" $norm | sponge $norm
        ${ANALYSIS}/run.sh -m gamma -r $reactor -s $topside -f $(expr $files \* 10) -j $parallel -e $(expr $events \* 1000) -g $target $justprint
    done
done