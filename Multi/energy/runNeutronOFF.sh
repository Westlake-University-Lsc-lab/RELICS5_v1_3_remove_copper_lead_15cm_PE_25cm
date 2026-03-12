#!/bin/bash

if [[ -z "${GEO}" ]]; then
    echo "Using default geometry setting"
else
    echo "Using customized geometry setting $GEO"
fi

export ANALYSIS=${RELICSSIM}/Multi/energy  # Need update
# export PYTHONPATH="$RELICSSIM/scripts:$PYTHONPATH"

parallel=50
files=1000
events=10000
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

# # Neutron when reactor ON and OFF
export FOLDER=${RELICSSIM}/result/NeutronOFF_60M
reactors="OFF"
topsides="TOP"
for reactor in $reactors; do
    for topside in $topsides; do
        export SUFFIX="_neutron_${reactor}_${topside}"
        jq ".$SUFFIX=1000" $norm | sponge $norm
        ./run.sh -m neutron -r $reactor -s $topside -f $(expr $files \* 10) -j $parallel -e $(expr $events \* 100) -g $target $justprint
    done
done
