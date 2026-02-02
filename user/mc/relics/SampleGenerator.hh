#pragma once

#include "BambooFactory.hh"
#include "BambooGenerator.hh"
#include <G4ParticleGun.hh>
#include <sqlite3.h>

#include <memory>

class G4ParticleGun;
class G4Event;

class SampleGenerator : public BambooGenerator
{
  public:
    SampleGenerator(const BambooParameters& pars);

    ~SampleGenerator()
    {
      if (db != nullptr) sqlite3_close_v2(db);
    };

    virtual void GeneratePrimaries(G4Event* anEvent);

    static GeneratorRegister<SampleGenerator> reg;

  private:
    sqlite3* db = nullptr;
    std::string table;

    sqlite3_int64 row_count;

    std::unique_ptr<G4ParticleGun> gun;
};
