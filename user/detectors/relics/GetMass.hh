#pragma once

#include <G4String.hh>
#include <G4VPhysicalVolume.hh>

#include <set>

class GetMass
{
  public:
    GetMass() = default;

    void printMass(G4VPhysicalVolume* mainPV);

    G4VPhysicalVolume* getWorld();

  private:
    static std::set<G4String> calculated;
};
