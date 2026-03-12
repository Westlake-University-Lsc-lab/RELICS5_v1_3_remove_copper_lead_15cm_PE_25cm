#pragma once

#include "BambooFactory.hh"
#include "BambooGenerator.hh"
#include <G4ParticleGun.hh>
#include <sys/mman.h>

class G4ParticleGun;
class G4Event;

class SampleGenerator : public BambooGenerator
{
  public:
    SampleGenerator(const BambooParameters& pars);

    ~SampleGenerator()
    {
      if (sampleTable != nullptr)
      {
        munmap(sampleTable, table_length * sizeof(SampleRow));
        sampleTable = nullptr;
      }
    };

    virtual void GeneratePrimaries(G4Event* anEvent);

    static GeneratorRegister<SampleGenerator> reg;

  private:
    struct SampleRow
    {
        const double trackX;
        const double trackY;
        const double trackZ;
        const double px;
        const double py;
        const double pz;
        const double trackEnergy;
        const char trackName[24];
    };
    size_t table_length;
    SampleRow* sampleTable = nullptr;

    std::unique_ptr<G4ParticleGun> gun;
};
