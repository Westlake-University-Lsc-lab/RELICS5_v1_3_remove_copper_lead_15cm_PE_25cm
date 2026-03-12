#!/bin/bash

if [[ -z "${GEO}" ]]; then
    echo "Using default geometry setting"
else
    echo "Using customized geometry setting $GEO"
fi

export RELICSSIM=/public/home/yyy/Relics_yyy_soild     # Need update
export ANALYSIS=/public/home/yyy/Relics_yyy_soild/Multi/energy   # Need update
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


# # Neutron when reactor ON and OFF
# export FOLDER=/public/home/yyy/result_yyy_soild/neutron/neutron_ON_600M
# reactors="ON"
# topsides="SIDE_ON"
# for reactor in $reactors; do
#     for topside in $topsides; do
#         export SUFFIX="_neutron_${reactor}_${topside}"
#         jq ".$SUFFIX=100" $norm | sponge $norm
#         ./run.sh -m neutron -r $reactor -s $topside -f $(expr $files \* 10) -j $parallel -e $(expr $events \* 30) $clean $justprint
#     done
# done

# export FOLDER=/public/home/yyy/result_yyy_soild/neutron/neutron_OFF_200M
# reactors="OFF"
# topsides="SIDE_OFF"
# for reactor in $reactors; do
#     for topside in $topsides; do
#         export SUFFIX="_neutron_${reactor}_${topside}"
#         jq ".$SUFFIX=100" $norm | sponge $norm
#         ./run.sh -m neutron -r $reactor -s $topside -f $(expr $files \* 10) -j $parallel -e $(expr $events \* 10) $clean $justprint
#     done
# done

# Gamma when reactor ON
export FOLDER=/public/home/yyy/result_yyy_soild/gamma/gamma_5.5billion
reactors="ON"
topsides="SIDE"
for reactor in $reactors; do
    for topside in $topsides; do
        export SUFFIX="_gamma_${reactor}_${topside}"
        jq ".$SUFFIX=1000" $norm | sponge $norm
        ./run.sh -m gamma -r $reactor -s $topside -f $(expr $files \* 100) -j $parallel -e $(expr $events \* 100) $clean $justprint
    done
done

python3 genNormalize.py --InputFile $norm --paramsFile "$RELICSSIM/config/geo_params.json" --GeoFile "$RELICSSIM/config/cevns.json" --OutputFile normalization.json

# # Muon induced neutron and gamma
# export FOLDER=$HOME/RelicsSim_v/RelicsSim_v5/results/muon   # Need update
# export SUFFIX="_muon"
# jq ".$SUFFIX=500" $norm | sponge $norm
# ./run.sh -m muon -f $(expr $files \* 10) -j $parallel -e $(expr $events \* 50) $clean $justprint

# # CRN induced neutron and gamma
# export FOLDER=$HOME/RelicsSim_v/RelicsSim_v5/results/CRN   # Need update
# export SUFFIX="_CRN"
# jq ".$SUFFIX=500" $norm | sponge $norm
# ./run.sh -m CRN -f $(expr $files \* 10) -j $parallel -e $(expr $events \* 50) $clean $justprint


# # Material background from metal, PE, and lXe
# export FOLDER=$HOME/RelicsSim_v/RelicsSim_v5/results/material
# isotopes="U238 Th232 Co60 K40"
# components="copper"
# # copper particles number is about 1000
# for isotope in $isotopes; do
#     for component in $components; do
#         export SUFFIX="_${isotope}_${component}"
#         jq ".$SUFFIX=0.0001" $norm | sponge $norm
#         ./run.sh -m material -i $isotope -t $component -f $(expr $files / 100) -j $parallel -e $(expr $events / 100) $clean $justprint
#     done
# done

# isotopes="U238 Th232 Co60 K40"
# components="steel"
# # steel particles number is about 100w
# for isotope in $isotopes; do
#     for component in $components; do
#         export SUFFIX="_${isotope}_${component}"
#         jq ".$SUFFIX=1" $norm | sponge $norm
#         ./run.sh -m material -i $isotope -t $component -f $files -j $parallel -e $(expr $events \* 1) $clean $justprint
#     done
# done


# isotopes="U238 Th232 Co60 K40"
# components="Teflon Flange PMTbase"
# # particles number is about 10w
# for isotope in $isotopes; do
#     for component in $components; do
#         export SUFFIX="_${isotope}_${component}"
#         jq ".$SUFFIX=0.01" $norm | sponge $norm
#         ./run.sh -m material -i $isotope -t $component -f $(expr $files / 10) -j $parallel -e $(expr $events / 10) $clean $justprint
#     done
# done



# isotopes="U238 Th232 Co60 K40 Cs137"
# components="PMTwindow"
# # particles number is about 100w
# for isotope in $isotopes; do
#     for component in $components; do
#         export SUFFIX="_${isotope}_${component}"
#         jq ".$SUFFIX=0.01" $norm | sponge $norm
#         ./run.sh -m material -i $isotope -t $component -f $(expr $files / 1) -j $parallel -e $(expr $events / 1) $clean $justprint
#     done
# done

# # particles number is about 1w
# export SUFFIX="_Kr85_lXe"
# jq ".$SUFFIX=0.01" $norm | sponge $norm
# ./run.sh -m material -i Kr85 -t lXe -f $(expr $files / 10) -j $parallel -e $(expr $events / 10) $clean $justprint

# export SUFFIX="_Rn222_lXe"
# jq ".$SUFFIX=0.01" $norm | sponge $norm
# ./run.sh -m material -i Rn222 -t lXe -f $(expr $files / 10) -j $parallel -e $(expr $events / 10) $clean $justprint


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