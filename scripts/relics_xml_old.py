#!/usr/bin/python3
import argparse
import copy
import json
import os
from xml.dom.minidom import Document

# 保持示例的导入结构（需确保arrangement模块存在）
from arrangement import PMTArrangement

# ===================== 命令行参数解析（完全对齐示例风格）=====================
parser = argparse.ArgumentParser(
    description="Automatically relics .xml geometry generator"
)

parser.add_argument(
    "ipt", action="store", help="Input .json file, containing geometry parameters"
)
parser.add_argument(
    "-o", dest="opt", action="store", required=True, help="Output .xml file name"
)
parser.add_argument(
    "--run_number",
    dest="run_number",
    action="store",
    default="0",
    help="Run number in .xml file",
)
parser.add_argument(
    "--gen",
    dest="generator",
    choices=["muon", "neutron", "gamma", "material", "CRN"],
    action="store",
    default="muon",
    help="Generator used",
)
parser.add_argument(
    "--cutlength",
    dest="cutlength",
    type=float,
    action="store",
    default=0.1,  # in mm
    help="Cut length used in simulation",
)
parser.add_argument(
    "--enable_track", action="store_true", help="Enable track of surface flux"
)
parser.add_argument(
    "--force_sd", action="store_true", help="Force all solid sensitive detector"
)
parser.add_argument(
    "--check_overlap", action="store_true", help="Whether check overlap of volumes"
)
parser.add_argument(
    "--get_geo_mass", action="store_true", help="Whether print geometry mass"
)
parser.add_argument(
    "--save_txt", action="store_true", help="Whether save .txt files of position"
)
parser.add_argument(
    "--optical", action="store_true", help="Whether do optical simulation"
)

args = parser.parse_args()

# 解析参数（变量命名完全对齐示例）
number = args.run_number
fipt = args.ipt
fopt = args.opt
gen = args.generator
cutlength = args.cutlength
enable_track = args.enable_track
force_sd = args.force_sd
check_overlap = args.check_overlap
get_geo_mass = args.get_geo_mass
save_txt = args.save_txt
optical = args.optical

# ===================== 加载几何参数（JSON）=====================
with open(fipt) as f:
    params = json.load(f)

# ===================== 固定参数定义（对齐示例的硬编码参数）=====================
# 世界体积半长（示例固定为500cm）
world_half_x = 500
# LXe veto相关固定参数
radius_LxeVeto = 21.443756
position_lxe = -0.7  # LXe基准位置（cm）

# ===================== 从JSON加载核心参数（带断言检查，对齐示例）=====================
# 铅/铜/PE/空气尺寸
lead_width_x = params["lead_width_x"]
assert lead_width_x >= 0
lead_width_y = params["lead_width_y"]
assert lead_width_y >= 0
lead_width_z = params["lead_width_z"]
assert lead_width_z >= 0

copper_width_x = params["copper_width_x"]
assert copper_width_x >= 0
copper_width_y = params["copper_width_y"]
assert copper_width_y >= 0
copper_width_z = params["copper_width_z"]
assert copper_width_z >= 0

inner_pe_width_x = params["inner_pe_width_x"]
assert inner_pe_width_x >= 0
inner_pe_width_y = params["inner_pe_width_y"]
assert inner_pe_width_y >= 0
inner_pe_width_z = params["inner_pe_width_z"]
assert inner_pe_width_z >= 0

air_width_x = params["air_width_x"]
assert air_width_x >= 0
air_width_y = params["air_width_y"]
assert air_width_y >= 0
air_width_z = params["air_width_z"]
assert air_width_z >= 0

# 容器尺寸
outer_container_radius = params["outer_container_radius"]
assert outer_container_radius >= 0
outer_container_height = params["outer_container_height"]
assert outer_container_height >= 0
outer_container_shift_z = params["outer_container_shift_z"]
assert outer_container_shift_z >= -1000  # 放宽范围，仅防异常值

outer_container_top_width_x = params["outer_container_top_width_x"]
assert outer_container_top_width_x >= 0
outer_container_top_width_y = params["outer_container_top_width_y"]
assert outer_container_top_width_y >= 0
outer_container_top_width_z = params["outer_container_top_width_z"]
assert outer_container_top_width_z >= 0
outer_container_top_shift_z = params["outer_container_top_shift_z"]
assert outer_container_top_shift_z >= -1000

outer_container_bottom_radius = params["outer_container_bottom_radius"]
assert outer_container_bottom_radius >= 0
outer_container_bottom_height = params["outer_container_bottom_height"]
assert outer_container_bottom_height >= 0
outer_container_bottom_shift_z = params["outer_container_bottom_shift_z"]
assert outer_container_bottom_shift_z >= -1000

vacuum_radius = params["vacuum_radius"]
assert vacuum_radius >= 0
vacuum_height = params["vacuum_height"]
assert vacuum_height >= 0
vacuum_shift_z = params["vacuum_shift_z"]
assert vacuum_shift_z >= -1000

inner_container_top_radius = params["inner_container_top_radius"]
assert inner_container_top_radius >= 0
inner_container_top_height = params["inner_container_top_height"]
assert inner_container_top_height >= 0
inner_container_top_shift_z = params["inner_container_top_shift_z"]
assert inner_container_top_shift_z >= -1000

inner_container_bottom_radius = params["inner_container_bottom_radius"]
assert inner_container_bottom_radius >= 0
inner_container_bottom_height = params["inner_container_bottom_height"]
assert inner_container_bottom_height >= 0
inner_container_bottom_shift_z = params["inner_container_bottom_shift_z"]
assert inner_container_bottom_shift_z >= -1000

inner_container_radius = params["inner_container_radius"]
assert inner_container_radius >= 0
inner_container_height = params["inner_container_height"]
assert inner_container_height >= 0

# 氙相关尺寸
outer_gxe_radius = params["outer_gxe_radius"]
assert outer_gxe_radius >= 0
outer_gxe_height = params["outer_gxe_height"]
assert outer_gxe_height >= 0
outer_gxe_shift_z = params["outer_gxe_shift_z"]
assert outer_gxe_shift_z >= -1000

outer_lxe_radius = params["outer_lxe_radius"]
assert outer_lxe_radius >= 0
outer_lxe_height = params["outer_lxe_height"]
assert outer_lxe_height >= 0
outer_lxe_shift_z = params["outer_lxe_shift_z"]
assert outer_lxe_shift_z >= -1000

teflon_radius = params["teflon_radius"]
assert teflon_radius >= 0
teflon_height = params["teflon_height"]
assert teflon_height >= 0
teflon_shift_z = params["teflon_shift_z"]
assert teflon_shift_z >= -1000

lxenon_radius = params["lxenon_radius"]
assert lxenon_radius >= 0
lxenon_height = params["lxenon_height"]
assert lxenon_height >= 0

teflon_gas_radius = params["teflon_gas_radius"]
assert teflon_gas_radius >= 0
teflon_gas_height = params["teflon_gas_height"]
assert teflon_gas_height >= 0
teflon_gas_shift_z = params["teflon_gas_shift_z"]
assert teflon_gas_shift_z >= -1000

gasxenon_radius = params["gasxenon_radius"]
assert gasxenon_radius >= 0
gasxenon_height = params["gasxenon_height"]
assert gasxenon_height >= 0

# 聚四氟乙烯板尺寸
top_teflon_radius = params["top_teflon_radius"]
assert top_teflon_radius >= 0
top_teflon_height = params["top_teflon_height"]
assert top_teflon_height >= 0
top_teflon_width_x = params["top_teflon_width_x"]
assert top_teflon_width_x >= 0
top_teflon_shift_z = params["top_teflon_shift_z"]
assert top_teflon_shift_z >= -1000

bot_teflon_radius = params["bot_teflon_radius"]
assert bot_teflon_radius >= 0
bot_teflon_height = params["bot_teflon_height"]
assert bot_teflon_height >= 0
bot_teflon_width_x = params["bot_teflon_width_x"]
assert bot_teflon_width_x >= 0
bot_teflon_shift_z = params["bot_teflon_shift_z"]
assert bot_teflon_shift_z >= -1000

# 电极尺寸
mesh_radius = params["mesh_radius"]
assert mesh_radius >= 0
mesh_wire_diameter = params["mesh_wire_diameter"]
assert mesh_wire_diameter >= 0
mesh_wire_pitch = params["mesh_wire_pitch"]
assert mesh_wire_pitch >= 0

anode_shift_z = params["anode_shift_z"]
assert anode_shift_z >= -1000
gate_shift_z = params["gate_shift_z"]
assert gate_shift_z >= -1000
cathode_shift_z = params["cathode_shift_z"]
assert cathode_shift_z >= -1000
bottom_screening_shift_z = params["bottom_screening_shift_z"]
assert bottom_screening_shift_z >= -1000

# 成型环尺寸
shaping_rings_outer_radius = params["shaping_rings_outer_radius"]
assert shaping_rings_outer_radius >= 0
shaping_rings_inner_radius = params["shaping_rings_inner_radius"]
assert shaping_rings_inner_radius >= 0
shaping_rings_height = params["shaping_rings_height"]
assert shaping_rings_height >= 0

# 材料属性参数
lxenon_scintillation_yield = params["lxenon_scintillation_yield"]
lxenon_resolution_scale = params["lxenon_resolution_scale"]
lxenon_abs_length = params["lxenon_abs_length"]
gxe_abs_length = params["gxe_abs_length"]
ss304l_reflectivity = params["ss304l_reflectivity"]
quartz_rindex = params["quartz_rindex"]
teflon_reflectivity = params["teflon_reflectivity"]
teflon_gas_reflectivity = params["teflon_gas_reflectivity"]
teflon_specular_lobe = params["teflon_specular_lobe"]
teflon_gas_specular_lobe = params["teflon_gas_specular_lobe"]
lxenon_rindex = params["lxenon_rindex"]

# 生成器参数
muon_x = params["muon_x"]
assert muon_x >= 0
muon_z = params["muon_z"]
assert muon_z >= 0
muon_e_low = params["muon_e_low"]

# ===================== 光学/非光学分支（完全对齐示例）=====================
if optical:
    physics_name = "RelicsOpticalPhysics"
    generator_name = "ConfineGenerator"
    analysis_name = "RelicsOpticalAnalysis"

    LXesd = False
    PMTsd = True
    opticalsd = True
    seed = int(number)

    # 材料属性（光学模式）
    materialList = {
        "LXe_SCINTILLATIONYIELD": lxenon_scintillation_yield,
        "LXe_RESOLUTIONSCALE": lxenon_resolution_scale,
        "LXe_ABSLENGTH": lxenon_abs_length,
        "GXe_ABSLENGTH": gxe_abs_length,
        "SS304LSteel_REFLECTIVITY": ss304l_reflectivity,
        "Quartz_RINDEX": quartz_rindex,
        "Teflon_REFLECTIVITY": teflon_reflectivity,
        "TeflonGas_REFLECTIVITY": teflon_gas_reflectivity,
        "Teflon_SPECULARLOBECONSTANT": teflon_specular_lobe,
        "TeflonGas_SPECULARLOBECONSTANT": teflon_gas_specular_lobe,
        "LXe_RINDEX": lxenon_rindex,
    }

    analysisList = {
        "EnableEnergyDeposition": 0,
        "EnablePrimaryParticle": 1,
        "SaveNullEvents": 1,
        "OpticalSdName": "bR8520",
        "UserSeed": f"{seed}",
        "GetGeoMass": int(get_geo_mass),
    }

    pmt_opsurface = {
        "base_type": "dielectric_metal",
        "casing_finish": "polished",
        "casing_type": "dielectric_metal",
        "window_partner": "parent",
        "window_finish": "polished",
        "window_order": str(1),
        "photocathode_finish": "polished",
    }
    surface = True
else:
    physics_name = "PandaXPhysics"
    if gen == "muon":
        generator_name = "MuonGenerator"
    elif gen == "neutron" or gen == "gamma":
        generator_name = "SimpleGPSGenerator"
    elif gen == "material":
        generator_name = "ConfineGenerator"
    elif gen == "CRN":
        generator_name = "NeutronGenerator"
    analysis_name = "PandaXAnalysis"

    LXesd = True
    Plasticsd = False
    PMTsd = False
    opticalsd = False
    seed = 0

    # 材料属性（非光学模式）
    materialList = {
        "LXe_SCINTILLATIONYIELD": lxenon_scintillation_yield,
        "LXe_RESOLUTIONSCALE": lxenon_resolution_scale,
        "LXe_ABSLENGTH": lxenon_abs_length,
        "GXe_ABSLENGTH": gxe_abs_length,
        "SS304LSteel_REFLECTIVITY": ss304l_reflectivity,
        "Quartz_RINDEX": quartz_rindex,
        "Teflon_REFLECTIVITY": teflon_reflectivity,
        "TeflonGas_REFLECTIVITY": teflon_gas_reflectivity,
        "Teflon_SPECULARLOBECONSTANT": teflon_specular_lobe,
        "TeflonGas_SPECULARLOBECONSTANT": teflon_gas_specular_lobe,
        "LXe_RINDEX": lxenon_rindex,
    }

    analysisList = {
        "EnableEnergyDeposition": 1,
        "EnableSurfaceFlux": int(enable_track),
        "EnablePrimaryParticle": 1,
        "SaveNullEvents": 0,
        "EnableDecayChainSplitting": 1,
        "ChainSplittingLifeTime": "400*us",
        "UserSeed": f"{seed}",
        "GetGeoMass": int(get_geo_mass),
    }

    pmt_opsurface = dict()
    surface = False

# ===================== XML文档初始化（对齐示例）=====================
doc = Document()
djson = dict()

root = doc.createElement("BambooMC")
doc.appendChild(root)

# Run节点
run = doc.createElement("run")
run.setAttribute("number", number)
root.appendChild(run)
djson["run"] = int(number)

# Geometry节点
geometry = doc.createElement("geometry")
root.appendChild(geometry)
djson["geometry"] = dict()

# Material节点
material = doc.createElement("material")
geometry.appendChild(material)
djson["geometry"]["material"] = dict()
material.setAttribute("name", "Material")
djson["geometry"]["material"].update({"name": "Material"})

# 写入材料参数
if len(list(materialList.keys())) > 0:
    djson["geometry"]["material"].update({"parameters": dict()})
for k in materialList.keys():
    parameter = doc.createElement("parameter")
    material.appendChild(parameter)
    parameter.setAttribute("name", k)
    parameter.setAttribute("value", f"{materialList[k]}")
    djson["geometry"]["material"]["parameters"].update({k: materialList[k]})

# Detector根节点（World）
detector = doc.createElement("detector")
geometry.appendChild(detector)
djson["geometry"]["detectors"] = []

detector.setAttribute("type", "World")
detector.setAttribute("name", "World")
djson["geometry"]["detectors"].append(dict())
djson["geometry"]["detectors"][-1].update({"type": "World"})
djson["geometry"]["detectors"][-1].update({"name": "World"})

# ===================== 常量定义（完全对齐示例的大写常量）=====================
Cuboid = "Cuboid"
Cylinder = "Cylinder"
Prism = "Prism"
Polyhedra = "Polyhedra"
HolesBoard = "HolesBoard"
Array = "Array"
PMTs = "PMTsR8520"
LXe = "LXe"
GXe = "GXe"
Teflon = "Teflon"
TeflonGas = "TeflonGas"
XenonVeto = "XenonVeto"
XenonDetector = "XenonDetector"
SS304LSteel = "SS304LSteel"
Copper = "Copper"
Vacuum = "Vacuum"

# 文件路径常量（对齐示例的CAD/数据文件拷贝逻辑）
topPMTs = "data/topPMT.txt"
botPMTs = "data/botPMT.txt"
Pipe = "data/Pipe.txt"
Flange = "data/Flange.txt"
topTeflon = "data/topTeflon.txt"
botTeflon = "data/botTeflon.txt"
shaping_rings = "data/shaping_rings.txt"

# ===================== 文件拷贝（对齐示例的shutil.copy逻辑）=====================
# 示例中存在CAD文件拷贝，此处保留结构（若无需拷贝可注释）
# CAD_Pipe = 'CADdata/Pipe.txt'
# CAD_Flange = 'CADdata/Flange.txt'
# shutil.copy(CAD_Pipe, Pipe)
# shutil.copy(CAD_Flange, Flange)

# ===================== PMT排列（对齐示例的PMTArrangement逻辑）=====================
# 若无需生成PMT位置文件，可保留空结构以对齐示例风格
count_pmt = 0
if save_txt:
    # 顶部PMT
    gas_PMT = position_lxe + 0.6 + 2.9 + 1 / 2 * 0.25  # 示例同款计算逻辑
    top = PMTArrangement(mesh_radius, gas_PMT, top=True)
    top.circular()
    top.save(topPMTs, minN=count_pmt)
    count_pmt += top.N

    # 底部PMT
    lxe_PMT = -1 / 2 * lxenon_height
    bot = PMTArrangement(mesh_radius, lxe_PMT, top=False)
    bot.circular()
    bot.save(botPMTs, minN=count_pmt)
    count_pmt += bot.N

# ===================== 世界体积参数（对齐示例）=====================
djson["geometry"]["detectors"][-1].update({"parameters": dict()})
for x in ["x", "y", "z"]:
    parameter = doc.createElement("parameter")
    parameter.setAttribute("name", f"half_{x}")
    parameter.setAttribute("value", f"{world_half_x}*cm")
    detector.appendChild(parameter)
    djson["geometry"]["detectors"][-1]["parameters"].update(
        {f"half_{x}": f"{world_half_x}*cm"}
    )


# ===================== 工具函数（对齐示例的dict_merger）=====================
def dict_merger(dict_a, dict_b):
    dict_c = copy.deepcopy(dict_a)
    dict_c.update(dict_b)
    return dict_c


# ===================== Detector列表构建（核心，完全对齐示例的detectorList风格）=====================
detectorList = [
    # Lead
    {
        "type": Cuboid,
        "name": "Lead",
        "parent": "World",
        "parameters": {
            "width_x": lead_width_x,
            "width_y": lead_width_y,
            "width_z": lead_width_z,
            "material": "G4_Pb",
        },
    },
    # Copper
    {
        "type": Cuboid,
        "name": "Copper",
        "parent": "Lead",
        "parameters": {
            "width_x": copper_width_x,
            "width_y": copper_width_y,
            "width_z": copper_width_z,
            "material": "Copper",
        },
    },
    # InnerPE
    {
        "type": Cuboid,
        "name": "InnerPE",
        "parent": "Copper",
        "parameters": {
            "width_x": inner_pe_width_x,
            "width_y": inner_pe_width_y,
            "width_z": inner_pe_width_z,
            "material": "G4_POLYETHYLENE",
        },
    },
    # Air
    {
        "type": Cuboid,
        "name": "Air",
        "parent": "InnerPE",
        "parameters": {
            "width_x": air_width_x,
            "width_y": air_width_y,
            "width_z": air_width_z,
            "material": "G4_AIR",
        },
    },
    # OuterContainer (外层不锈钢罐侧壁)
    {
        "type": Cylinder,
        "name": "OuterContainer",
        "parent": "Air",
        "parameters": {
            "radius": outer_container_radius,
            "height": outer_container_height,
            "material": SS304LSteel,
            "shift_z": outer_container_shift_z,
            "surface": int(surface),
        },
    },
    # OuterContainerTop (外层不锈钢罐顶盖)
    {
        "type": Cuboid,
        "name": "OuterContainerTop",
        "parent": "Air",
        "parameters": {
            "width_x": outer_container_top_width_x,
            "width_y": outer_container_top_width_y,
            "width_z": outer_container_top_width_z,
            "material": SS304LSteel,
            "shift_z": outer_container_top_shift_z,
            "surface": int(surface),
        },
    },
    # OuterContainerBottom (外层不锈钢罐底部)
    {
        "type": Cylinder,
        "name": "OuterContainerBottom",
        "parent": "Air",
        "parameters": {
            "radius": outer_container_bottom_radius,
            "height": outer_container_bottom_height,
            "material": SS304LSteel,
            "shift_z": outer_container_bottom_shift_z,
            "surface": int(surface),
        },
    },
    # Pipe
    {
        "type": Array,
        "name": "Pipe",
        "parent": "Air",
        "parameters": {
            "objects": "Tube",
            "outer_radius": 19.05,
            "inner_radius": 17.4,
            "sides": str(0),
            "height": 99.3999999999,
            "material": SS304LSteel,
            "source": Pipe,
            "surface": int(surface),
        },
    },
    # Flange
    {
        "type": Array,
        "name": "Flange",
        "parent": "Air",
        "parameters": {
            "objects": "Tube",
            "outer_radius": 34.75,
            "inner_radius": 11.5,
            "sides": str(0),
            "height": 12.6999999999,
            "material": SS304LSteel,
            "source": Flange,
            "surface": int(surface),
        },
    },
    # Vacuum (真空夹层)
    {
        "type": Cylinder,
        "name": "Vacuum",
        "parent": "OuterContainer",
        "parameters": {
            "radius": vacuum_radius,
            "height": vacuum_height,
            "material": Vacuum,
            "shift_z": vacuum_shift_z,
            "surface": int(surface),
        },
    },
    # InnerContainerTop (内层不锈钢罐顶部)
    {
        "type": Cylinder,
        "name": "InnerContainerTop",
        "parent": "Vacuum",
        "parameters": {
            "radius": inner_container_top_radius,
            "height": inner_container_top_height,
            "material": SS304LSteel,
            "shift_z": inner_container_top_shift_z,
            "surface": int(surface),
        },
    },
    # InnerContainerBottom (内层不锈钢罐底部)
    {
        "type": Cylinder,
        "name": "InnerContainerBottom",
        "parent": "Vacuum",
        "parameters": {
            "radius": inner_container_bottom_radius,
            "height": inner_container_bottom_height,
            "material": SS304LSteel,
            "shift_z": inner_container_bottom_shift_z,
            "surface": int(surface),
        },
    },
    # InnerContainer (内层不锈钢罐侧壁)
    {
        "type": Cylinder,
        "name": "InnerContainer",
        "parent": "Vacuum",
        "parameters": {
            "radius": inner_container_radius,
            "height": inner_container_height,
            "material": SS304LSteel,
            "surface": int(surface),
        },
    },
    # OuterGXe (气态氙外层)
    {
        "type": Cylinder,
        "name": "OuterGXe",
        "parent": "InnerContainer",
        "parameters": {
            "radius": outer_gxe_radius,
            "height": outer_gxe_height,
            "material": GXe,
            "shift_z": outer_gxe_shift_z,
            "surface": int(surface),
        },
    },
    # OuterLXe (液态氙外层)
    {
        "type": Cylinder,
        "name": "OuterLXe",
        "parent": "InnerContainer",
        "parameters": {
            "radius": outer_lxe_radius,
            "height": outer_lxe_height,
            "material": LXe,
            "shift_z": outer_lxe_shift_z,
            "surface": int(surface),
        },
        "sd": LXesd,
    },
    # 顶部PMT阵列 (tR8520)
    {
        "type": Array,
        "name": "tR8520",
        "parent": "OuterGXe",
        "parameters": dict_merger(
            {
                "objects": PMTs,
                "physvol": "R8520",
                "source": topPMTs,
                "surface": int(surface),
            },
            pmt_opsurface,
        ),
        "sd": PMTsd,
        "opticalsd": opticalsd,
    },
    # 底部PMT阵列 (bR8520)
    {
        "type": Array,
        "name": "bR8520",
        "parent": "OuterLXe",
        "parameters": dict_merger(
            {
                "objects": PMTs,
                "physvol": "R8520",
                "source": botPMTs,
                "surface": int(surface),
            },
            pmt_opsurface,
        ),
        "sd": PMTsd,
        "opticalsd": opticalsd,
    },
    # Teflon (聚四氟乙烯容器)
    {
        "type": Cylinder,
        "name": "Teflon",
        "parent": "OuterLXe",
        "parameters": {
            "radius": teflon_radius,
            "height": teflon_height,
            "material": Teflon,
            "shift_z": teflon_shift_z,
            "surface": int(surface),
        },
    },
    # Shapingrings (成型环)
    {
        "type": Array,
        "name": "Shapingrings",
        "parent": "OuterLXe",
        "parameters": {
            "objects": "Tube",
            "outer_radius": shaping_rings_outer_radius,
            "inner_radius": shaping_rings_inner_radius,
            "sides": str(0),
            "height": shaping_rings_height,
            "material": Copper,
            "source": shaping_rings,
            "surface": int(surface),
        },
    },
    # lxenon (液态氙主体)
    {
        "type": Cylinder,
        "name": "lxenon",
        "parent": "Teflon",
        "parameters": {
            "radius": lxenon_radius,
            "height": lxenon_height,
            "material": LXe,
            "shift_z": 0,
            "surface": int(surface),
        },
        "sd": LXesd,
    },
    # TeflonGas (气态氙区域聚四氟乙烯)
    {
        "type": Cylinder,
        "name": "TeflonGas",
        "parent": "OuterGXe",
        "parameters": {
            "radius": teflon_gas_radius,
            "height": teflon_gas_height,
            "material": TeflonGas,
            "shift_z": teflon_gas_shift_z,
            "surface": int(surface),
        },
    },
    # gasxenon (气态氙主体)
    {
        "type": Cylinder,
        "name": "gasxenon",
        "parent": "TeflonGas",
        "parameters": {
            "radius": gasxenon_radius,
            "height": gasxenon_height,
            "material": GXe,
            "shift_z": 0,
            "surface": int(surface),
        },
    },
    # TopTeflon (顶部聚四氟乙烯板)
    {
        "type": HolesBoard,
        "name": "TopTeflon",
        "parent": "gasxenon",
        "parameters": {
            "radius": top_teflon_radius,
            "height": top_teflon_height,
            "width_x": top_teflon_width_x,
            "sides": str(0),
            "material": TeflonGas,
            "shift_z": top_teflon_shift_z,
            "source": topTeflon,
            "surface": int(surface),
        },
    },
    # BotTeflon (底部聚四氟乙烯板)
    {
        "type": HolesBoard,
        "name": "BotTeflon",
        "parent": "lxenon",
        "parameters": {
            "radius": bot_teflon_radius,
            "height": bot_teflon_height,
            "width_x": bot_teflon_width_x,
            "sides": str(0),
            "material": Teflon,
            "shift_z": bot_teflon_shift_z,
            "source": botTeflon,
            "surface": int(surface),
        },
    },
]

# ===================== 电极列表（对齐示例的electrodes逻辑）=====================
electrodes = [
    {
        "name": "Anode",
        "parent": "gasxenon",
        "parameters": {
            "radius": mesh_radius,
            "wire_diameter": mesh_wire_diameter,
            "wire_pitch": mesh_wire_pitch,
            "sides": str(0),
            "material": SS304LSteel,
            "type": "dielectric_metal",
            "surface": int(surface),
            "shift_z": anode_shift_z,
        },
    },
    {
        "name": "Gate",
        "parent": "lxenon",
        "parameters": {
            "radius": mesh_radius,
            "wire_diameter": mesh_wire_diameter,
            "wire_pitch": mesh_wire_pitch,
            "sides": str(0),
            "material": SS304LSteel,
            "type": "dielectric_metal",
            "surface": int(surface),
            "shift_z": gate_shift_z,
        },
    },
    {
        "name": "Cathode",
        "parent": "lxenon",
        "parameters": {
            "radius": mesh_radius,
            "wire_diameter": mesh_wire_diameter,
            "wire_pitch": mesh_wire_pitch,
            "sides": str(0),
            "material": SS304LSteel,
            "type": "dielectric_metal",
            "surface": int(surface),
            "shift_z": cathode_shift_z,
        },
    },
    {
        "name": "BottomScreening",
        "parent": "lxenon",
        "parameters": {
            "radius": mesh_radius,
            "wire_diameter": mesh_wire_diameter,
            "wire_pitch": 5.774,  # 底部屏蔽专属线间距
            "sides": str(0),
            "material": SS304LSteel,
            "type": "dielectric_metal",
            "surface": int(surface),
            "shift_z": bottom_screening_shift_z,
        },
    },
]

# 为电极添加类型（对齐示例）
for electrode in electrodes:
    electrode.update({"type": "MeshGrid"})

# 合并探测器列表和电极列表
detectorList += electrodes

# 强制敏感探测器（对齐示例）
if force_sd:
    for d in detectorList:
        d.update({"sd": True})

# ===================== 体积参数定义（完全对齐示例）=====================
volume = {"soliname": "Solid", "logivol": "Log", "physvol": ""}

# ===================== 写入所有Detector节点（核心循环，对齐示例）=====================
for d in detectorList:
    detector = doc.createElement("detector")
    geometry.appendChild(detector)
    detector.setAttribute("type", d["type"])
    detector.setAttribute("name", d["name"])
    detector.setAttribute("parent", d["parent"])

    djson["geometry"]["detectors"].append(dict())
    djson["geometry"]["detectors"][-1].update({"type": d["type"]})
    djson["geometry"]["detectors"][-1].update({"name": d["name"]})
    djson["geometry"]["detectors"][-1].update({"parent": d["parent"]})
    djson["geometry"]["detectors"][-1].update({"parameters": dict()})

    # 写入体积参数（soliname/logivol/physvol）
    for k in volume.keys():
        parameter = doc.createElement("parameter")
        detector.appendChild(parameter)
        parameter.setAttribute("name", k)
        name = d["parameters"].get("physvol", d["name"])
        parameter.setAttribute("value", f"{name}{volume[k]}")
        djson["geometry"]["detectors"][-1]["parameters"].update(
            {k: f"{name}{volume[k]}"}
        )

    # 写入自定义参数
    for x in d["parameters"].keys():
        if x == "physvol":
            continue
        is_surface = d["parameters"].get("surface", False)
        if not is_surface and (x in ["model", "finish", "type", "alpha"]):
            continue

        parameter = doc.createElement("parameter")
        detector.appendChild(parameter)
        parameter.setAttribute("name", f"{x}")

        if isinstance(d["parameters"][x], str):
            parameter.setAttribute("value", f"{d['parameters'][x]}")
            djson["geometry"]["detectors"][-1]["parameters"].update(
                {f"{x}": f"{d['parameters'][x]}"}
            )
        elif isinstance(d["parameters"][x], bool):
            parameter.setAttribute("value", f"{int(d['parameters'][x])}")
            djson["geometry"]["detectors"][-1]["parameters"].update(
                {f"{x}": f"{int(d['parameters'][x])}"}
            )
        else:
            # 尺寸参数统一加cm单位（对齐示例的单位处理）
            if x in [
                "radius",
                "height",
                "width_x",
                "width_y",
                "width_z",
                "outer_radius",
                "inner_radius",
                "shift_z",
                "wire_diameter",
                "wire_pitch",
            ]:
                parameter.setAttribute("value", f"{d['parameters'][x]}*mm")
                djson["geometry"]["detectors"][-1]["parameters"].update(
                    {f"{x}": f"{d['parameters'][x]}*mm"}
                )
            else:
                parameter.setAttribute("value", f"{d['parameters'][x]}")
                djson["geometry"]["detectors"][-1]["parameters"].update(
                    {f"{x}": f"{d['parameters'][x]}"}
                )

    # 敏感探测器参数
    if d.pop("sd", None):
        parameter = doc.createElement("parameter")
        detector.appendChild(parameter)
        parameter.setAttribute("name", "sendname")
        name = d["name"]
        parameter.setAttribute("value", f"{name}")
        djson["geometry"]["detectors"][-1]["parameters"].update({"sendname": f"{name}"})

        if d.pop("opticalsd", False):
            parameter = doc.createElement("parameter")
            detector.appendChild(parameter)
            parameter.setAttribute("name", "opticalsd")
            parameter.setAttribute("value", "1")
            djson["geometry"]["detectors"][-1]["parameters"].update({"opticalsd": "1"})

        if enable_track:
            parameter = doc.createElement("parameter")
            detector.appendChild(parameter)
            parameter.setAttribute("name", "entrack")
            parameter.setAttribute("value", "1")
            djson["geometry"]["detectors"][-1]["parameters"].update({"entrack": "1"})

    # 重叠检查
    if check_overlap:
        parameter = doc.createElement("parameter")
        detector.appendChild(parameter)
        parameter.setAttribute("name", "check_overlap")
        parameter.setAttribute("value", "1")
        djson["geometry"]["detectors"][-1]["parameters"].update({"check_overlap": "1"})

# ===================== Physics节点（对齐示例）=====================
physics = doc.createElement("physics")
root.appendChild(physics)
djson["physics"] = dict()
physics.setAttribute("name", physics_name)
djson["physics"].update({"name": physics_name})

parameter = doc.createElement("parameter")
physics.appendChild(parameter)
djson["physics"].update({"parameters": dict()})
parameter.setAttribute("name", "cutlength")
parameter.setAttribute("value", f"{cutlength}*mm")
djson["physics"]["parameters"].update({"cutlength": f"{cutlength}*mm"})

# ===================== Generator节点（对齐示例）=====================
generator = doc.createElement("generator")
root.appendChild(generator)
djson["generator"] = dict()
generator.setAttribute("name", generator_name)
djson["generator"].update({"name": generator_name})

djson["generator"].update({"parameters": dict()})

# Muon生成器参数
if gen == "muon" and not optical:
    parameter = doc.createElement("parameter")
    generator.appendChild(parameter)
    parameter.setAttribute("name", "shielding_x")
    parameter.setAttribute("value", f"{muon_x}*cm")
    djson["generator"]["parameters"].update({"shielding_x": f"{muon_x}*cm"})

    parameter = doc.createElement("parameter")
    generator.appendChild(parameter)
    parameter.setAttribute("name", "shielding_z")
    parameter.setAttribute("value", f"{muon_z}*cm")
    djson["generator"]["parameters"].update({"shielding_z": f"{muon_z}*cm"})

    parameter = doc.createElement("parameter")
    generator.appendChild(parameter)
    parameter.setAttribute("name", "E_low")
    parameter.setAttribute("value", muon_e_low)
    djson["generator"]["parameters"].update({"E_low": muon_e_low})

# ===================== Analysis节点（对齐示例）=====================
analysis = doc.createElement("analysis")
root.appendChild(analysis)
djson["analysis"] = dict()
analysis.setAttribute("name", analysis_name)
djson["analysis"].update({"name": analysis_name})

djson["analysis"].update({"parameters": dict()})
for k in analysisList.keys():
    parameter = doc.createElement("parameter")
    analysis.appendChild(parameter)
    parameter.setAttribute("name", k)
    parameter.setAttribute("value", f"{analysisList[k]}")
    djson["analysis"]["parameters"].update({k: analysisList[k]})

# ===================== 写入文件（对齐示例）=====================
fp = open(fopt, "w")
doc.writexml(fp, indent="  ", addindent="  ", newl="\n", encoding="UTF-8")

with open(os.path.splitext(fopt)[0] + ".json", "w") as fp:
    json.dump(djson, fp, indent="\t")
