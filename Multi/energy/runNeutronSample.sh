#!/bin/bash

if [[ -z "${GEO}" ]]; then
    echo "Using default geometry setting"
else
    echo "Using customized geometry setting $GEO"
fi

export ANALYSIS=${RELICSSIM}/Multi/energy
# export PYTHONPATH="$RELICSSIM/scripts:$PYTHONPATH"

parallel=200
files=20
events=5000
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
    target="collection"
fi

# # Neutron when reactor ON
export FOLDER=${RELICSSIM}/result/SampleON_1G_1

export SUFFIX="_neutron_sample"
jq ".$SUFFIX=1000" $norm | sponge $norm
${ANALYSIS}/run.sh -m sample -f $(expr $files \* 10) -j $parallel -e $(expr $events \* 1000) $clean $justprint