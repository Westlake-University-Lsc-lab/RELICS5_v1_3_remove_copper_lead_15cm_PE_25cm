#!/bin/bash

if [[ -z "${GEO}" ]]; then
    echo "Using default geometry setting"
else
    echo "Using customized geometry setting $GEO"
fi

export RELICSSIM=/public/home/yyy/RELICS5各个版本/RELICS5_v1/RELICS5_v1_3_remove_copper各个版本/RELICS5_v1/RELICS5_v1_1_PE_in   # Need update
export ANALYSIS=/public/home/yyy/RELICS5各个版本/RELICS5_v1/RELICS5_v1_3_remove_copper各个版本/RELICS5_v1/RELICS5_v1_1_PE_in/Multi/energy   # Need update
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

# # Material background from metal, PE, and lXe
export FOLDER=/public/home/yyy/RELICS5各个版本/RELICS5_v1/RELICS5_v1_3_remove_copper各个版本/RELICS5_v1/RELICS5_v1_1_PE_in/result/Material
isotopes="Kr85"
components="lXe"
for isotope in $isotopes; do
    for component in $components; do
        export SUFFIX="_${isotope}_${component}"
        jq ".$SUFFIX=100" $norm | sponge $norm
        ./run.sh -m material -i Kr85 -t lXe -f $(expr $files \* 10) -j $parallel -e $(expr $events \* 10) $clean $justprint
    done
done


isotopes="Rn222"
components="lXe"
for isotope in $isotopes; do
    for component in $components; do
        export SUFFIX="_${isotope}_${component}"
        jq ".$SUFFIX=100" $norm | sponge $norm
        ./run.sh -m material -i Rn222 -t lXe -f $(expr $files \* 10) -j $parallel -e $(expr $events \* 10) $clean $justprint
    done
done
