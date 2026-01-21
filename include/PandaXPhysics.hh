#pragma once

#include "BambooFactory.hh"
#include "BambooPhysics.hh"

class PandaXPhysics : public BambooPhysics
{
  public:
    PandaXPhysics(const BambooParameters& pars);

    ~PandaXPhysics() = default;

    static PhysicsRegister<PandaXPhysics> reg;
};
