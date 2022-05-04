# Global imports
import argparse
import os
import re
import sys
from typing import List

import wx
from gui import Gui
from helpers import (
    generate_3dmodel,
    generate_footprint,
    generate_symbol,
    get_cad_data,
    valid_arguments,
)


def get_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description="A Python script that convert any electronic components from LCSC or EasyEDA to a Kicad library"
    )

    parser.add_argument("--lcsc_id", help="LCSC id", required=True, type=str)

    parser.add_argument(
        "--symbol", help="Get symbol of this id", required=False, action="store_true"
    )

    parser.add_argument(
        "--footprint",
        help="Get footprint of this id",
        required=False,
        action="store_true",
    )

    parser.add_argument(
        "--3d",
        help="Get the 3d model of this id",
        required=False,
        action="store_true",
    )

    parser.add_argument(
        "--full",
        help="Get the symbol, footprint and 3d model of this id",
        required=False,
        action="store_true",
    )

    parser.add_argument(
        "--output",
        required=False,
        metavar="file.lib",
        help="Output file",
        type=str,
        # default=
    )

    parser.add_argument(
        "--overwrite",
        required=False,
        help="overwrite symbol and footprint lib if there is already a component with this lcsc_id",
        action="store_true",
    )

    return parser


def main(argv: List[str] = sys.argv[1:]) -> int:

    if len(argv) == 0:
        # start GUI
        app = wx.App()
        frame = Gui()
        app.MainLoop()
    else:
        # cli interface
        parser = get_parser()
        try:
            args = parser.parse_args(argv)
        except SystemExit as err:
            return err.code
        arguments = vars(args)

        if not valid_arguments(arguments=arguments):
            return 1

        component_id = arguments["lcsc_id"]
        overwrite = arguments['overwrite']
        output = arguments['output']
        
        print("-- easyeda2kicad.py --")

        cad_data = get_cad_data(component_id=component_id)

        # ---------------- SYMBOL ----------------
        if arguments["symbol"]:
            generate_symbol(cad_data=cad_data, component_id=component_id, overwrite=overwrite, output=output)

        # ---------------- FOOTPRINT ----------------
        if arguments["footprint"]:
            generate_footprint(cad_data=cad_data, component_id=component_id, overwrite=overwrite, output=output)

        # ---------------- 3D MODEL ----------------
        if arguments["3d"]:
            generate_3dmodel(cad_data=cad_data, component_id=component_id, output=output)

        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
