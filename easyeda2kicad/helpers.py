# Global imports
import os
import re

from easyeda2kicad.easyeda.easyeda_api import easyeda_api
from easyeda2kicad.easyeda.easyeda_importer import (
    easyeda_3d_model_importer,
    easyeda_footprint_importer,
    easyeda_symbol_importer,
)
from easyeda2kicad.easyeda.parameters_easyeda import ee_symbol
from easyeda2kicad.kicad.export_kicad_3d_model import exporter_3d_model_kicad
from easyeda2kicad.kicad.export_kicad_footprint import exporter_footprint_kicad
from easyeda2kicad.kicad.export_kicad_symbol import exporter_symbol_kicad


def get_cad_data(component_id: str):
    # Get CAD data of the component using easyeda API
    api = easyeda_api()
    return api.get_cad_data_of_component(lcsc_id=component_id)


def generate_symbol(cad_data: str, component_id: str, output: str, overwrite: bool):
    importer = easyeda_symbol_importer(easyeda_cp_cad_data=cad_data)
    easyeda_symbol: ee_symbol = importer.get_symbol()

    is_id_already_in_symbol_lib = id_already_in_symbol_lib(
        lib_path=f"{output}.lib",
        component_id=easyeda_symbol.info.lcsc_id,
        component_name=easyeda_symbol.info.name,
    )
    if not overwrite and is_id_already_in_symbol_lib:
        print("[-] Error: Use --overwrite to update the older symbol lib")
        return 1

    print(f"[*] Creating Kicad symbol library for LCSC id : {component_id}")

    exporter = exporter_symbol_kicad(symbol=easyeda_symbol, kicad_version=5)
    # print(exporter.output)
    kicad_symbol_lib = exporter.get_kicad_lib()

    if is_id_already_in_symbol_lib:
        delete_component_in_symbol_lib(
            lib_path=f"{output}.lib",
            component_id=easyeda_symbol.info.lcsc_id,
            component_name=easyeda_symbol.info.name,
        )

    with open(file=f"{output}.lib", mode="a+", encoding="utf-8") as my_lib:
        my_lib.write(kicad_symbol_lib)


def generate_footprint(cad_data: str, component_id: str, output: str, overwrite: bool):
    importer = easyeda_footprint_importer(easyeda_cp_cad_data=cad_data)
    easyeda_footprint = importer.get_footprint()

    is_id_already_in_footprint_lib = fp_already_in_footprint_lib(
        lib_path=f"{output}.pretty",
        package_name=easyeda_footprint.info.name,
    )
    if not overwrite and is_id_already_in_footprint_lib:
        print("[-] Error: Use --overwrite to replace the older footprint lib")
        return 1

    print(f"[*] Creating Kicad footprint library for LCSC id : {component_id}")
    exporter = exporter_footprint_kicad(footprint=easyeda_footprint).export(
        output_path=output
    )


def generate_3dmodel(cad_data: str, component_id: str, output: str):
    print(f"[*] Creating 3D model for LCSC id : {component_id}")
    exporter = exporter_3d_model_kicad(
        model_3d=easyeda_3d_model_importer(easyeda_cp_cad_data=cad_data).output
    ).export(lib_path=output)


def valid_arguments(arguments: dict) -> bool:

    if not arguments["lcsc_id"].startswith("C"):
        print("[-] Error: lcsc_id should start by C....")
        return False

    if arguments["full"]:
        arguments["symbol"], arguments["footprint"], arguments["3d"] = True, True, True

    if not any([arguments["symbol"], arguments["footprint"], arguments["3d"]]):
        print("[-] Error: Missing action arguments. For example :")
        print("  easyeda2kicad --lcsc_id=C2040 --footprint")
        print("  easyeda2kicad --lcsc_id=C2040 --symbol")
        return False

    if arguments["output"]:
        base_folder = "/".join(arguments["output"].replace("\\", "/").split("/")[:-1])
        lib_name = (
            arguments["output"].replace("\\", "/").split("/")[-1].split(".lib")[0]
        )
        # Check input
        if not os.path.isdir(base_folder):
            print("Can't find the folder")
            return False
    else:
        default_folder = os.path.join(
            os.path.expanduser("~"), "Documents", "Kicad", "easyeda2kicad"
        )
        if not os.path.isdir(default_folder):
            os.mkdir(default_folder)

        base_folder = default_folder
        lib_name = "easyeda2kicad"

    arguments["output"] = f"{base_folder}/{lib_name}"
    # Create new lib files if they dont exist
    if not os.path.isdir(f"{arguments['output']}.pretty"):
        os.mkdir(f"{arguments['output']}.pretty")
        print(f"[+] Create {lib_name}.pretty footprint folder in {base_folder}")

    # Create new 3d model folder if don't exist
    if not os.path.isdir(f"{arguments['output']}.3dshapes"):
        os.mkdir(f"{arguments['output']}.3dshapes")
        print(f"[+] Create {lib_name}.3dshapes 3D model folder in {base_folder}")

    if not os.path.isfile(f"{arguments['output']}.lib"):
        with open(
            file=f"{arguments['output']}.lib", mode="w+", encoding="utf-8"
        ) as my_lib:
            my_lib.write("EESchema-LIBRARY Version 2.4\n#encoding utf-8\n")
        print(f"[+] Create {lib_name}.lib symbol lib in {base_folder}")

    return True


def id_already_in_symbol_lib(
    lib_path: str, component_id: str, component_name: str
) -> bool:
    with open(lib_path, encoding="utf-8") as f:
        current_lib = f.read()
        component = re.findall(
            rf'(#\n# {component_name}\n#\n.*?F6 "{component_id}".*?ENDDEF)',
            current_lib,
            flags=re.DOTALL,
        )

        if component != []:
            print(f"[*] This id is already in {lib_path}")
            return True
    return False


def delete_component_in_symbol_lib(
    lib_path: str, component_id: str, component_name: str
):
    with open(file=lib_path, encoding="utf-8") as f:
        current_lib = f.read()
        new_data = re.sub(
            rf'(#\n# {component_name}\n#\n.*?F6 "{component_id}".*?ENDDEF\n)',
            "",
            current_lib,
            flags=re.DOTALL,
        )

    with open(file=lib_path, mode="w", encoding="utf-8") as my_lib:
        my_lib.write(new_data)


def fp_already_in_footprint_lib(lib_path: str, package_name: str) -> bool:
    if os.path.isfile(f"{lib_path}/{package_name}.kicad_mod"):
        print(f"[*] The footprint for this id is already in {lib_path}")
        return True
    return False
