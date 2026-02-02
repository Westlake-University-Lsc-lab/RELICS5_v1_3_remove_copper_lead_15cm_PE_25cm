#include "HollowCuboid.hh"

#include "PandaXSensitiveDetector.hh"
#include <G4Box.hh>
#include <G4LogicalVolume.hh>
#include <G4Material.hh>
#include <G4SubtractionSolid.hh>

DetectorRegister<HollowCuboid, std::string, BambooParameters> HollowCuboid::reg("HollowCuboid");

HollowCuboid::HollowCuboid(const std::string& n, const BambooParameters& pars) : Monoblock(n, pars)
{
  G4cout << "create detector HollowCuboid..." << G4endl;
}

bool HollowCuboid::constructMainLV(const BambooParameters&)
{
  using namespace CLHEP;
  auto soliname = parameters.getParameter("soliname");
  auto logivol = parameters.getParameter("logivol");
  auto width_x = parameters.evaluateParameter("width_x");
  auto width_y = parameters.evaluateParameter("width_y");
  auto width_z = parameters.evaluateParameter("width_z");
  auto thickness = parameters.evaluateParameter("thickness");
  auto material = parameters.getParameter("material");
  auto optical_sister = parameters.getParameter("optical_sister");
  if (width_x == 0)
  {
    width_x = 4 * m;
  }
  if (width_y == 0)
  {
    width_y = 4 * m;
  }
  if (width_z == 0)
  {
    width_z = 4 * m;
  }
  if (thickness == 0)
  {
    thickness = 10 * cm;
  }
  auto outerSolid = new G4Box("outer_" + soliname, width_x / 2, width_y / 2, width_z / 2);
  auto innerSolid = new G4Box("inner_" + soliname, width_x / 2 - thickness, width_y / 2 - thickness,
                              width_z / 2 - thickness);
  auto solid =
    new G4SubtractionSolid(soliname, outerSolid, innerSolid, nullptr, G4ThreeVector(0, 0, 0));
  auto medium = G4Material::GetMaterial(material);
  mainLV = new G4LogicalVolume(solid, medium, logivol, nullptr, nullptr, nullptr);
  return true;
}
