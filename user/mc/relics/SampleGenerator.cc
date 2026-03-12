#include "SampleGenerator.hh"

#include "BambooUtils.hh"
#include <G4Event.hh>
#include <G4ParticleGun.hh>
#include <G4ParticleTable.hh>
#include <Randomize.hh>
#include <sys/mman.h>
#include <unistd.h>

using namespace CLHEP;

GeneratorRegister<SampleGenerator> SampleGenerator::reg("SampleGenerator");

SampleGenerator::SampleGenerator(const BambooParameters& pars)
  : BambooGenerator{pars}, gun{new G4ParticleGun}
{
  const auto& pmap = generatorParameters.getParameters();
  if (pmap.find("file_path") == pmap.end())
    throw std::runtime_error("SampleGenerator: should provide `file_path`");

  auto& file_path = generatorParameters.getParameter("file_path");

  FILE* fd = fopen64(file_path.c_str(), "rb");
  if (fd == nullptr) throw std::runtime_error("SampleGenerator: cannot open file " + file_path);

  if (fseeko64(fd, 0, SEEK_END) != 0)
    throw std::runtime_error("SampleGenerator: cannot seek to end of file " + file_path);

  auto tail = ftello64(fd);
  if (tail <= 0)
    throw std::runtime_error("SampleGenerator: file is empty or get size failed for " + file_path);

  if (tail % sizeof(SampleRow) != 0)
    throw std::runtime_error("SampleGenerator: file size is not multiple of SampleRow size in "
                             + file_path);

  table_length = tail / sizeof(SampleRow);

  sampleTable = static_cast<SampleRow*>(
    mmap(nullptr, table_length * sizeof(SampleRow), PROT_READ, MAP_SHARED, fileno(fd), 0));

  if (fclose(fd) != 0) throw std::runtime_error("SampleGenerator: cannot close file " + file_path);

  if (sampleTable == MAP_FAILED)
    throw std::runtime_error("SampleGenerator: cannot mmap file " + file_path);
}

void SampleGenerator::GeneratePrimaries(G4Event* anEvent)
{
  const long offset = G4RandFlat::shootInt(table_length);
  const double& dirX = sampleTable[offset].trackX * mm;
  const double& dirY = sampleTable[offset].trackY * mm;
  const double& dirZ = sampleTable[offset].trackZ * mm;
  const double& px = sampleTable[offset].px * keV;
  const double& py = sampleTable[offset].py * keV;
  const double& pz = sampleTable[offset].pz * keV;
  const double& energy = sampleTable[offset].trackEnergy * keV;
  const G4String trackName = sampleTable[offset].trackName;

  auto particleTable = G4ParticleTable::GetParticleTable();
  G4ParticleDefinition* particle = particleTable->FindParticle(trackName);
  if (particle == nullptr)
    throw std::runtime_error("SampleGenerator: cannot find particle " + trackName);

  gun->SetParticleDefinition(particle);
  gun->SetParticleEnergy(energy);
  gun->SetParticleMomentumDirection(G4ThreeVector(px, py, pz).unit());
  gun->SetParticlePosition(G4ThreeVector(dirX, dirY, dirZ));
  gun->GeneratePrimaryVertex(anEvent);
}
