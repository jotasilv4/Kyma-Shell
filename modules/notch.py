from os import truncate
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.button import Button
from fabric.widgets.stack import Stack
from fabric.widgets.x11 import X11Window as Window
from fabric.hyprland.widgets import ActiveWindow
from fabric.utils.helpers import FormattedString, truncate
from modules.corners import MyCorner
from gi.repository import GLib, Gdk
import modules.icons as icons

class Notch(Window):
    def __init__(self, **kwargs):
        super().__init__(
            name="notch",
            layer="top",
            geometry="top",
            type_hint="normal",
            margin="-4px -4px -4px -4px",
            keyboard_mode="none",
            visible=True,
            all_visible=True,
        )

        self.compact = Button(
            name="notch-compact",
            h_expand=True,
            child=Label(label="teste")
        )

        self.stack = Stack(
            name="notch-content",
            v_expand=True,
            h_expand=True,
            transition_type="crossfade",
            transition_duration=100,
            children=[
                self.compact
            ]
        )

        self.corner_left = Box(
            name="notch-corner-left",
            orientation="v",
            children=[
                MyCorner("top-right"),
                Box(),
            ]
        )

        self.corner_right = Box(
            name="notch-corner-right",
            orientation="v",
            children=[
                MyCorner("top-left"),
                Box(),
            ]
        )

        self.notch_box = CenterBox(
            name="notch-box",
            orientation="h",
            h_align="center",
            v_align="center",
            start_children=Box(
                children=[
                    self.corner_left,
                ],
            ),
            center_children=self.stack,
            end_children=Box(
                children=[
                    self.corner_right,
                ]
            )
        )

        self.add(self.notch_box)
        self.hidden = False
        
        self.show_all()