import os
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
from modules.power import PowerMenu
from modules.rofi import Rofi

class Notch(Window):
    def __init__(self, **kwargs):
        super().__init__(
            name="notch",
            layer="top",
            geometry="top",
            type_hint="normal",
            margin="-8px -4px -8px -4px",
            keyboard_mode="none",
            visible=True,
            all_visible=True,
        )
        
        self.power = PowerMenu(notch=self)
        self.rofi = Rofi(notch=self)

        self.compact = Button(
            name="notch-compact",
            h_expand=True,
            child=Label(label=f"{os.getlogin()}@{os.uname().nodename}")
        )

        self.stack = Stack(
            name="notch-content",
            v_expand=True,
            h_expand=True,
            transition_type="crossfade",
            transition_duration=100,
            children=[
                self.compact,
                self.power,
                self.rofi
            ]
        )
        self.compact.connect("enter-notify-event", self.on_button_enter)
        self.compact.connect("leave-notify-event", self.on_button_leave)

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
        
        self.add_keybinding("Escape", lambda *_: self.close_notch())
        
    def on_button_enter(self, widget, event):
        window = widget.get_window()
        if window:
            window.set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))

    def on_button_leave(self, widget, event):
        window = widget.get_window()
        if window:
            window.set_cursor(None)
           
    def open_notch(self, widget):
        #self.set_keyboard_mode("exclusive")
        
        if self.hidden:
            self.notch_box.remove_style_class("hidden")
            self.notch_box.add_style_class("hideshow")
            
        widgets = {
            "power": self.power,
            "rofi": self.rofi
        }
        
        for style in widgets.keys():
            self.stack.remove_style_class(style)
        for w in widgets.values():
            w.remove_style_class("open")
            
        if widget in widgets:
            self.stack.add_style_class(widget)
            self.stack.set_visible_child(widgets[widget])
            widgets[widget].add_style_class("open")
            
            if widget == "rofi":
                self.rofi.open_launcher()
                self.rofi.search_entry.set_text("")
                self.rofi.search_entry.grab_focus()
        else:
            self.stack.set_visible_child(self.compact)
        
    def close_notch(self):
        #self.set_keyboard_mode("none")
        self.rofi.launcher_box.remove(self.rofi.scrolled_window)

        if self.hidden:
            self.notch_box.remove_style_class("hideshow")
            self.notch_box.add_style_class("hidden")

        for widget in [self.power, self.rofi]:
             widget.remove_style_class("open")
        for style in ["power", "rofi"]:
            self.stack.remove_style_class(style)
            
        self.stack.set_visible_child(self.compact)
        
    def toggle_hidden(self):
        self.hidden = not self.hidden
        if self.hidden:
            self.notch_box.add_style_class("hidden")
        else:
            self.notch_box.remove_style_class("hidden")

    
