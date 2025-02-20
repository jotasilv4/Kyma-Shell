import setproctitle
import os
from fabric import Application
from fabric.utils import get_relative_path
from modules.bar import Bar
from modules.notch import Notch
from modules.corners import Corners

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk

screen = Gdk.Screen.get_default()
CURRENT_WIDTH = screen.get_width()
CURRENT_HEIGHT = screen.get_height()

if __name__ == "__main__":
    setproctitle.setproctitle("kyshell")
    bar = Bar()
    notch = Notch()
    bar.notch = notch
    app = Application("kymashell", bar, notch)
    
    def set_css():
        app.set_stylesheet_from_file(
            get_relative_path("style.css"),
            exposed_functions={
                "overview_width": lambda: f"min-width: {CURRENT_WIDTH * 0.1 * 5}px;",
                "overview_height": lambda: f"min-height: {CURRENT_HEIGHT * 0.1 * 2}px;",
            },
        )
        
    app.set_css = set_css
    
    app.set_css()
    app.run()