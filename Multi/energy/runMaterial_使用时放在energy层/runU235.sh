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
isotopes="U235"
components="copper"
# copper particles number is about 1000
for isotope in $isotopes; do
    for component in $components; do
        export SUFFIX="_${isotope}_${component}"
        jq ".$SUFFIX=1000" $norm | sponge $norm
        ./run.sh -m material -i $isotope -t $component -f $(expr $files \* 1) -j $parallel -e $(expr $events \* 1000) $clean $justprint
    done
done

isotopes="U235"
components="steel"
# copper particles number is about 1000
for isotope in $isotopes; do
    for component in $components; do
        export SUFFIX="_${isotope}_${component}"
        jq ".$SUFFIX=2000" $norm | sponge $norm
        ./run.sh -m material -i $isotope -t $component -f $(expr $files \* 2) -j $parallel -e $(expr $events \* 1000) $clean $justprint
    done
done

isotopes="U235"
components="PMTwindow"
# copper particles number is about 1000
for isotope in $isotopes; do
    for component in $components; do
        export SUFFIX="_${isotope}_${component}"
        jq ".$SUFFIX=12000" $norm | sponge $norm
        ./run.sh -m material -i $isotope -t $component -f $(expr $files \* 12) -j $parallel -e $(expr $events \* 1000) $clean $justprint
    done
done

isotopes="U235"
components="PMTbase"
# copper particles number is about 1000
for isotope in $isotopes; do
    for component in $components; do
        export SUFFIX="_${isotope}_${component}"
        jq ".$SUFFIX=2000" $norm | sponge $norm
        ./run.sh -m material -i $isotope -t $component -f $(expr $files \* 2) -j $parallel -e $(expr $events \* 1000) $clean $justprint
    done
done

isotopes="U235"
components="Flange"
# copper particles number is about 1000
for isotope in $isotopes; do
    for component in $components; do
        export SUFFIX="_${isotope}_${component}"
        jq ".$SUFFIX=1000" $norm | sponge $norm
        ./run.sh -m material -i $isotope -t $component -f $(expr $files \* 1) -j $parallel -e $(expr $events \* 1000) $clean $justprint
    done
done