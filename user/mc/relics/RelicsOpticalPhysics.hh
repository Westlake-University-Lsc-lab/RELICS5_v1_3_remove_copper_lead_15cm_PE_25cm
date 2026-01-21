#pragma once

#include "BambooFactory.hh"
#include "BambooPhysics.hh"

class RelicsOpticalPhysics : public BambooPhysics
{
  public:
    RelicsOpticalPhysics(const BambooParameters& pars);

    ~RelicsOpticalPhysics() = default;

    static PhysicsRegister<RelicsOpticalPhysics> reg;
};
