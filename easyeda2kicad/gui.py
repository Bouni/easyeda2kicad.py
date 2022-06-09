# Global imports
import os
import pathlib
from ast import arg

import wx
from numpy import outer

from easyeda2kicad.helpers import (
    generate_3dmodel,
    generate_footprint,
    generate_symbol,
    get_cad_data,
    valid_arguments,
)


class Gui(wx.Frame):
    def __init__(self):
        super().__init__(
            parent=None,
            title="easyeda2kicad",
            size=wx.Size(500, 300),
        )
        panel = wx.Panel(self)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # ---------------- LCSC ID ----------------
        h1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lcsc_id_label = wx.StaticText(
            panel, wx.ID_ANY, "LCSC ID", wx.DefaultPosition, wx.Size(200, -1), 0
        )
        h1_sizer.Add(self.lcsc_id_label, 1, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        self.lcsc_id_textctrl = wx.TextCtrl(
            panel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(300, -1), 0
        )
        h1_sizer.Add(self.lcsc_id_textctrl, 0, wx.LEFT | wx.RIGHT, 5)

        # ---------------- Symbol ----------------
        h2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.symbol_label = wx.StaticText(
            panel, wx.ID_ANY, "Generate symbol", wx.DefaultPosition, wx.Size(200, -1), 0
        )
        h2_sizer.Add(self.symbol_label, 1, wx.LEFT | wx.RIGHT, 5)
        self.symbol_checkbox = wx.CheckBox(
            panel,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(300, -1),
            0,
        )
        self.symbol_checkbox.SetValue(True)
        h2_sizer.Add(self.symbol_checkbox, 0, wx.LEFT | wx.RIGHT, 5)

        # ---------------- Footprint ----------------
        h3_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.footprint_label = wx.StaticText(
            panel,
            wx.ID_ANY,
            "Generate footprint",
            wx.DefaultPosition,
            wx.Size(200, -1),
            0,
        )
        h3_sizer.Add(self.footprint_label, 1, wx.LEFT | wx.RIGHT, 5)
        self.footprint_checkbox = wx.CheckBox(
            panel,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(300, -1),
            0,
        )
        self.footprint_checkbox.SetValue(True)
        h3_sizer.Add(self.footprint_checkbox, 0, wx.LEFT | wx.RIGHT, 5)

        # ---------------- 3D model ----------------
        h4_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.model_label = wx.StaticText(
            panel,
            wx.ID_ANY,
            "Generate 3D model",
            wx.DefaultPosition,
            wx.Size(200, -1),
            0,
        )
        h4_sizer.Add(self.model_label, 1, wx.LEFT | wx.RIGHT, 5)
        self.model_checkbox = wx.CheckBox(
            panel,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(300, -1),
            0,
        )
        self.model_checkbox.SetValue(True)
        h4_sizer.Add(self.model_checkbox, 0, wx.LEFT | wx.RIGHT, 5)

        # ---------------- Overwrite ----------------
        h5_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.overwrite_label = wx.StaticText(
            panel,
            wx.ID_ANY,
            "Overwrite existing data",
            wx.DefaultPosition,
            wx.Size(200, -1),
            0,
        )
        h5_sizer.Add(self.overwrite_label, 1, wx.LEFT | wx.RIGHT, 5)
        self.overwrite_checkbox = wx.CheckBox(
            panel,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(300, -1),
            0,
        )
        h5_sizer.Add(self.overwrite_checkbox, 0, wx.LEFT | wx.RIGHT, 5)

        # ---------------- Library path ----------------

        username = os.getlogin()
        self.library_path = pathlib.Path(
            f"C:/Users/{username}/Documents/KiCad/easyeda2kicad/easyeda2kicad"
        )

        h6_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.output_label = wx.StaticText(
            panel,
            wx.ID_ANY,
            str(self.library_path),
            wx.DefaultPosition,
            wx.Size(-1, -1),
            0,
        )
        h6_sizer.Add(self.output_label, 1, wx.LEFT | wx.RIGHT | wx.TOP, 5)

        h7_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.select_output_button = wx.Button(panel, label="Select library path")
        self.select_output_button.Bind(wx.EVT_BUTTON, self.select_output_path)
        h7_sizer.Add(self.select_output_button, 0, wx.LEFT | wx.RIGHT, 5)

        main_sizer.Add(h1_sizer, 0, wx.ALL | wx.CENTER, 5)
        main_sizer.Add(h2_sizer, 0, wx.ALL | wx.CENTER, 5)
        main_sizer.Add(h3_sizer, 0, wx.ALL | wx.CENTER, 5)
        main_sizer.Add(h4_sizer, 0, wx.ALL | wx.CENTER, 5)
        main_sizer.Add(h5_sizer, 0, wx.ALL | wx.CENTER, 5)
        main_sizer.Add(h6_sizer, 0, wx.ALL | wx.CENTER, 5)
        main_sizer.Add(h7_sizer, 0, wx.ALL | wx.CENTER, 5)

        download_button = wx.Button(panel, label="Download")

        download_button.Bind(wx.EVT_BUTTON, self.download)

        main_sizer.Add(download_button, 0, wx.ALL | wx.CENTER, 5)
        panel.SetSizer(main_sizer)
        self.Show()

    def select_output_path(self, e):
        dlg = wx.FileDialog(
            self,
            message="Choose a folder",
            defaultDir=str(self.library_path.parent),
            defaultFile=str(self.library_path.name),
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.library_path = pathlib.Path(dlg.GetPath())
            self.output_label.SetLabel(str(self.library_path))
        dlg.Destroy()

    def download(self, e):
        arguments = {
            "lcsc_id": self.lcsc_id_textctrl.GetValue(),
            "symbol": self.symbol_checkbox.GetValue(),
            "footprint": self.footprint_checkbox.GetValue(),
            "3d": self.model_checkbox.GetValue(),
            "overwrite": self.overwrite_checkbox.GetValue(),
            "output": str(self.library_path),
            "full": None,
        }

        if not valid_arguments(arguments=arguments):
            return

        cad_data = get_cad_data(component_id=arguments["lcsc_id"])

        # Symbol
        if arguments["symbol"]:
            generate_symbol(
                cad_data=cad_data,
                component_id=arguments["lcsc_id"],
                output=arguments["output"],
                overwrite=arguments["overwrite"],
            )

        # Footprint
        if arguments["footprint"]:
            generate_footprint(
                cad_data=cad_data,
                component_id=arguments["lcsc_id"],
                output=arguments["output"],
                overwrite=arguments["overwrite"],
            )

        # 3D model
        if arguments["3d"]:
            generate_3dmodel(
                cad_data=cad_data,
                component_id=arguments["lcsc_id"],
                output=arguments["output"],
            )
