import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gtk, Pango

from logic import CalculatorLogic


class GtkCalculator(Adw.ApplicationWindow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logic = CalculatorLogic()
        self.current_theme = "light"
        self.clipboard = Gdk.Display.get_default().get_clipboard()

        self.set_title("Kalkulator")
        self.set_default_size(360, 600)
        self.set_size_request(340, 580)
        self.set_resizable(True)

        self.css = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self._build_ui()
        self.apply_theme("light")
        self.update_display()
        self.update_history()
        self._sync_display_limit()
        self.connect("notify::width", self._on_window_size_changed)

        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_controller)

    def _build_ui(self):
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.root.add_css_class("root")
        self.set_content(self.root)

        self._build_top_menu()
        self._build_history_area()
        self._build_display_area()
        self._build_button_grid()

    def _build_top_menu(self):
        top_menu = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        top_menu.add_css_class("top-menu")
        top_menu.set_margin_start(12)
        top_menu.set_margin_end(12)
        top_menu.set_margin_top(4)
        top_menu.set_margin_bottom(4)

        self.settings_menu_btn = Gtk.MenuButton(label="Ustawienia")
        self.settings_menu_btn.add_css_class("menu-btn")
        self.settings_menu_btn.set_popover(self._build_settings_popover())

        self.about_btn = Gtk.Button(label="Opis")
        self.about_btn.add_css_class("menu-btn-active")
        self.about_btn.connect("clicked", lambda *_: self.show_about())

        self.min_btn = Gtk.Button(label="—")
        self.min_btn.add_css_class("win-btn")
        self.min_btn.connect("clicked", lambda *_: self.minimize())

        self.max_btn = Gtk.Button(label="❐")
        self.max_btn.add_css_class("win-btn")
        self.max_btn.connect("clicked", self._toggle_maximize)

        self.close_btn = Gtk.Button(label="✕")
        self.close_btn.add_css_class("win-close-btn")
        self.close_btn.connect("clicked", lambda *_: self.close())

        top_menu.append(self.settings_menu_btn)
        top_menu.append(self.about_btn)
        top_menu.append(Gtk.Box(hexpand=True))
        top_menu.append(self.min_btn)
        top_menu.append(self.max_btn)
        top_menu.append(self.close_btn)
        top_handle = Gtk.WindowHandle()
        top_handle.set_child(top_menu)
        self.root.append(top_handle)

    def _build_settings_popover(self):

        popover = Gtk.Popover()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(8)
        box.set_margin_end(8)

        btn_light = Gtk.Button(label="Motyw: Jasny")
        btn_light.connect("clicked", lambda *_: self.apply_theme("light"))

        btn_kiwi = Gtk.Button(label="Motyw: Kiwi")
        btn_kiwi.connect("clicked", lambda *_: self.apply_theme("kiwi"))

        self.always_on_top_switch = Gtk.CheckButton(label="Zawsze na wierzchu")
        self.always_on_top_switch.connect("toggled", self.on_toggle_always_on_top)

        btn_clear_history = Gtk.Button(label="Wyczysc historie")
        btn_clear_history.connect("clicked", lambda *_: self.clear_history())

        box.append(btn_light)
        box.append(btn_kiwi)
        box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        box.append(self.always_on_top_switch)
        box.append(btn_clear_history)
        popover.set_child(box)
        return popover

    def _build_history_area(self):
        self.history_scrolled = Gtk.ScrolledWindow()
        self.history_scrolled.set_min_content_height(95)
        self.history_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.history_scrolled.add_css_class("history-area")
        self.history_scrolled.set_vexpand(True)

        self.history_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.history_box.set_margin_start(20)
        self.history_box.set_margin_end(20)
        self.history_box.set_margin_top(10)
        self.history_box.set_margin_bottom(4)
        self.history_scrolled.set_child(self.history_box)
        self.root.append(self.history_scrolled)

        self.divider = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.divider.add_css_class("divider")
        self.root.append(self.divider)

    def _build_display_area(self):

        self.output_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.output_panel.set_vexpand(True)

        self.hint_label = Gtk.Label(label="")
        self.hint_label.set_xalign(1.0)
        self.hint_label.add_css_class("copy-hint")
        self.hint_label.set_margin_end(20)
        self.output_panel.append(self.hint_label)

        self.display_label = Gtk.Label(label="0")
        self.display_label.add_css_class("main-display")
        self.display_label.set_xalign(1.0)
        self.display_label.set_wrap(True)
        self.display_label.set_wrap_mode(Pango.WrapMode.CHAR)
        self.display_label.set_justify(Gtk.Justification.RIGHT)
        self.display_label.set_valign(Gtk.Align.END)
        self.display_label.set_vexpand(True)
        self.display_label.set_margin_start(20)
        self.display_label.set_margin_end(20)
        self.display_label.set_margin_top(6)
        self.display_label.set_margin_bottom(14)
        self.output_panel.append(self.display_label)
        self.root.append(self.output_panel)

    def _build_button_grid(self):

        self.grid_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.grid_container.add_css_class("grid-container")
        self.grid_container.set_vexpand(False)
        self.grid_container.set_hexpand(True)

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(False)
        self.grid.set_row_spacing(1)
        self.grid.set_column_spacing(1)
        self.grid.set_vexpand(False)
        self.grid.set_hexpand(True)
        self.grid.set_margin_start(0)
        self.grid.set_margin_end(0)
        self.grid.set_margin_top(0)
        self.grid.set_margin_bottom(0)

        buttons = [
            ("C", 0, 0, "btn-c"),
            ("xʸ", 0, 1, "btn-op"),
            ("√", 0, 2, "btn-op"),
            ("÷", 0, 3, "btn-op"),
            ("7", 1, 0, "btn-num"),
            ("8", 1, 1, "btn-num"),
            ("9", 1, 2, "btn-num"),
            ("×", 1, 3, "btn-op"),
            ("4", 2, 0, "btn-num"),
            ("5", 2, 1, "btn-num"),
            ("6", 2, 2, "btn-num"),
            ("−", 2, 3, "btn-op"),
            ("1", 3, 0, "btn-num"),
            ("2", 3, 1, "btn-num"),
            ("3", 3, 2, "btn-num"),
            ("+", 3, 3, "btn-op"),
            ("0", 4, 0, "btn-num"),
            (".", 4, 1, "btn-num"),
            ("=", 4, 2, "btn-eq", 2),
        ]

        for item in buttons:
            text, row, col, css_class = item[:4]
            span = item[4] if len(item) == 5 else 1
            btn = Gtk.Button(label=text)
            btn.add_css_class(css_class)
            btn.add_css_class("calc-btn")
            btn.set_hexpand(True)
            btn.set_vexpand(False)
            btn.set_size_request(-1, 60)
            btn.connect("clicked", self.on_click)
            self.grid.attach(btn, col, row, span, 1)

        self.grid_container.append(self.grid)
        self.root.append(self.grid_container)

    def on_click(self, btn):
        text = btn.get_label()
        if text == "C":
            self.logic.clear_all()
            self.hint_label.set_label("")
            self.update_display()
            return

        if text == "=":
            self.handle_eval()
            return

        symbol = "^" if text == "xʸ" else text
        self._sync_display_limit()
        self.logic.add_character(symbol)
        if self.logic.consume_input_limited():
            self.hint_label.set_label(">>> LIMIT ZNAKOW" if self.current_theme == "kiwi" else "Limit znakow")
        else:
            self.hint_label.set_label("")
        self.update_display()
        if text == "√":
            self.update_history()

    def handle_eval(self):

        result = self.logic.evaluate()
        self.update_display()
        self.update_history()
        if result.startswith("Błąd"):
            self.hint_label.set_label("")
            return
        self.hint_label.set_label("")

    def on_key_pressed(self, _controller, keyval, _keycode, state):

        ctrl = bool(state & Gdk.ModifierType.CONTROL_MASK)

        if ctrl and keyval in (Gdk.KEY_c, Gdk.KEY_C):
            self.clipboard.set_text(self.display_label.get_text())
            if self.current_theme == "kiwi":
                self.hint_label.set_label(">>> SCHOWEK: ZSYNCHRONIZOWANY")
            else:
                self.hint_label.set_label("Wynik skopiowany: Ctrl+C")
            return True

        if ctrl and keyval in (Gdk.KEY_v, Gdk.KEY_V):
            self._sync_display_limit()
            self.clipboard.read_text_async(None, self._on_clipboard_text_ready)
            return True

        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_equal):
            self.handle_eval()
            return True

        if keyval == Gdk.KEY_BackSpace:
            self.logic.backspace()
            self.hint_label.set_label("")
            self.update_display()
            return True

        if keyval == Gdk.KEY_Escape:
            self.logic.clear_all()
            self.hint_label.set_label("")
            self.update_display()
            return True

        ch = chr(Gdk.keyval_to_unicode(keyval)) if Gdk.keyval_to_unicode(keyval) else ""
        if ch and ch in "0123456789.+-*/^":
            self._sync_display_limit()
            self.logic.add_character(ch)
            if self.logic.consume_input_limited():
                self.hint_label.set_label(">>> LIMIT ZNAKOW" if self.current_theme == "kiwi" else "Limit znakow")
            else:
                self.hint_label.set_label("")
            self.update_display()
            return True

        return False

    def _on_clipboard_text_ready(self, clipboard, result):

        try:
            text = clipboard.read_text_finish(result)
        except Exception:
            return
        if not text:
            return

        self.logic.add_character(text)
        if self.logic.consume_input_limited():
            self.hint_label.set_label(">>> LIMIT ZNAKOW" if self.current_theme == "kiwi" else "Limit znakow")
        else:
            self.hint_label.set_label("")
        self.update_display()

    def update_display(self):

        self._sync_display_limit()
        raw_text = self.logic.current_expression
        self.display_label.set_label(self._format_display_text(raw_text))
        self.display_label.remove_css_class("display-error")
        if raw_text.startswith("Błąd"):
            self.display_label.add_css_class("display-error")

    def _format_display_text(self, text):

        if not text or text.startswith("Błąd"):
            return text or "0"

        char_px = max(1, self.display_label.create_pango_layout("8").get_pixel_size()[0])
        available_px = max(120, self.display_label.get_allocated_width() - 40)
        line_capacity = max(6, available_px // char_px)
        if len(text) <= line_capacity:
            return text

        chunks = [text[i: i + line_capacity] for i in range(0, len(text), line_capacity)]
        return "\n".join(chunks[-2:])

    def _sync_display_limit(self):

        char_px = max(1, self.display_label.create_pango_layout("8").get_pixel_size()[0])
        available_px = max(120, self.display_label.get_allocated_width() - 40)
        line_capacity = max(6, available_px // char_px)
        dynamic_limit = max(12, line_capacity * 2)
        self.logic.set_max_expression_length(dynamic_limit)

    def update_history(self):

        child = self.history_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.history_box.remove(child)
            child = next_child

        prefix = ">>> " if self.current_theme == "kiwi" else ""
        for entry in self.logic.get_history():
            label = Gtk.Label(label=f"{prefix}{entry}")
            label.set_xalign(1.0)
            label.add_css_class("hist-item")
            self.history_box.append(label)

    def clear_history(self):
        self.logic.clear_history()
        self.update_history()

    def on_toggle_always_on_top(self, btn):

        enabled = bool(btn.get_active())
        if hasattr(self, "set_keep_above"):
            self.set_keep_above(enabled)

    def apply_theme(self, theme):

        self.current_theme = theme
        self.set_title("Kalkulator [Tryb Kiwi]" if theme == "kiwi" else "Kalkulator")

        if theme == "kiwi":
            self.css.load_from_data(
                """
                .root { background: #0d0e0d; }
                .top-menu { background: #1a1b1a; border-bottom: 1px solid #2d2e2d; }
                .menu-btn { color: #aab8ab; background: transparent; border-radius: 6px; padding: 4px 6px; }
                .menu-btn:hover { background: #242524; color: #cfe4d1; }
                .menu-btn-active { color: #84cc16; font-weight: 700; background: transparent; border-radius: 6px; padding: 4px 6px; }
                .menu-btn-active:hover { background: #273027; color: #a3e635; }
                .win-btn { min-width: 34px; min-height: 28px; color: #ffffff; background: transparent; border: none; border-radius: 6px; }
                .win-btn:hover { background: #2a2c2a; }
                .win-close-btn { min-width: 34px; min-height: 28px; color: #ffffff; background: transparent; border: none; border-radius: 6px; }
                .win-close-btn:hover { background: #e81123; color: #ffffff; }
                .history-area { background: #0a0b0a; }
                .hist-item { color: #84cc16; font-family: "Segoe UI", "Inter", sans-serif; font-weight: 500; font-size: 13px; }
                .divider { color: #2d2e2d; background: #2d2e2d; }
                .copy-hint { color: #84cc16; font-family: "Segoe UI", "Inter", sans-serif; font-size: 10px; font-weight: 600; margin-top: 4px; }
                .main-display { color: #ecfccb; font-family: "Segoe UI", "Inter", sans-serif; font-weight: 500; font-size: 42px; line-height: 1.05; }
                .display-error { color: #f87171; font-size: 24px; font-weight: 600; }
                .grid-container { background: #0d0e0d; padding: 12px; }
                .calc-btn { background: #181918; color: #cbd5e1; border-radius: 8px; border: none; font-size: 20px; font-family: "Segoe UI", "Inter", sans-serif; font-weight: 600; }
                .calc-btn:hover { background: #222422; }
                .btn-op { color: #84cc16; }
                .btn-op:hover { background: #273027; color: #a3e635; }
                .btn-eq { background: #84cc16; color: #0d0e0d; font-weight: 700; }
                .btn-eq:hover { background: #a3e635; }
                .btn-c { color: #f87171; }
                .btn-c:hover { background: #3a1f25; color: #fca5a5; }
                .about-title { color: #84cc16; font-size: 26px; font-weight: 700; }
                .about-version { color: #94a3b8; font-size: 13px; }
                .about-text { color: #ffffff; font-size: 13px; }
                .about-shortcuts { background: rgba(0, 0, 0, 0.25); color: #ffffff; border-radius: 12px; padding: 10px; font-size: 12px; }
                .about-close { min-height: 40px; background: #84cc16; color: #0d0e0d; border: none; border-radius: 8px; font-weight: 700; }
                .about-close:hover { background: #a3e635; }
                .about-dialog-kiwi { background: #101116; }
                .about-dialog-kiwi .about-card { background: #1e293b; border: 1px solid #84cc16; border-radius: 20px; }
                """.encode()
            )
            self.grid.set_row_spacing(6)
            self.grid.set_column_spacing(6)
        else:
            self.css.load_from_data(
                """
                .root { background: #ffffff; }
                .top-menu { background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
                .menu-btn { color: #334155; background: transparent; border-radius: 6px; padding: 4px 6px; }
                .menu-btn:hover { background: #e2e8f0; color: #0f172a; }
                .menu-btn-active { color: #0067c0; font-weight: 700; background: transparent; border-radius: 6px; padding: 4px 6px; }
                .menu-btn-active:hover { background: #dbeafe; color: #0057a8; }
                .win-btn { min-width: 34px; min-height: 28px; color: #1f2937; background: transparent; border: none; border-radius: 6px; }
                .win-btn:hover { background: #e2e8f0; }
                .win-close-btn { min-width: 34px; min-height: 28px; color: #1f2937; background: transparent; border: none; border-radius: 6px; }
                .win-close-btn:hover { background: #e81123; color: #ffffff; }
                .history-area { background: #ffffff; }
                .hist-item { color: #64748b; font-family: "Segoe UI", "Inter", sans-serif; font-weight: 500; font-size: 13px; }
                .divider { color: rgba(0, 0, 0, 0.08); background: rgba(0, 0, 0, 0.08); }
                .copy-hint { color: #0067c0; font-family: "Segoe UI", "Inter", sans-serif; font-size: 10px; font-weight: 600; margin-top: 4px; }
                .main-display { color: #1e293b; font-family: "Segoe UI", "Inter", sans-serif; font-weight: 500; font-size: 42px; line-height: 1.05; }
                .display-error { color: #e11d48; font-size: 24px; font-weight: 600; }
                .grid-container { background: #eeeeee; padding: 0; }
                .calc-btn { background: #ffffff; color: #333333; border-radius: 0; border: none; font-size: 20px; font-family: "Segoe UI", "Inter", sans-serif; font-weight: 600; }
                .calc-btn:hover { background: #f1f5f9; }
                .btn-op { color: #0067c0; font-weight: 600; }
                .btn-op:hover { background: #e0f2fe; color: #0369a1; }
                .btn-eq { background: #0067c0; color: #ffffff; font-weight: 600; }
                .btn-eq:hover { background: #0b79d0; }
                .btn-c { color: #e11d48; }
                .btn-c:hover { background: #fee2e2; color: #be123c; }
                .about-title { color: #0067c0; font-size: 26px; font-weight: 700; }
                .about-version { color: #64748b; font-size: 13px; }
                .about-text { color: #1e293b; font-size: 13px; }
                .about-shortcuts { background: #e6f0fb; color: #1e3a5f; border-radius: 12px; padding: 10px; font-size: 12px; }
                .about-close { min-height: 40px; background: #0067c0; color: #ffffff; border: none; border-radius: 8px; font-weight: 700; }
                .about-close:hover { background: #0b79d0; }
                .about-dialog-light { background: #f1f5f9; }
                .about-dialog-light .about-card { background: #ffffff; border: 1px solid #0067c0; border-radius: 20px; }
                """.encode()
            )
            self.grid.set_row_spacing(1)
            self.grid.set_column_spacing(1)

        self.update_history()
        self.update_display()

    def show_about(self):

        dialog = Gtk.Dialog(transient_for=self, modal=True, title="Opis", use_header_bar=False)
        dialog.set_default_size(460, 300)
        dialog.set_size_request(460, 300)
        dialog.set_resizable(False)

        content = dialog.get_content_area()
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        content.set_margin_start(16)
        content.set_margin_end(16)

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        card.add_css_class("about-card")
        card.set_margin_top(0)
        card.set_margin_bottom(0)
        card.set_margin_start(0)
        card.set_margin_end(0)

        card_inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        card_inner.set_margin_top(22)
        card_inner.set_margin_bottom(18)
        card_inner.set_margin_start(24)
        card_inner.set_margin_end(24)

        title = Gtk.Label(label="Kalkulator")
        title.set_xalign(0.0)
        title.add_css_class("about-title")

        version = Gtk.Label(label="Wersja 1.0.0")
        version.set_xalign(0.0)
        version.add_css_class("about-version")

        desc = Gtk.Label(label="Aplikacja desktopowa wspierająca dynamiczne motywy i historię sesji.")
        desc.set_xalign(0.0)
        desc.set_wrap(True)
        desc.add_css_class("about-text")

        shortcuts = Gtk.Label(
            label="<b>Skróty:</b> [Enter] Wynik   [Ctrl+C] Kopiuj   [Ctrl+V] Wklej   [Esc] Czyść"
        )
        shortcuts.set_use_markup(True)
        shortcuts.set_xalign(0.0)
        shortcuts.set_wrap(True)
        shortcuts.add_css_class("about-shortcuts")

        author = Gtk.Label(label="Autor: <b>Piotr Zienowicz</b>\nNr indeksu: <b>212032</b>")
        author.set_use_markup(True)
        author.set_xalign(0.0)
        author.add_css_class("about-text")

        close_btn = Gtk.Button(label="ZAMKNIJ")
        close_btn.add_css_class("about-close")
        close_btn.set_hexpand(True)
        close_btn.connect("clicked", lambda *_: dialog.close())

        spacer = Gtk.Box(vexpand=True)

        card_inner.append(title)
        card_inner.append(version)
        card_inner.append(desc)
        card_inner.append(shortcuts)
        card_inner.append(author)
        card_inner.append(spacer)
        card_inner.append(close_btn)

        card.append(card_inner)
        content.append(card)

        if self.current_theme == "kiwi":
            dialog.add_css_class("about-dialog-kiwi")
        else:
            dialog.add_css_class("about-dialog-light")

        dialog.present()

    def _toggle_maximize(self, *_args):
        if self.is_maximized():
            self.unmaximize()
        else:
            self.maximize()

    def _on_window_size_changed(self, *_args):
        self._sync_display_limit()
        self.update_display()


class GtkApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="pl.piotr.calc")

    def do_activate(self):
        win = GtkCalculator(application=self)
        win.present()


if __name__ == "__main__":
    import sys

    GtkApp().run(sys.argv)
