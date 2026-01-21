#pragma once

#include "BambooControl.hh"
#include "BambooDetector.hh"
#include "BambooFactory.hh"
#include "Monoblock.hh"
#include <G4TwoVector.hh>

class MeshGrid_cuowei : public Monoblock
{
  public:
    MeshGrid_cuowei(const std::string& n, const BambooParameters& pars);

    bool constructMainLV(const BambooParameters& global_pars);

    static DetectorRegister<MeshGrid_cuowei, std::string, BambooParameters> reg;

  private:
    // define additional parameters here
    std::vector<G4TwoVector> GetPolygon(const G4int& sides, const G4double& radius);

  protected:
};
