#pragma once

#include "BambooAnalysis.hh"
#include "BambooFactory.hh"

class PandaXOpticalAnalysis : public BambooAnalysis
{
  public:
    PandaXOpticalAnalysis(const BambooParameters& pars);

    ~PandaXOpticalAnalysis() = default;

    static AnalysisRegister<PandaXOpticalAnalysis> reg;
};
