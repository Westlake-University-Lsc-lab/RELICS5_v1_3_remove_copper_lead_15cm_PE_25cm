#pragma once

#include "BambooFactory.hh"
#include "BambooPhysics.hh"

class PandaXOpticalPhysics : public BambooPhysics
{
  public:
    PandaXOpticalPhysics(const BambooParameters& pars);

    ~PandaXOpticalPhysics() = default;

    static PhysicsRegister<PandaXOpticalPhysics> reg;
};
