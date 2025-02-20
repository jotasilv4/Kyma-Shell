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
import multiprocessing, threading

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

        self.workspaces_box = Box(
            name="workspaces-box",
            spacing=10,
            orientation="h",
            children=[Button(name="workspaces-button", on_clicked=lambda b, num=i: self.switch_workspace(num)) for i in range(1, 11)]
        )

        # Workspaces Events
        focused = self.i3.get_tree().find_focused()
        wsnumber = focused.workspace().num - 1
        self.workspaces_box.children[wsnumber].add_style_class("focused")

        self.i3.on(Event.WORKSPACE, self.on_workspaces)

        threading.Thread(target=self.i3.main, daemon=True).start()   
        
        self.children = self.workspaces_box
        
    def on_workspaces(self, works, e):
        try:
            tree = self.i3.get_tree()
            focused_workspace = tree.find_focused().workspace()

            for i, btn in enumerate(self.workspaces_box.children):
                ws_num = i + 1

                idle_add(btn.remove_style_class, "focused")
                idle_add(btn.remove_style_class, "active")

                ws = next((w for w in tree.workspaces() if w.num == ws_num), None)
                if ws is not None:
                    if ws_num == focused_workspace.num:
                        idle_add(btn.add_style_class, "focused")
                    elif len(ws.leaves()) > 0:
                        idle_add(btn.add_style_class, "active")
        except Exception as ex:
            print("Erro ao atualizar workspaces:", ex)


    def switch_workspace(self, num):
        self.i3.command(f"workspace {num}")

        ## CODIGO ANTIGO DO ON_WORKSPACES
        # try:
        #     focused = self.i3.get_tree().find_focused()
        #     wsnumber = focused.workspace().num - 1

        #     # Remove o estilo "active" de todos os botões, se desejar:
        #     for btn in self.workspaces_box.children:
        #         idle_add(btn.remove_style_class, "focused")

        #     # Atualiza o botão correspondente usando idle_add na thread principal
        #     workspace = self.workspaces_box.children[wsnumber]
        #     idle_add(workspace.add_style_class, "focused")

        # except Exception as ex:
        #     print("Error:", ex)
    