#pragma once

#include "BambooControl.hh"
#include "BambooDetector.hh"
#include "BambooFactory.hh"
#include "Monoblock.hh"

class HollowCuboid : public Monoblock
{
  public:
    HollowCuboid(const std::string& n, const BambooParameters& pars);

    bool constructMainLV(const BambooParameters& global_pars);

    static DetectorRegister<HollowCuboid, std::string, BambooParameters> reg;

  private:
    // define additional parameters here

  protected:
};
