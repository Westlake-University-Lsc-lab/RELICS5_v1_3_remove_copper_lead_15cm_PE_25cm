#!/usr/bin/python3
import argparse
import copy
import json
import os
from xml.dom.minidom import Document

from arrangement import PMTArrangement, TankArrangement

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
    "--sampling-mode",
    dest="sampling_mode",
    type=bool,
    action="store",
    default=False,
    help="Enable sampling mode",
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
parser.add_argument(
    "--disable_energy_depo", action="store_true", help="Disable energy deposition"
)
parser.add_argument(
    "--disable_primary_particle",
    action="store_true",
    help="Disable primary particle recording",
)

args = parser.parse_args()

number: str = args.run_number
fipt: str = args.ipt
fopt: str = args.opt
gen: str = args.generator
cutlength: float = args.cutlength

enable_track: bool = args.enable_track
force_sd: bool = args.force_sd
check_overlap: bool = args.check_overlap
get_geo_mass: bool = args.get_geo_mass
save_txt: bool = args.save_txt
optical: bool = args.optical
disable_energy_depo: bool = args.disable_energy_depo
disable_primary_particle: bool = args.disable_primary_particle
sampling_mode: bool = args.sampling_mode

if sampling_mode:
    disable_energy_depo = True
    enable_track = True

with open(fipt) as f:
    params = json.load(f)

# ===================== 完整参数加载与校验（原代码全部保留）=====================
# 从参数文件加载参数
radius_outer_gxe = params["radius_outer_gxe"]
assert radius_outer_gxe >= 0, (
    f"参数 radius_outer_gxe = {radius_outer_gxe} 非法，半径不能为负数"
)
height_outer_gxe = params["height_outer_gxe"]
assert height_outer_gxe >= 0, (
    f"参数 height_outer_gxe = {height_outer_gxe} 非法，高度不能为负数"
)
shift_z_outer_gxe = params["shift_z_outer_gxe"]  # 位移可正可负，不校验

radius_outer_lxe = params["radius_outer_lxe"]
assert radius_outer_lxe >= 0, (
    f"参数 radius_outer_lxe = {radius_outer_lxe} 非法，半径不能为负数"
)
height_outer_lxe = params["height_outer_lxe"]
assert height_outer_lxe >= 0, (
    f"参数 height_outer_lxe = {height_outer_lxe} 非法，高度不能为负数"
)
shift_z_outer_lxe = params["shift_z_outer_lxe"]  # 位移可正可负，不校验

radius_lxe = params["radius_lxe"]
assert radius_lxe >= 0, f"参数 radius_lxe = {radius_lxe} 非法，半径不能为负数"
height_lxe = params["height_lxe"]
assert height_lxe >= 0, f"参数 height_lxe = {height_lxe} 非法，高度不能为负数"
shift_z_lxe = params["shift_z_lxe"]  # 位移可正可负，不校验

radius_gxe = params["radius_gxe"]
assert radius_gxe >= 0, f"参数 radius_gxe = {radius_gxe} 非法，半径不能为负数"
height_gxe = params["height_gxe"]
assert height_gxe >= 0, f"参数 height_gxe = {height_gxe} 非法，高度不能为负数"
shift_z_gxe = params["shift_z_gxe"]  # 位移可正可负，不校验

radius_teflon = params["radius_teflon"]
assert radius_teflon >= 0, f"参数 radius_teflon = {radius_teflon} 非法，半径不能为负数"
height_teflon = params["height_teflon"]
assert height_teflon >= 0, f"参数 height_teflon = {height_teflon} 非法，高度不能为负数"
shift_z_teflon = params["shift_z_teflon"]  # 位移可正可负，不校验

radius_teflon_gas = params["radius_teflon_gas"]
assert radius_teflon_gas >= 0, (
    f"参数 radius_teflon_gas = {radius_teflon_gas} 非法，半径不能为负数"
)
height_teflon_gas = params["height_teflon_gas"]
assert height_teflon_gas >= 0, (
    f"参数 height_teflon_gas = {height_teflon_gas} 非法，高度不能为负数"
)
shift_z_teflon_gas = params["shift_z_teflon_gas"]  # 位移可正可负，不校验

radius_top_teflon = params["radius_top_teflon"]
assert radius_top_teflon >= 0, (
    f"参数 radius_top_teflon = {radius_top_teflon} 非法，半径不能为负数"
)
height_top_teflon = params["height_top_teflon"]
assert height_top_teflon >= 0, (
    f"参数 height_top_teflon = {height_top_teflon} 非法，高度不能为负数"
)
width_x_top_teflon = params["width_x_top_teflon"]
assert width_x_top_teflon >= 0, (
    f"参数 width_x_top_teflon = {width_x_top_teflon} 非法，宽度不能为负数"
)
shift_z_top_teflon = params["shift_z_top_teflon"]  # 位移可正可负，不校验

radius_bot_teflon = params["radius_bot_teflon"]
assert radius_bot_teflon >= 0, (
    f"参数 radius_bot_teflon = {radius_bot_teflon} 非法，半径不能为负数"
)
height_bot_teflon = params["height_bot_teflon"]
assert height_bot_teflon >= 0, (
    f"参数 height_bot_teflon = {height_bot_teflon} 非法，高度不能为负数"
)
width_x_bot_teflon = params["width_x_bot_teflon"]
assert width_x_bot_teflon >= 0, (
    f"参数 width_x_bot_teflon = {width_x_bot_teflon} 非法，宽度不能为负数"
)
shift_z_bot_teflon = params["shift_z_bot_teflon"]  # 位移可正可负，不校验

# 电极参数
radius_electrode = params["radius_electrode"]
assert radius_electrode >= 0, (
    f"参数 radius_electrode = {radius_electrode} 非法，电极半径不能为负数"
)
wire_diameter = params["wire_diameter"]
assert wire_diameter >= 0, (
    f"参数 wire_diameter = {wire_diameter} 非法，导线直径不能为负数"
)
shift_z_anode = params["shift_z_anode"]  # 位移可正可负，不校验
wire_pitch_anode = params["wire_pitch_anode"]
assert wire_pitch_anode >= 0, (
    f"参数 wire_pitch_anode = {wire_pitch_anode} 非法，导线间距不能为负数"
)
shift_z_gate = params["shift_z_gate"]  # 位移可正可负，不校验
wire_pitch_gate = params["wire_pitch_gate"]
assert wire_pitch_gate >= 0, (
    f"参数 wire_pitch_gate = {wire_pitch_gate} 非法，导线间距不能为负数"
)
shift_z_cathode = params["shift_z_cathode"]  # 位移可正可负，不校验
wire_pitch_cathode = params["wire_pitch_cathode"]
assert wire_pitch_cathode >= 0, (
    f"参数 wire_pitch_cathode = {wire_pitch_cathode} 非法，导线间距不能为负数"
)
shift_z_bottom_screening = params["shift_z_bottom_screening"]  # 位移可正可负，不校验
wire_pitch_bottom_screening = params["wire_pitch_bottom_screening"]
assert wire_pitch_bottom_screening >= 0, (
    f"参数 wire_pitch_bottom_screening = {wire_pitch_bottom_screening} 非法，导线间距不能为负数"
)

# 屏蔽参数
lead_width_x = params["lead_width_x"]
assert lead_width_x >= 0, (
    f"参数 lead_width_x = {lead_width_x} 非法，铅屏蔽X方向宽度不能为负数"
)
lead_width_y = params["lead_width_y"]
assert lead_width_y >= 0, (
    f"参数 lead_width_y = {lead_width_y} 非法，铅屏蔽Y方向宽度不能为负数"
)
lead_width_z = params["lead_width_z"]
assert lead_width_z >= 0, (
    f"参数 lead_width_z = {lead_width_z} 非法，铅屏蔽Z方向宽度不能为负数"
)

copper_width_x = params["copper_width_x"]
assert copper_width_x >= 0, (
    f"参数 copper_width_x = {copper_width_x} 非法，铜屏蔽X方向宽度不能为负数"
)
copper_width_y = params["copper_width_y"]
assert copper_width_y >= 0, (
    f"参数 copper_width_y = {copper_width_y} 非法，铜屏蔽Y方向宽度不能为负数"
)
copper_width_z = params["copper_width_z"]
assert copper_width_z >= 0, (
    f"参数 copper_width_z = {copper_width_z} 非法，铜屏蔽Z方向宽度不能为负数"
)

inner_pe_width_x = params["inner_pe_width_x"]
assert inner_pe_width_x >= 0, (
    f"参数 inner_pe_width_x = {inner_pe_width_x} 非法，内层PE屏蔽X方向宽度不能为负数"
)
inner_pe_width_y = params["inner_pe_width_y"]
assert inner_pe_width_y >= 0, (
    f"参数 inner_pe_width_y = {inner_pe_width_y} 非法，内层PE屏蔽Y方向宽度不能为负数"
)
inner_pe_width_z = params["inner_pe_width_z"]
assert inner_pe_width_z >= 0, (
    f"参数 inner_pe_width_z = {inner_pe_width_z} 非法，内层PE屏蔽Z方向宽度不能为负数"
)

# 真空参数
radius_vacuum = params["radius_vacuum"]
assert radius_vacuum >= 0, (
    f"参数 radius_vacuum = {radius_vacuum} 非法，真空层半径不能为负数"
)
height_vacuum = params["height_vacuum"]
assert height_vacuum >= 0, (
    f"参数 height_vacuum = {height_vacuum} 非法，真空层高度不能为负数"
)
shift_z_vacuum = params["shift_z_vacuum"]  # 位移可正可负，不校验

# 成形环参数
outer_radius_shapingrings = params["outer_radius_shapingrings"]
assert outer_radius_shapingrings >= 0, (
    f"参数 outer_radius_shapingrings = {outer_radius_shapingrings} 非法，成形环外半径不能为负数"
)
inner_radius_shapingrings = params["inner_radius_shapingrings"]
assert inner_radius_shapingrings >= 0, (
    f"参数 inner_radius_shapingrings = {inner_radius_shapingrings} 非法，成形环内半径不能为负数"
)

# 新增参数加载
height_shapingrings = params["height_shapingrings"]
number_shapingrings = params["number_shapingrings"]
pitch_shapingrings = params["pitch_shapingrings"]
pmt_hole = params["pmt_hole"]
outer_container_radius = params["outer_container_radius"]
outer_container_height = params["outer_container_height"]
outer_container_shift_z = params["outer_container_shift_z"]
outer_container_top_width_x = params["outer_container_top_width_x"]
outer_container_top_width_y = params["outer_container_top_width_y"]
outer_container_top_height = params["outer_container_top_height"]
outer_container_top_shift_z = params["outer_container_top_shift_z"]
outer_container_bottom_radius = params["outer_container_bottom_radius"]
outer_container_bottom_height = params["outer_container_bottom_height"]
outer_container_bottom_shift_z = params["outer_container_bottom_shift_z"]
pipe_outer_radius = params["pipe_outer_radius"]
pipe_inner_radius = params["pipe_inner_radius"]
pipe_height = params["pipe_height"]
flange_outer_radius = params["flange_outer_radius"]
flange_inner_radius = params["flange_inner_radius"]
flange_height = params["flange_height"]
inner_container_radius = params["inner_container_radius"]
inner_container_height = params["inner_container_height"]
inner_container_top_radius = params["inner_container_top_radius"]
inner_container_top_height = params["inner_container_top_height"]
inner_container_top_shift_z = params["inner_container_top_shift_z"]
inner_container_bottom_radius = params["inner_container_bottom_radius"]
inner_container_bottom_height = params["inner_container_bottom_height"]
inner_container_bottom_shift_z = params["inner_container_bottom_shift_z"]
air_width_x = params["air_width_x"]
air_width_y = params["air_width_y"]
air_width_z = params["air_width_z"]
muon_x = params["muon_x"]
muon_z = params["muon_z"]
muon_e_low = params["muon_e_low"]
CRN_x = params["CRN_x"]
CRN_z = params["CRN_z"]


# ===================== 辅助函数（原代码全部保留）=====================
# 处理参数值，移除不需要的单位后缀
def format_parameter_value(param_name, value):
    # 不需要单位的参数列表
    no_unit_params = {
        "material",
        "type",
        "window_partner",
        "objects",
        "sendname",
        "base_type",
        "casing_finish",
        "casing_type",
        "window_finish",
        "photocathode_finish",
        "source",
        "surface",
        "check_overlap",
        "opticalsd",
        "entrack",
        "window_order",
    }

    # 对于不需要单位的参数，移除可能的*mm后缀
    if param_name in no_unit_params:
        if isinstance(value, str) and "*mm" in value:
            return value.replace("*mm", "")
        return str(value)

    # 对于需要单位的参数，确保格式正确
    if isinstance(value, (int, float)):
        return f"{value}*mm"

    return str(value)


def dict_merger(dict_a, dict_b):
    dict_c = copy.deepcopy(dict_a)
    for key, value in dict_b.items():
        if isinstance(value, dict):
            if key in dict_c:
                dict_c[key] = dict_merger(dict_c[key], value)
            else:
                dict_c[key] = copy.deepcopy(value)
        else:
            # 处理参数值，应用格式转换
            if "." in key:
                param_name = key.split(".")[1]
                dict_c[key] = format_parameter_value(param_name, value)
            else:
                dict_c[key] = value
    return dict_c


# 创建探测器节点的辅助函数
def create_detector_node(parent, det_type, name, parent_name, params):
    det_node = doc.createElement("detector")
    det_node.setAttribute("type", det_type)
    det_node.setAttribute("name", name)
    det_node.setAttribute("parent", parent_name)
    parent.appendChild(det_node)

    for param_name, value in params.items():
        formatted_value = format_parameter_value(param_name, value)
        param_node = doc.createElement("parameter")
        param_node.setAttribute("name", param_name)
        param_node.setAttribute("value", formatted_value)
        det_node.appendChild(param_node)

    return det_node


# ===================== Generator/Physics/Analysis 配置（按范本重构）=====================
if optical:
    # 光学模式：固定Generator/Physics/Analysis名称，无Generator参数
    generator_name = "ConfineGenerator"
    physics_name = "RelicsOpticalPhysics"
    analysis_name = "RelicsOpticalAnalysis"
    seed = int(number)
    generator_params = []  # 光学模式无Generator参数
else:
    # 非光学模式：按gen参数映射Generator名称
    physics_name = "PandaXPhysics"
    analysis_name = "PandaXAnalysis"
    seed = 0

    if gen == "muon":
        generator_name = "MuonGenerator"
        generator_params = [
            ("shielding_x", f"{muon_x}*cm"),
            ("shielding_z", f"{muon_z}*cm"),
            ("E_low", f"{muon_e_low}*GeV"),
        ]
    elif gen == "neutron" or gen == "gamma":
        generator_name = "SimpleGPSGenerator"
        generator_params = [
            # ("particle", gen),
            # ("energy_min", "0.01*MeV" if gen == 'neutron' else "0.001*MeV"),
            # ("energy_max", "10*MeV")
        ]
    elif gen == "material":
        generator_name = "ConfineGenerator"
        generator_params = []
    elif gen == "CRN":
        generator_name = "NeutronGenerator"
        generator_params = [
            ("shielding_x", f"{CRN_x}*cm"),
            ("shielding_z", f"{CRN_z}*cm"),
        ]
    elif gen == "sample":
        generator_name = "SampleGenerator"
        generator_params = [
            {
                "db_path": "/root/RELICS5_v1_3_remove_copper_lead_15cm_PE_25cm/data/flux_neutron_ON.db",
                "table": "samples",
            }
        ]

# ===================== XML文档构建（几何部分完全保留）=====================
# 创建XML文档
doc = Document()
root = doc.createElement("BambooMC")
doc.appendChild(root)

# 添加run节点
run_node = doc.createElement("run")
run_node.setAttribute("number", number)
root.appendChild(run_node)

# 添加geometry节点
geometry_node = doc.createElement("geometry")
root.appendChild(geometry_node)

# 添加material节点
material_node = doc.createElement("material")
material_node.setAttribute("name", "Material")
geometry_node.appendChild(material_node)

# 材料参数
material_params = [
    ("LXe_SCINTILLATIONYIELD", "1000000."),
    ("LXe_RESOLUTIONSCALE", "0."),
    ("LXe_ABSLENGTH", "6.91 5000 6.98 5000 7.05 5000"),
    ("GXe_ABSLENGTH", "6.91 20000 6.98 20000 7.05 20000"),
    ("SS304LSteel_REFLECTIVITY", "1 0.57 5 0.57"),
    ("Quartz_RINDEX", "1 1.70 6.9 1.70 6.91 1.70 6.98 1.70 7.05 1.70"),
    ("Teflon_REFLECTIVITY", "6.91 0.95 6.98 0.95 7.05 0.95"),
    ("TeflonGas_REFLECTIVITY", "6.91 0.70 6.98 0.70 7.05 0.70"),
    ("Teflon_SPECULARLOBECONSTANT", "6.91 0.01 6.98 0.01 7.05 0.01"),
    ("TeflonGas_SPECULARLOBECONSTANT", "6.91 0.01 6.98 0.01 7.05 0.01"),
    ("LXe_RINDEX", "6.91 1.69 6.98 1.69 7.05 1.69"),
]

for name, value in material_params:
    param_node = doc.createElement("parameter")
    param_node.setAttribute("name", name)
    param_node.setAttribute("value", value)
    material_node.appendChild(param_node)

# World探测器
create_detector_node(
    geometry_node,
    "World",
    "World",
    "",
    {"half_x": "3000*cm", "half_y": "500*cm", "half_z": "500*cm"},
)
if sampling_mode:
    # AirShell探测器
    create_detector_node(
        geometry_node,
        "HollowCuboid",
        "AirShell",
        "World",
        {
            "soliname": "AirShellSolid",
            "logivol": "AirShellLog",
            "physvol": "AirShell",
            "width_x": "200*cm",
            "width_y": "200*cm",
            "width_z": "250*cm",
            "thickness": "10*cm",
            "material": "G4_AIR",
            "check_overlap": "1",
            "entrack": "1",
            "sendname": "AirShell",
        },
    )

# Lead探测器
create_detector_node(
    geometry_node,
    "Cuboid",
    "Lead",
    "World",
    {
        "soliname": "LeadSolid",
        "logivol": "LeadLog",
        "physvol": "Lead",
        "width_x": f"{lead_width_x}*mm",
        "width_y": f"{lead_width_y}*mm",
        "width_z": f"{lead_width_z}*mm",
        "material": "G4_Pb",
        "check_overlap": "1",
        # "sendname": "Lead"
    },
)

# # Copper探测器
# create_detector_node(geometry_node, "Cuboid", "Copper", "Lead", {
#     "soliname": "CopperSolid",
#     "logivol": "CopperLog",
#     "physvol": "Copper",
#     "width_x": f"{copper_width_x}*mm",
#     "width_y": f"{copper_width_y}*mm",
#     "width_z": f"{copper_width_z}*mm",
#     "material": "Copper",
#     "check_overlap": "1",
#     # "sendname": "Copper"
# })

# InnerPE探测器
create_detector_node(
    geometry_node,
    "Cuboid",
    "InnerPE",
    "Lead",
    {
        "soliname": "InnerPESolid",
        "logivol": "InnerPELog",
        "physvol": "InnerPE",
        "width_x": f"{inner_pe_width_x}*mm",
        "width_y": f"{inner_pe_width_y}*mm",
        "width_z": f"{inner_pe_width_z}*mm",
        "material": "G4_POLYETHYLENE",
        "check_overlap": "1",
        # "sendname": "InnerPE"
    },
)

# Air探测器
create_detector_node(
    geometry_node,
    "Cuboid",
    "Air",
    "InnerPE",
    {
        "soliname": "AirSolid",
        "logivol": "AirLog",
        "physvol": "Air",
        "width_x": f"{air_width_x}*mm",
        "width_y": f"{air_width_y}*mm",
        "width_z": f"{air_width_z}*mm",
        "material": "G4_AIR",
        "check_overlap": "1",
    },
)

# OuterContainer探测器
create_detector_node(
    geometry_node,
    "Cylinder",
    "OuterContainer",
    "Air",
    {
        "soliname": "OuterContainerSolid",
        "logivol": "OuterContainerLog",
        "physvol": "OuterContainer",
        "radius": f"{outer_container_radius}*mm",
        "height": f"{outer_container_height}*mm",
        "material": "SS304LSteel",
        "shift_z": f"{outer_container_shift_z}*mm",
        "surface": "0",
        "check_overlap": "1",
    },
)

# OuterContainerTop探测器
create_detector_node(
    geometry_node,
    "Cuboid",
    "OuterContainerTop",
    "Air",
    {
        "soliname": "OuterContainerTopSolid",
        "logivol": "OuterContainerLog",
        "physvol": "OuterContainerTop",
        "width_x": f"{outer_container_top_width_x}*mm",
        "width_y": f"{outer_container_top_width_y}*mm",
        "width_z": f"{outer_container_top_height}*mm",
        "material": "SS304LSteel",
        "shift_z": f"{outer_container_top_shift_z}*mm",
        "surface": "1",
        "check_overlap": "1",
    },
)

# OuterContainerBottom探测器
create_detector_node(
    geometry_node,
    "Cylinder",
    "OuterContainerBottom",
    "Air",
    {
        "soliname": "OuterContainerBottomSolid",
        "logivol": "OuterContainerLog",
        "physvol": "OuterContainerBottom",
        "radius": f"{outer_container_bottom_radius}*mm",
        "height": f"{outer_container_bottom_height}*mm",
        "material": "SS304LSteel",
        "shift_z": f"{outer_container_bottom_shift_z}*mm",
        "surface": "1",
        "check_overlap": "1",
    },
)

# Pipe探测器
create_detector_node(
    geometry_node,
    "Array",
    "Pipe",
    "Air",
    {
        "soliname": "PipeSolid",
        "logivol": "PipeLog",
        "physvol": "Pipe",
        "objects": "Tube",
        "outer_radius": f"{pipe_outer_radius}*mm",
        "inner_radius": f"{pipe_inner_radius}*mm",
        "sides": "0",
        "height": f"{pipe_height}*mm",
        "material": "SS304LSteel",
        "source": "data/Pipe.txt",
        "check_overlap": "1",
    },
)

# Flange探测器
create_detector_node(
    geometry_node,
    "Array",
    "Flange",
    "Air",
    {
        "soliname": "FlangeSolid",
        "logivol": "FlangeLog",
        "physvol": "Flange",
        "objects": "Tube",
        "outer_radius": f"{flange_outer_radius}*mm",
        "inner_radius": f"{flange_inner_radius}*mm",
        "sides": "0",
        "height": f"{flange_height}*mm",
        "material": "Flange",
        "source": "data/Flange.txt",
        "check_overlap": "1",
    },
)

# Vacuum探测器
create_detector_node(
    geometry_node,
    "Cylinder",
    "Vacuum",
    "OuterContainer",
    {
        "soliname": "VacuumSolid",
        "logivol": "VacuumLog",
        "physvol": "Vacuum",
        "radius": f"{radius_vacuum}*mm",
        "height": f"{height_vacuum}*mm",
        "material": "Vacuum",
        "shift_z": f"{shift_z_vacuum}*mm",
        "surface": "0",
        "check_overlap": "1",
    },
)

# InnerContainerTop探测器
create_detector_node(
    geometry_node,
    "Cylinder",
    "InnerContainerTop",
    "Vacuum",
    {
        "soliname": "InnerContainerTopSolid",
        "logivol": "InnerContainerLog",
        "physvol": "InnerContainerTop",
        "radius": f"{inner_container_top_radius}*mm",
        "height": f"{inner_container_top_height}*mm",
        "shift_z": f"{inner_container_top_shift_z}*mm",
        "material": "SS304LSteel",
        "surface": "0",
        "check_overlap": "1",
    },
)

# InnerContainerBottom探测器
create_detector_node(
    geometry_node,
    "Cylinder",
    "InnerContainerBottom",
    "Vacuum",
    {
        "soliname": "InnerContainerBottomSolid",
        "logivol": "InnerContainerLog",
        "physvol": "InnerContainerBottom",
        "radius": f"{inner_container_bottom_radius}*mm",
        "height": f"{inner_container_bottom_height}*mm",
        "shift_z": f"{inner_container_bottom_shift_z}*mm",
        "material": "SS304LSteel",
        "surface": "0",
        "check_overlap": "1",
    },
)

# InnerContainer探测器
create_detector_node(
    geometry_node,
    "Cylinder",
    "InnerContainer",
    "Vacuum",
    {
        "soliname": "InnerContainerSolid",
        "logivol": "InnerContainerLog",
        "physvol": "InnerContainer",
        "radius": f"{inner_container_radius}*mm",
        "height": f"{inner_container_height}*mm",
        "material": "SS304LSteel",
        "surface": "0",
        "check_overlap": "1",
    },
)

# OuterGXe探测器
create_detector_node(
    geometry_node,
    "Cylinder",
    "OuterGXe",
    "InnerContainer",
    {
        "soliname": "OuterGXeSolid",
        "logivol": "OuterGXeLog",
        "physvol": "OuterGXe",
        "radius": f"{radius_outer_gxe}*mm",
        "height": f"{height_outer_gxe}*mm",
        "material": "GXe",
        "shift_z": f"{shift_z_outer_gxe}*mm",
        "surface": "0",
        "check_overlap": "1",
    },
)

# OuterLXe探测器
create_detector_node(
    geometry_node,
    "Cylinder",
    "OuterLXe",
    "InnerContainer",
    {
        "soliname": "OuterLXeSolid",
        "logivol": "OuterLXeLog",
        "physvol": "OuterLXe",
        "radius": f"{radius_outer_lxe}*mm",
        "height": f"{height_outer_lxe}*mm",
        "material": "LXe",
        "shift_z": f"{shift_z_outer_lxe}*mm",
        "surface": "0",
        "check_overlap": "1",
        "sendname": "OuterLXe",
    }
    if not sampling_mode
    else {
        "soliname": "OuterLXeSolid",
        "logivol": "OuterLXeLog",
        "physvol": "OuterLXe",
        "radius": f"{radius_outer_lxe}*mm",
        "height": f"{height_outer_lxe}*mm",
        "material": "LXe",
        "shift_z": f"{shift_z_outer_lxe}*mm",
        "surface": "0",
        "check_overlap": "1",
    },
)

# tR8520探测器
create_detector_node(
    geometry_node,
    "Array",
    "tR8520",
    "OuterGXe",
    {
        "soliname": "R8520Solid",
        "logivol": "R8520Log",
        "physvol": "R8520",
        "objects": "PMTsR8520",
        "source": "data/topPMT.txt",
        "base_type": "dielectric_metal",
        "casing_finish": "polished",
        "casing_type": "dielectric_metal",
        "window_partner": "parent",
        "window_finish": "polished",
        "window_order": "1",
        "photocathode_finish": "polished",
        "opticalsd": "1",
        "entrack": "1",
        "check_overlap": "1",
    },
)

# bR8520探测器
create_detector_node(
    geometry_node,
    "Array",
    "bR8520",
    "OuterLXe",
    {
        "soliname": "R8520Solid",
        "logivol": "R8520Log",
        "physvol": "R8520",
        "objects": "PMTsR8520",
        "source": "data/botPMT.txt",
        "base_type": "dielectric_metal",
        "casing_finish": "polished",
        "casing_type": "dielectric_metal",
        "window_partner": "parent",
        "window_finish": "polished",
        "window_order": "1",
        "photocathode_finish": "polished",
        "opticalsd": "1",
        "entrack": "1",
        "check_overlap": "1",
    },
)

# Teflon探测器
create_detector_node(
    geometry_node,
    "Cylinder",
    "Teflon",
    "OuterLXe",
    {
        "soliname": "TeflonSolid",
        "logivol": "TeflonLog",
        "physvol": "Teflon",
        "radius": f"{radius_teflon}*mm",
        "height": f"{height_teflon}*mm",
        "material": "Teflon",
        "shift_z": f"{shift_z_teflon}*mm",
        "surface": "1",
        "check_overlap": "1",
    },
)

# Shapingrings探测器
create_detector_node(
    geometry_node,
    "Array",
    "Shapingrings",
    "OuterLXe",
    {
        "soliname": "ShapingringsSolid",
        "logivol": "ShapingringsLog",
        "physvol": "Shapingrings",
        "objects": "Tube",
        "outer_radius": f"{outer_radius_shapingrings}*mm",
        "inner_radius": f"{inner_radius_shapingrings}*mm",
        "height": f"{height_shapingrings}*mm",
        "material": "Copper",
        "surface": "0",
        "source": "data/shaping_rings.txt",
        "check_overlap": "1",
    },
)

# l xenon探测器
create_detector_node(
    geometry_node,
    "Cylinder",
    "lxenon",
    "Teflon",
    {
        "soliname": "lxenonSolid",
        "logivol": "lxenonLog",
        "physvol": "lxenon",
        "radius": f"{radius_lxe}*mm",
        "height": f"{height_lxe}*mm",
        "material": "LXe",
        "shift_z": f"{shift_z_lxe}*mm",
        "surface": "0",
        "sendname": "lxenon",
        "check_overlap": "1",
    }
    if not sampling_mode
    else {
        "soliname": "lxenonSolid",
        "logivol": "lxenonLog",
        "physvol": "lxenon",
        "radius": f"{radius_lxe}*mm",
        "height": f"{height_lxe}*mm",
        "material": "LXe",
        "shift_z": f"{shift_z_lxe}*mm",
        "surface": "0",
        "check_overlap": "1",
    },
)

# TeflonGas探测器
create_detector_node(
    geometry_node,
    "Cylinder",
    "TeflonGas",
    "OuterGXe",
    {
        "soliname": "TeflonGasSolid",
        "logivol": "TeflonGasLog",
        "physvol": "TeflonGas",
        "radius": f"{radius_teflon_gas}*mm",
        "height": f"{height_teflon_gas}*mm",
        "material": "Teflon",
        "shift_z": f"{shift_z_teflon_gas}*mm",
        "surface": "1",
        "check_overlap": "1",
    },
)

# gasxenon探测器
create_detector_node(
    geometry_node,
    "Cylinder",
    "gasxenon",
    "TeflonGas",
    {
        "soliname": "gasxenonSolid",
        "logivol": "gasxenonLog",
        "physvol": "gasxenon",
        "radius": f"{radius_gxe}*mm",
        "height": f"{height_gxe}*mm",
        "material": "GXe",
        "shift_z": f"{shift_z_gxe}*mm",
        "surface": "0",
        "check_overlap": "1",
    },
)

# TopTeflon探测器
create_detector_node(
    geometry_node,
    "HolesBoard",
    "TopTeflon",
    "gasxenon",
    {
        "soliname": "TopTeflonSolid",
        "logivol": "TopTeflonLog",
        "physvol": "TopTeflon",
        "radius": f"{radius_top_teflon}*mm",
        "height": f"{height_top_teflon}*mm",
        "width_x": f"{width_x_top_teflon}*mm",
        "sides": "0",
        "material": "TeflonGas",
        "shift_z": f"{shift_z_top_teflon}*mm",
        "source": "data/topTeflon.txt",
        "surface": "1",
        "check_overlap": "1",
    },
)

# BotTeflon探测器
create_detector_node(
    geometry_node,
    "HolesBoard",
    "BotTeflon",
    "lxenon",
    {
        "soliname": "BotTeflonSolid",
        "logivol": "BotTeflonLog",
        "physvol": "BotTeflon",
        "radius": f"{radius_bot_teflon}*mm",
        "height": f"{height_bot_teflon}*mm",
        "width_x": f"{width_x_bot_teflon}*mm",
        "sides": "0",
        "material": "Teflon",
        "shift_z": f"{shift_z_bot_teflon}*mm",
        "source": "data/botTeflon.txt",
        "surface": "1",
        "check_overlap": "1",
    },
)

# Anode探测器
create_detector_node(
    geometry_node,
    "MeshGrid",
    "Anode",
    "gasxenon",
    {
        "soliname": "AnodeSolid",
        "logivol": "AnodeLog",
        "physvol": "Anode",
        "shift_z": f"{shift_z_anode}*mm",
        "radius": f"{radius_electrode}*mm",
        "wire_diameter": f"{wire_diameter}*mm",
        "wire_pitch": f"{wire_pitch_anode}*mm",
        "sides": "0",
        "material": "SS304LSteel",
        "type": "dielectric_metal",
        "surface": "1",
        "check_overlap": "1",
    },
)

# Gate探测器
create_detector_node(
    geometry_node,
    "MeshGrid",
    "Gate",
    "lxenon",
    {
        "soliname": "GateSolid",
        "logivol": "GateLog",
        "physvol": "Gate",
        "radius": f"{radius_electrode}*mm",
        "wire_diameter": f"{wire_diameter}*mm",
        "wire_pitch": f"{wire_pitch_gate}*mm",
        "sides": "0",
        "material": "SS304LSteel",
        "type": "dielectric_metal",
        "surface": "1",
        "shift_z": f"{shift_z_gate}*mm",
        "check_overlap": "1",
    },
)

# Cathode探测器
create_detector_node(
    geometry_node,
    "MeshGrid",
    "Cathode",
    "lxenon",
    {
        "soliname": "CathodeSolid",
        "logivol": "CathodeLog",
        "physvol": "Cathode",
        "radius": f"{radius_electrode}*mm",
        "wire_diameter": f"{wire_diameter}*mm",
        "wire_pitch": f"{wire_pitch_cathode}*mm",
        "sides": "0",
        "material": "SS304LSteel",
        "type": "dielectric_metal",
        "surface": "1",
        "shift_z": f"{shift_z_cathode}*mm",
        "check_overlap": "1",
    },
)

# BottomScreening探测器
create_detector_node(
    geometry_node,
    "MeshGrid",
    "BottomScreening",
    "lxenon",
    {
        "soliname": "BottomScreeningSolid",
        "logivol": "BottomScreeningLog",
        "physvol": "BottomScreening",
        "radius": f"{radius_electrode}*mm",
        "wire_diameter": f"{wire_diameter}*mm",
        "wire_pitch": f"{wire_pitch_bottom_screening}*mm",
        "sides": "0",
        "material": "SS304LSteel",
        "type": "dielectric_metal",
        "surface": "1",
        "shift_z": f"{shift_z_bottom_screening}*mm",
        "check_overlap": "1",
    },
)

# ===================== Physics节点（按范本重构）=====================
physics_node = doc.createElement("physics")
physics_node.setAttribute("name", physics_name)
root.appendChild(physics_node)

physics_param = doc.createElement("parameter")
physics_param.setAttribute("name", "cutlength")
physics_param.setAttribute("value", f"{cutlength}*mm")
physics_node.appendChild(physics_param)

# ===================== Generator节点（按范本重构）=====================
generator_node = doc.createElement("generator")
generator_node.setAttribute("name", generator_name)
root.appendChild(generator_node)

# 添加Generator参数
for name, value in generator_params:
    param_node = doc.createElement("parameter")
    param_node.setAttribute("name", name)
    param_node.setAttribute("value", value)
    generator_node.appendChild(param_node)

# ===================== Analysis节点（按范本重构）=====================
analysis_node = doc.createElement("analysis")
analysis_node.setAttribute("name", analysis_name)
root.appendChild(analysis_node)

# 分析参数配置（区分光学/非光学模式）
if optical:
    analysis_params = [
        ("EnableEnergyDeposition", "0"),
        ("EnablePrimaryParticle", "1"),
        ("SaveNullEvents", "1"),
        ("OpticalSdName", "bR8520"),
        ("UserSeed", str(seed)),
        ("GetGeoMass", str(int(get_geo_mass))),
    ]
else:
    analysis_params = [
        ("EnableEnergyDeposition", str(int(not disable_energy_depo))),
        ("EnableSurfaceFlux", str(int(enable_track))),
        ("EnablePrimaryParticle", str(int(not disable_primary_particle))),
        ("SaveNullEvents", "0"),
        ("EnableDecayChainSplitting", "1"),
        ("ChainSplittingLifeTime", "400*us"),
        ("UserSeed", str(seed)),
        ("GetGeoMass", str(int(get_geo_mass))),
    ]

for name, value in analysis_params:
    param_node = doc.createElement("parameter")
    param_node.setAttribute("name", name)
    param_node.setAttribute("value", value)
    analysis_node.appendChild(param_node)

# ===================== 保存XML文件 + 辅助文件处理 =====================
# 保存XML文件
with open(fopt, "w") as f:
    doc.writexml(f, indent="  ", addindent="  ", newl="\n", encoding="UTF-8")

# 处理辅助文件
if save_txt:
    raise AssertionError("Unimplemented feature: save_txt is True")
    # 创建数据目录
    if not os.path.exists("data"):
        os.makedirs("data")

    # 生成PMT位置文件
    pmt_arr = PMTArrangement(radius_outer_gxe, radius_outer_lxe)
    pmt_arr.generate_top_pmt("data/topPMT.txt")
    pmt_arr.generate_bottom_pmt("data/botPMT.txt")

    # 生成成形环位置文件
    tank_arr = TankArrangement(
        outer_radius_shapingrings,
        inner_radius_shapingrings,
        height_shapingrings,
        number_shapingrings,
        pitch_shapingrings,
    )
    tank_arr.generate_shaping_rings("data/shaping_rings.txt")

    # 生成管道和法兰位置文件
    tank_arr.generate_pipe("data/Pipe.txt")
    tank_arr.generate_flange("data/Flange.txt")

    # 生成特氟龙位置文件
    tank_arr.generate_teflon("data/topTeflon.txt", "data/botTeflon.txt")
