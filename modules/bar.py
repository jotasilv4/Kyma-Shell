from fabric.widgets.box import Box
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.button import Button
from fabric.widgets.x11 import X11Window as Window

from gi.repository import GLib, Gdk
from modules.systemtray import SystemTray
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
            visible=True,
            all_visilbe=True
        )

        self.notch = kwargs.get("notch", None)
        
        self.systray = SystemTray()

        self.date_time = DateTime(name="date-time", formatters=["%H:%M"], h_align="center", v_align="center")
        
        self.button_apps = Button(
            name="button-bar",
            child=Label(
                name="button-bar-label",
                markup=icons.apps
            )
        )
        self.button_apps.connect("enter_notify_event", self.on_button_enter)
        self.button_apps.connect("leave_notify_event", self.on_button_leave)

        self.button_power = Button(
            name="button-bar",
            child=Label(
                name="button-bar-label",
                markup=icons.shutdown
            )
        )
        self.button_power.connect("enter_notify_event", self.on_button_enter)
        self.button_power.connect("leave_notify_event", self.on_button_leave)
        
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
            ),
            end_children=Box(
                name="end-container",
                spacing=4,
                orientation="h",
                children=[
                    self.systray,
                    self.date_time,
                    self.button_power,
                ],
            ),
        )
        
        self.children = self.bar_inner
        
        self.hidden = False
        
        self.show_all()

    def on_button_enter(self, widget, event):
        window = widget.get_window()
        if window:
            window.set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))

    def on_button_leave(self, widget, event):
        window = widget.get_window()
        if window:
            window.set_cursor(None)