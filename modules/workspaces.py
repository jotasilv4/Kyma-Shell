from inspect import _empty
import operator
from collections.abc import Iterator
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.entry import Entry
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.utils import DesktopApp, get_desktop_applications, idle_add, remove_handler
from i3ipc import Connection, Event
import multiprocessing

class Workspaces(Box):
    def __init__(self, **kwargs):
        super().__init__(
            name="workspaces",
            visible=True,
            all_visible=True,
            orientation="h",
            h_align="fill",
            v_align="center",
        )
        
        self.i3 = Connection()
        self.i3.on(Event.WORKSPACE, self.on_workspaces)
        
        self.workspaces_box = Box(
            name="workspaces-box",
            spacing=10,
            orientation="h",
            children=[Button(name="workspaces-button") for i in range(1, 11)]
        )   
        
        
        
        self.children = self.workspaces_box
        
        multiprocessing.Process(target=self.i3.main, args=()).start()
        
    def on_workspaces(self, ws, e):
        focused = self.i3.get_tree().find_focused()
        wsnumber = focused.workspace().num - 1
        
        ws = self.workspaces_box.children[wsnumber]
        
        ws.add_style_class("active")
        
        print(ws)
    