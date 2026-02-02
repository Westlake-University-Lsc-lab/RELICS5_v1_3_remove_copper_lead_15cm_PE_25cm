#include "SampleGenerator.hh"

#include "BambooUtils.hh"
#include <G4Event.hh>
#include <G4ParticleGun.hh>
#include <G4ParticleTable.hh>
#include <Randomize.hh>
#include <sqlite3.h>

using namespace CLHEP;

GeneratorRegister<SampleGenerator> SampleGenerator::reg("SampleGenerator");

SampleGenerator::SampleGenerator(const BambooParameters& pars)
  : BambooGenerator{pars}, gun{new G4ParticleGun}
{
  const auto& pmap = generatorParameters.getParameters();
  if (pmap.find("db_path") == pmap.end())
  {
    throw std::runtime_error("SampleGenerator: should provide `db_path`");
  }
  if (pmap.find("table") == pmap.end())
  {
    throw std::runtime_error("SampleGenerator: should provide `table`");
  }
  table = generatorParameters.getParameter("table");

  if (sqlite3_open_v2(generatorParameters.getParameter("db_path").c_str(), &db,
                      SQLITE_OPEN_READONLY, nullptr)
      != SQLITE_OK)
  {
    throw std::runtime_error("SampleGenerator: cannot open database file");
  }

  std::stringstream sql;
  sql << "SELECT COUNT(*) FROM " << table << ";";

  sqlite3_stmt* stmt = nullptr;
  if (sqlite3_prepare_v2(db, sql.str().c_str(), -1, &stmt, nullptr) != SQLITE_OK)
  {
    throw std::runtime_error("SampleGenerator: cannot prepare count statement");
  }
  if (sqlite3_step(stmt) == SQLITE_ROW)
  {
    row_count = sqlite3_column_int64(stmt, 0);
  }
  else
  {
    throw std::runtime_error("SampleGenerator: cannot get row count");
  }
  sqlite3_finalize(stmt);
}

void SampleGenerator::GeneratePrimaries(G4Event* anEvent)
{
  std::stringstream sql;
  sql << "SELECT trackX, trackY, trackZ, px, py, pz, trackEnergy, trackName FROM " << table
      << " LIMIT 1 OFFSET " << G4RandFlat::shootInt(row_count) << ";";

  sqlite3_stmt* stmt = nullptr;
  if (sqlite3_prepare_v2(db, sql.str().c_str(), -1, &stmt, nullptr) != SQLITE_OK)
  {
    throw std::runtime_error("SampleGenerator: cannot prepare select statement");
  }
  if (sqlite3_step(stmt) == SQLITE_ROW)
  {
    const G4double dirX = sqlite3_column_double(stmt, 0) * mm;
    const G4double dirY = sqlite3_column_double(stmt, 1) * mm;
    const G4double dirZ = sqlite3_column_double(stmt, 2) * mm;
    const G4double px = sqlite3_column_double(stmt, 3) * keV;
    const G4double py = sqlite3_column_double(stmt, 4) * keV;
    const G4double pz = sqlite3_column_double(stmt, 5) * keV;
    const G4double energy = sqlite3_column_double(stmt, 6) * keV;
    const G4String trackName = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 7));

    auto particleTable = G4ParticleTable::GetParticleTable();
    G4ParticleDefinition* particle = particleTable->FindParticle(trackName);
    if (particle == nullptr)
    {
      throw std::runtime_error("SampleGenerator: cannot find particle " + trackName);
    }

    gun->SetParticleDefinition(particle);
    gun->SetParticleEnergy(energy);
    gun->SetParticleMomentumDirection(G4ThreeVector(px, py, pz).unit());
    gun->SetParticlePosition(G4ThreeVector(dirX, dirY, dirZ));
    gun->GeneratePrimaryVertex(anEvent);
  }
  else
  {
    throw std::runtime_error("SampleGenerator: cannot get row data");
  }
  sqlite3_finalize(stmt);
}
