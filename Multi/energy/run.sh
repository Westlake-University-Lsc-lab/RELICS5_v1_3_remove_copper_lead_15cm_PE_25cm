#!/bin/bash

mode='muon'
isotope='geantino'
component='steel'
reactor='ON'
topside='TOP'
files=100
events=100000
parallel=50
target=''
clean=''
justprint=''

while getopts m:i:t:r:s:f:e:j:g:cn flag
do
    case "${flag}" in
        m) mode=${OPTARG};;
        i) isotope=${OPTARG};;
        t) component=${OPTARG};;
        r) reactor=${OPTARG};;
        s) topside=${OPTARG};;
        f) files=${OPTARG};;
        e) events=${OPTARG};;
        j) parallel=${OPTARG};;
        g) target=${OPTARG};;
        c) clean='clean';; # only used if target is not set
        n) justprint='-n';;
    esac
done

export FILEN=$files
export EVENTN=$events
export PMODE=$mode
export ISOTOPE=$isotope
export COMPONENT=$component
export REACTOR=$reactor
export TOPSIDE=$topside

if [[ -z "${RELICSSIM}" ]]; then
    echo "Error: Must provide directory to RelicsSim"
    exit 1
fi

if [[ -z "${ANALYSIS}" ]]; then
    echo "Error: Must provide directory to RelicsAnalysis"
    exit 1
fi

if [[ -z "${FOLDER}" ]]; then
    echo "Error: Must provide directory to simulation results"
    exit 1
fi

if [[ ${clean} == 'clean' ]] && [[ ${target} == '' ]]; then
    target='clean'
fi

make -C ${ANALYSIS} -j $parallel $target $justprint
