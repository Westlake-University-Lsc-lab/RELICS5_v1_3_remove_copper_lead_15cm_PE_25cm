#pragma once

#include "BambooAnalysis.hh"
#include "BambooFactory.hh"

class RelicsOpticalAnalysis : public BambooAnalysis
{
  public:
    RelicsOpticalAnalysis(const BambooParameters& pars);

    ~RelicsOpticalAnalysis() = default;

    static AnalysisRegister<RelicsOpticalAnalysis> reg;
};
