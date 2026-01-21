import argparse
import copy
import json
import shutil

import numpy as np
import pandas as pd
from muonRate import muon_rate

parser = argparse.ArgumentParser(
    description="Generate normalization factor after simulation"
)
parser.add_argument(
    "--InputFile",
    dest="InputFile",
    required=True,
    help="Input .json file with simulated events",
)
parser.add_argument(
    "--paramsFile", dest="paramsFile", required=True, help="Parameters .json file"
)
parser.add_argument(
    "--GeoFile", dest="GeoFile", required=True, help="Geometry setup .json file"
)
parser.add_argument(
    "--OutputFile", dest="OutputFile", required=True, help="Output .json file"
)
args = parser.parse_args()

# 文件路径处理
InputFilename = args.InputFile
paramsFilename = args.paramsFile
GeoFilename = args.GeoFile
OutputFilename = args.OutputFile
shutil.copy(
    GeoFilename, "../analysis/geo_params.json"
)  # 修正：复制几何文件而非参数文件

# 常量定义
date_s = 24 * 3600  # 秒/天
pmtN = 38  # PMT数量
Kr85 = 10  # 天然氪浓度 (ppt)
Rn222 = 40  # 氡浓度 (uBq/kg)

# 加载配置文件
with open(paramsFilename) as f:
    params = json.load(f)
with open(GeoFilename) as f:
    geo = json.load(f)  # 几何参数从GeoFile加载
with open(InputFilename) as f:
    norm = json.load(f)

normalization = dict()

# 缪子和CRN率计算
shielding_x = params["muon_x"] / 100  # 转换为米
m_rate = muon_rate() * shielding_x**2 * 2 * np.pi
print(f"Total muon rate: {m_rate:.2f}Hz")
print(f"Muon rate per m²: {m_rate / (shielding_x**2):.2f}Hz/m²")

shielding_x = params["CRN_x"] / 100  # 转换为米
CRN_rate = 248.59 / 25 * shielding_x * shielding_x
print(f"Total CRN rate: {CRN_rate:.2f}Hz")
print(f"CRN rate per m²: {CRN_rate / (shielding_x**2):.2f}Hz/m²")

# 从几何配置中提取探测器组件
detectors = copy.deepcopy(geo.get("geometry", {}).get("detectors", []))  # 增加容错处理
for i, det in enumerate(detectors):
    print(f"{i:2d} {det['name']}")

# 从mass.log加载质量数据
masses = []
reading = False
with open("mass.log", "r") as f:
    for line in f.readlines():
        if "Printed Mass of Geometry" in line:
            reading = False
        if reading:
            parts = [p for p in line.strip().split() if p]
            if len(parts) >= 6:  # 确保数据完整性
                masses.append(parts)
        if "Printing Mass of Geometry" in line:
            reading = True

# 处理质量数据（转换单位为kg和g/cm³）
mass_data = []
for m in masses:
    geom, mat = m[0], m[1]
    mass_val, mass_unit = float(m[2]), m[3]
    dens_val, dens_unit = float(m[4]), m[5]

    # 质量单位转换为kg
    if mass_unit == "mg":
        mass_kg = mass_val * 1e-6
    elif mass_unit == "g":
        mass_kg = mass_val * 1e-3
    else:  # kg
        mass_kg = mass_val

    # 密度单位转换为g/cm³
    if dens_unit == "mg/cm³":
        dens_gcm3 = dens_val * 1e-3
    elif dens_unit == "kg/cm³":
        dens_gcm3 = dens_val * 1e3
    else:  # g/cm³
        dens_gcm3 = dens_val

    mass_data.append(
        {
            "geometry": geom,
            "material": mat,
            "mass_kg": mass_kg,
            "density_gcm3": dens_gcm3,
        }
    )

# 按材料分组计算总质量
material_mass = pd.DataFrame(mass_data).groupby("material")["mass_kg"].sum().to_dict()
geom_mass = {m["geometry"]: (m["mass_kg"], m["density_gcm3"]) for m in mass_data}

# 1. 铜组件（Shapingrings，几何配置中明确为Copper）
if "Shapingrings" in geom_mass:
    copper_mass, copper_dens = geom_mass["Shapingrings"]
else:
    # 从几何文件获取成形环尺寸计算质量（备用方案）
    outer_r = geo["outer_radius_shapingrings"] / 10  # cm（修正：从geo获取参数）
    inner_r = geo["inner_radius_shapingrings"] / 10
    height = geo["height_shapingrings"] / 10
    num_rings = geo["number_shapingrings"]  # 修正：增加环数量
    volume_cm3 = (
        np.pi * (outer_r**2 - inner_r**2) * height * num_rings
    )  # 修正：乘以环数量
    copper_dens = 8.92  # 修正：使用Material.cc中定义的铜密度
    copper_mass = volume_cm3 * copper_dens * 1e-3  # 转换为kg

normalization["copper"] = {
    "density": copper_dens,
    "mass": copper_mass,
    "volume": copper_mass * 1e3 / copper_dens,  # cm³
}

# 2. 钢组件（包含所有SS304LSteel和Flange材质的部件，Material.cc中Flange与SS304LSteel成分相同）
steel_components = [
    "OuterContainer",
    "InnerContainer",
    "Flange",
    "Anode",
    "Cathode",
    "Gate",
    "BottomScreening",
    "Casing",
]  # 修正：统一Flange命名
steel_mass = sum(geom_mass[comp][0] for comp in steel_components if comp in geom_mass)
steel_dens = (
    geom_mass["OuterContainer"][1] if "OuterContainer" in geom_mass else 8.00
)  # 修正：使用Material.cc中SS304LSteel密度

normalization["steel"] = {
    "density": steel_dens,
    "total_mass": steel_mass,
    "volume": steel_mass * 1e3 / steel_dens,
}

# 3. Teflon组件（包含所有Teflon材质部件，Material.cc中定义Teflon和TeflonGas）
teflon_components = ["Teflon", "TopTeflon", "BotTeflon", "TeflonGas"]
teflon_mass = sum(geom_mass[comp][0] for comp in teflon_components if comp in geom_mass)
teflon_dens = (
    geom_mass["Teflon"][1] if "Teflon" in geom_mass else 2.2
)  # 与Material.cc一致

normalization["Teflon"] = {
    "density": teflon_dens,
    "mass": teflon_mass,
    "volume": teflon_mass * 1e3 / teflon_dens,
}

# 4. PMT相关组件（参考Material.cc中的PhotoCathodeAluminium和Quartz）
normalization["PMTwindow"] = {
    "density": geom_mass["Window"][1] if "Window" in geom_mass else 2.2,  # Quartz密度
    "mass": geom_mass["Window"][0] if "Window" in geom_mass else 0.1,
    "volume": (geom_mass["Window"][0] * 1e3 / geom_mass["Window"][1])
    if "Window" in geom_mass
    else 45.45,
    "num": pmtN,
}

normalization["PMTbase"] = {
    "density": geom_mass["Base"][1] if "Base" in geom_mass else 8.00,  # 钢材质
    "mass": geom_mass["Base"][0] if "Base" in geom_mass else 0.2,
    "volume": (geom_mass["Base"][0] * 1e3 / geom_mass["Base"][1])
    if "Base" in geom_mass
    else 25.06,
    "num": pmtN,
}

# 5. 液态氙组件（Material.cc中定义LXe）
lxe_components = ["XenonDetector", "XenonVeto"]
lxe_mass = sum(geom_mass[comp][0] for comp in lxe_components if comp in geom_mass)
lxe_dens = (
    geom_mass["XenonDetector"][1] if "XenonDetector" in geom_mass else 2.862
)  # 修正：使用Material.cc中LXe密度

normalization["lXe"] = {
    "density": lxe_dens,
    "mass": lxe_mass,
    "volume": lxe_mass * 1e3 / lxe_dens,
}

# 打印组件质量验证
for component in ["copper", "steel", "Teflon", "PMTwindow", "PMTbase", "lXe"]:
    print(f"{component} mass: {normalization[component]['mass']:.4f} kg")

# 归一化因子计算（保持原逻辑）
eventALL = norm["N"]

# 缪子和CRN归一化
normalization["muon"] = {"factor": norm["_muon"] * eventALL, "activity": m_rate}

normalization["CRN"] = {"factor": norm["_CRN"] * eventALL, "activity": CRN_rate}

# 同位素归一化（匹配几何组件，Flange已包含在steel中）
isotopes = ["U238", "Th232", "Co60", "K40"]
components = ["copper", "steel", "Teflon", "PMTwindow", "PMTbase"]  # 移除重复的Flange
for isotope in isotopes:
    for component in components:
        key = f"{isotope}_{component}"
        normalization[key] = {"factor": norm[f"_{key}"] * eventALL}

# 特殊同位素（PMT窗口铯137）
normalization["Cs137_PMTwindow"] = {"factor": norm["_Cs137_PMTwindow"] * eventALL}

# 液态氙同位素
lxe_isotopes = ["Kr85", "Rn222"]
for isotope in lxe_isotopes:
    key = f"{isotope}_lXe"
    normalization[key] = {"factor": norm[f"_{key}"] * eventALL}

# 保存结果
with open(OutputFilename, "w") as f:
    json.dump(normalization, f, indent=2)
