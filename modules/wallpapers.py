import os
import hashlib
import shutil
from gi.repository import GdkPixbuf, Gtk, GLib, Gio, Gdk
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.entry import Entry
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.utils.helpers import exec_shell_command_async
from PIL import Image
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from functools import partial
import configparser

class WallpaperSelector(Box):
    HOME = os.path.expanduser("~")
    CACHE_DIR = os.path.join(HOME, ".cache/kyma-shell/thumbs")
    WALLPAPERS_DIR = os.path.join(HOME, ".config/Kyma-Shell/assets/wallpapers/")
    NITROGEN_CFG = os.path.join(HOME, ".config/nitrogen/bg-saved.cfg")

    def __init__(self, **kwargs):
        old_cache_dir = os.path.join(self.HOME, ".cache/kyma-shell/wallpapers")
        if os.path.exists(old_cache_dir):
            shutil.rmtree(old_cache_dir)
        
        super().__init__(
            name="wallpapers",
            orientation="v",
            h_expand=True,
            v_expand=True,
            margin=10,
            spacing=10,
            **kwargs
        )
        os.makedirs(self.CACHE_DIR, exist_ok=True)
        
        self.screens = self._load_nitro_screens()
        self.files = sorted([f for f in os.listdir(self.WALLPAPERS_DIR) if self._is_image(f)])
        self.thumbnails = []
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.thumb_lock = Lock()
        self.selected_index = -1

        # Configuração do grid
        self.viewport = Gtk.IconView(
            name="wallpaper-icons",
            item_width=140,
            columns=5,
            row_spacing=20,
            column_spacing=20,
            margin=10,
        )
        self.viewport.set_model(Gtk.ListStore(GdkPixbuf.Pixbuf, str))
        self.viewport.set_pixbuf_column(0)
        self.viewport.connect("item-activated", self.on_wallpaper_selected)

        # Container centralizado
        self.center_box = Box(
            orientation="v",
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            h_expand=True,
            v_expand=True,
        )
        self.center_box.add(self.viewport)

        self.scrolled_window = ScrolledWindow(
            name="scrolled-window",
            h_expand=True,
            v_expand=True,
            min_content_width=800,
            child=self.center_box,
        )

        # Componentes da UI
        self.search_entry = Entry(
            name="search-entry-walls",
            placeholder="Search Wallpapers...",
            h_expand=True,
            halign=Gtk.Align.CENTER,
            notify_text=lambda entry, *_: self.arrange_viewport(entry.get_text()),
            on_key_press_event=self.on_search_entry_key_press,
        )
        self.search_entry.set_size_request(400, -1)

        # Dropdown de screens
        self.screen_dropdown = Gtk.ComboBoxText()
        self.screen_dropdown.set_name("screen-dropdown")
        self.screen_dropdown.append("all", "All Screens")
        for i, screen in enumerate(self.screens):
            self.screen_dropdown.append(screen, f"Screen {i+1}")
        self.screen_dropdown.set_active_id("all")

        # Dropdown de esquemas
        self.schemes = {
            "scheme-tonal-spot": "Tonal Spot",
            "scheme-content": "Content",
            "scheme-expressive": "Expressive",
            "scheme-fidelity": "Fidelity",
            "scheme-fruit-salad": "Fruit Salad",
            "scheme-monochrome": "Monochrome",
            "scheme-neutral": "Neutral",
            "scheme-rainbow": "Rainbow",
        }
        self.scheme_dropdown = Gtk.ComboBoxText()
        self.scheme_dropdown.set_name("scheme-dropdown")
        for key, display_name in self.schemes.items():
            self.scheme_dropdown.append(key, display_name)
        self.scheme_dropdown.set_active_id("scheme-tonal-spot")

        # Header
        self.header_box = CenterBox(
            name="header-box",
            spacing=20,
            start_children=[self.screen_dropdown],
            center_children=[self.search_entry],
            end_children=[self.scheme_dropdown],
        )

        self.add(self.header_box)
        self.add(self.scrolled_window)
        
        self._start_thumbnail_thread()
        self.setup_file_monitor()
        self.show_all()
        self.search_entry.grab_focus()

    def _load_nitro_screens(self):
        """Carrega os screens da configuração do Nitrogen"""
        config = configparser.ConfigParser()
        screens = []
        
        if os.path.exists(self.NITROGEN_CFG):
            try:
                config.read(self.NITROGEN_CFG)
                screens = [section for section in config.sections() if section.startswith('xin_')]
            except Exception as e:
                print(f"Erro ao ler configuração do Nitrogen: {e}")
        
        if not screens:
            screens = ['xin_0']
            
        return screens

    def _update_nitro_config(self, screen_id, wallpaper_path):
        """Atualiza o arquivo de configuração do Nitrogen"""
        config = configparser.ConfigParser()
        
        if os.path.exists(self.NITROGEN_CFG):
            config.read(self.NITROGEN_CFG)
        
        target_screens = [screen_id] if screen_id != "all" else self.screens
        
        for screen in target_screens:
            if not config.has_section(screen):
                config.add_section(screen)
            
            config.set(screen, 'file', wallpaper_path)
            config.set(screen, 'mode', '0')
        
        with open(self.NITROGEN_CFG, 'w') as configfile:
            config.write(configfile)

    def setup_file_monitor(self):
        gfile = Gio.File.new_for_path(self.WALLPAPERS_DIR)
        self.file_monitor = gfile.monitor_directory(Gio.FileMonitorFlags.NONE, None)
        self.file_monitor.connect("changed", self.on_directory_changed)

    def on_directory_changed(self, monitor, file, other_file, event_type):
        file_name = file.get_basename()
        if event_type == Gio.FileMonitorEvent.DELETED:
            if file_name in self.files:
                self.files.remove(file_name)
                cache_path = self._get_cache_path(file_name)
                if os.path.exists(cache_path):
                    try: os.remove(cache_path)
                    except Exception as e: print(f"Erro ao deletar cache {cache_path}: {e}")
                self.thumbnails = [(p, n) for p, n in self.thumbnails if n != file_name]
                GLib.idle_add(self.arrange_viewport, self.search_entry.get_text())
        elif event_type == Gio.FileMonitorEvent.CREATED:
            if self._is_image(file_name):
                new_name = file_name.lower().replace(" ", "-")
                full_path = os.path.join(self.WALLPAPERS_DIR, file_name)
                new_full_path = os.path.join(self.WALLPAPERS_DIR, new_name)
                if new_name != file_name and not os.path.exists(new_full_path):
                    try: os.rename(full_path, new_full_path)
                    except Exception as e: print(f"Erro ao renomear arquivo {full_path}: {e}")
                if new_name not in self.files:
                    self.files.append(new_name)
                    self.files.sort()
                    self.executor.submit(self._process_file, new_name)
        elif event_type == Gio.FileMonitorEvent.CHANGED:
            if self._is_image(file_name) and file_name in self.files:
                cache_path = self._get_cache_path(file_name)
                if os.path.exists(cache_path):
                    try: os.remove(cache_path)
                    except Exception as e: print(f"Erro ao deletar cache {file_name}: {e}")
                self.executor.submit(self._process_file, file_name)
        GLib.idle_add(self.viewport.queue_draw)

    def arrange_viewport(self, query: str = ""):
        model = self.viewport.get_model()
        model.clear()
        filtered = [(t, n) for t, n in self.thumbnails if query.casefold() in n.casefold()]
        filtered.sort(key=lambda x: x[1].lower())
        for pixbuf, name in filtered:
            model.append([pixbuf, name])
        if query.strip() == "":
            self.viewport.unselect_all()
            self.selected_index = -1
        elif len(model) > 0:
            self.update_selection(0)

    def on_wallpaper_selected(self, iconview, path):
        model = iconview.get_model()
        file_name = model[path][1]
        full_path = os.path.join(self.WALLPAPERS_DIR, file_name)
        selected_scheme = self.scheme_dropdown.get_active_id()
        selected_screen = self.screen_dropdown.get_active_id()
        
        self._update_nitro_config(selected_screen, full_path)
        exec_shell_command_async(f'matugen image {full_path} -t {selected_scheme}')

    def on_scheme_changed(self, combo):
        selected_scheme = combo.get_active_id()
        print(f"Esquema de cores selecionado: {selected_scheme}")

    def on_search_entry_key_press(self, widget, event):
        if event.keyval in (Gdk.KEY_Up, Gdk.KEY_Down, Gdk.KEY_Left, Gdk.KEY_Right):
            self.move_selection_2d(event.keyval)
            return True
        elif event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            if self.selected_index != -1:
                path = Gtk.TreePath.new_from_indices([self.selected_index])
                self.on_wallpaper_selected(self.viewport, path)
            return True
        return False

    def move_selection_2d(self, keyval):
        model = self.viewport.get_model()
        total = len(model)
        if total == 0: return

        current = self.selected_index if self.selected_index != -1 else 0
        columns = 5

        if keyval == Gdk.KEY_Right: new = current + 1
        elif keyval == Gdk.KEY_Left: new = current - 1
        elif keyval == Gdk.KEY_Down: new = current + columns
        elif keyval == Gdk.KEY_Up: new = current - columns
        else: return

        new = max(0, min(new, total - 1))
        self.update_selection(new)
    
    def update_selection(self, new_index: int):
        self.viewport.unselect_all()
        path = Gtk.TreePath.new_from_indices([new_index])
        self.viewport.select_path(path)
        self.viewport.scroll_to_path(path, False, 0.5, 0.5)
        self.selected_index = new_index

    def _start_thumbnail_thread(self):
        GLib.Thread.new("thumbnail-loader", self._preload_thumbnails, None)

    def _preload_thumbnails(self, _data):
        futures = [self.executor.submit(self._process_file, f) for f in self.files]
        concurrent.futures.wait(futures)

    def _process_file(self, file_name):
        try:
            full_path = os.path.join(self.WALLPAPERS_DIR, file_name)
            cache_path = self._get_cache_path(file_name)
            
            if not os.path.exists(cache_path):
                with Image.open(full_path) as img:
                    # Mantém o aspect ratio original e redimensiona para um retângulo
                    target_width = 192  # Largura aumentada para formato retangular
                    target_height = 108 # Altura reduzida
                    
                    # Calcula novas dimensões mantendo o aspect ratio
                    img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
                    
                    # Cria nova imagem com fundo preto para preencher espaços vazios
                    new_img = Image.new("RGB", (target_width, target_height), "black")
                    new_img.paste(
                        img,
                        (
                            (target_width - img.width) // 2,  # Centraliza horizontalmente
                            (target_height - img.height) // 2  # Centraliza verticalmente
                        )
                    )
                    
                    new_img.save(cache_path, "PNG")
            
            with self.thumb_lock:
                GLib.idle_add(partial(self._add_thumbnail, cache_path, file_name))
        except Exception as e:
            print(f"Erro ao processar {file_name}: {e}")
            GLib.idle_add(partial(self._handle_processing_error, file_name))

    def _add_thumbnail(self, cache_path, file_name):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(cache_path)
            self.thumbnails.append((pixbuf, file_name))
            if self.search_entry.get_text().casefold() in file_name.casefold():
                self.viewport.get_model().append([pixbuf, file_name])
        except Exception as e:
            print(f"Erro ao carregar thumbnail {cache_path}: {e}")

    def _handle_processing_error(self, file_name):
        if file_name in self.files:
            self.files.remove(file_name)
            self.thumbnails = [(p, n) for p, n in self.thumbnails if n != file_name]
            GLib.idle_add(self.arrange_viewport, self.search_entry.get_text())

    def _get_cache_path(self, file_name: str) -> str:
        file_hash = hashlib.md5(file_name.encode("utf-8")).hexdigest()
        return os.path.join(self.CACHE_DIR, f"{file_hash}.png")

    @staticmethod
    def _is_image(file_name: str) -> bool:
        return file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp'))

    def on_search_entry_focus_out(self, widget, event):
        if self.is_visible():
            widget.grab_focus()
        return False