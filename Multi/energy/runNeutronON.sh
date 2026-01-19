#!/bin/bash

if [[ -z "${GEO}" ]]; then
    echo "Using default geometry setting"
else
    echo "Using customized geometry setting $GEO"
fi

export RELICSSIM=/public/home/yyy/RELICS5各个版本/RELICS5_v1/RELICS5_v1_3_remove_copper_lead_15cm_PE_25cm     # Need update
export ANALYSIS=/public/home/yyy/RELICS5各个版本/RELICS5_v1/RELICS5_v1_3_remove_copper_lead_15cm_PE_25cm/Multi/energy  # Need update
# export PYTHONPATH="$RELICSSIM/scripts:$PYTHONPATH"

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


# # Neutron when reactor ON
export FOLDER=/public/home/yyy/RELICS5各个版本/RELICS5_v1/RELICS5_v1_3_remove_copper_lead_15cm_PE_25cm/result/NeutronON_600M
reactors="ON"
topsides="SIDE"
for reactor in $reactors; do
    for topside in $topsides; do
        export SUFFIX="_neutron_${reactor}_${topside}"
        jq ".$SUFFIX=1000" $norm | sponge $norm
        ./run.sh -m neutron -r $reactor -s $topside -f $(expr $files \* 10) -j $parallel -e $(expr $events \* 100) $clean $justprint
    done
done
