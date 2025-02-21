from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.utils.helpers import exec_shell_command_async
import modules.icons as icons
from gi.repository import GLib, Gdk

class PowerMenu(Box):
    def __init__(self, **kwargs):
        super().__init__(
            name="power-menu",
            orientation="h",
            spacing=4,
            v_align="center",
            h_align="center",
            v_expand=True,
            h_expand=True,
            visible=True,
            **kwargs,
        )

        self.notch = kwargs["notch"]

        self.btn_lock = Button(
            name="power-menu-button",
            child=Label(name="button-label", markup=icons.lock),
            on_clicked=self.lock,
        )
        self.btn_lock.connect("enter_notify_event", self.on_button_enter)
        self.btn_lock.connect("leave_notify_event", self.on_button_leave)

        self.btn_suspend = Button(
            name="power-menu-button",
            child=Label(name="button-label", markup=icons.suspend),
            on_clicked=self.suspend,
        )
        self.btn_suspend.connect("enter_notify_event", self.on_button_enter)
        self.btn_suspend.connect("leave_notify_event", self.on_button_leave)

        self.btn_logout = Button(
            name="power-menu-button",
            child=Label(name="button-label", markup=icons.logout),
            on_clicked=self.logout,
        )
        self.btn_logout.connect("enter_notify_event", self.on_button_enter)
        self.btn_logout.connect("leave_notify_event", self.on_button_leave)

        self.btn_reboot = Button(
            name="power-menu-button",
            child=Label(name="button-label", markup=icons.reboot),
            on_clicked=self.reboot,
        )
        self.btn_reboot.connect("enter_notify_event", self.on_button_enter)
        self.btn_reboot.connect("leave_notify_event", self.on_button_leave)

        self.btn_shutdown = Button(
            name="power-menu-button",
            child=Label(name="button-label", markup=icons.shutdown),
            on_clicked=self.poweroff,
        )
        self.btn_shutdown.connect("enter_notify_event", self.on_button_enter)
        self.btn_shutdown.connect("leave_notify_event", self.on_button_leave)

        self.buttons = [
            self.btn_lock,
            self.btn_suspend,
            self.btn_logout,
            self.btn_reboot,
            self.btn_shutdown,
        ]

        for button in self.buttons:
            self.add(button)

        self.show_all()

    def close_menu(self):
        self.notch.close_notch()

    def on_button_enter(self, widget, event):
        window = widget.get_window()
        if window:
            window.set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))

    def on_button_leave(self, widget, event):
        window = widget.get_window()
        if window:
            window.set_cursor(None)

    # Métodos de acción
    def lock(self, *args):
        print("Locking screen...")
        exec_shell_command_async("xflock4")
        self.close_menu()

    def suspend(self, *args):
        print("Suspending system...")
        exec_shell_command_async("systemctl suspend")
        self.close_menu()

    def logout(self, *args):
        print("Logging out...")
        exec_shell_command_async("xfce4-session-logout --logout --fast")
        self.close_menu()

    def reboot(self, *args):
        print("Rebooting system...")
        exec_shell_command_async("systemctl reboot")
        self.close_menu()

    def poweroff(self, *args):
        print("Powering off...")
        exec_shell_command_async("systemctl poweroff")
        self.close_menu()