from fabric.widgets.box import Box
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.button import Button
from fabric.widgets.x11 import X11Window as Window

from gi.repository import GLib, Gdk
#from modules.systemtray import SystemTray
import modules.icons as icons
from modules.workspaces import Workspaces

class Bar(Window):
    def __init__(self, **kwargs):
        super().__init__(
            name="bar",
            layer="top",
            geometry="top",
            type_hint="dock",
            margin="-8px -4px -8px -4px",
            exclusivity="auto",
            visible=True,
            all_visilbe=True
        )
        
        #self.systray = SystemTray()
        
        self.button_apps = Button(
            name="button-bar",
            child=Label(
                name="button-bar-label",
                markup=icons.apps
            )
        )
        
        self.workspaces = Workspaces()
        
        self.bar_inner = CenterBox(
            name="bar-inner",
            orientation="h",
            h_align="fill",
            v_align="center",
            start_children=Box(
                name="start-container",
                spacing=4,
                orientation="h",
                children=[
                    self.button_apps,
                    self.workspaces
                ]
            )
        )
        
        self.children = self.bar_inner
        
        self.hidden = False
        
        self.show_all()