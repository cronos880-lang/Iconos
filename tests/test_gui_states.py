"""Regresión visual de selecciones. En entorno sin pantalla se omite."""
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from PIL import Image
from iconos.gui import IconosApp

class GuiStateTests(unittest.TestCase):
    def test_preview_survives_combobox_changes(self):
        try:
            app = IconosApp()
        except tk.TclError:
            self.skipTest('Prueba gráfica requiere pantalla')
        try:
            with tempfile.TemporaryDirectory() as d:
                src = Path(d) / 'control.png'
                Image.new('RGBA', (64,64), (40,130,190,128)).save(src)
                app.sources.append(src)
                app.listbox.insert('end',src.name)
                app.listbox.selection_set(0)
                app._on_select()
                app.update()
                self.assertIsNotNone(app.preview)
                app.filter_combo.focus_set()
                for val in ('Automático','Lanczos','Bicubic','Automático'):
                    app.filter_combo.set(val)
                    app._on_filter_mode_change()
                    app.update()
                    self.assertEqual(app.listbox.curselection(),(0,))
                    self.assertIsNotNone(app.preview)
                    self.assertEqual(len(app.preview_canvas.find_all()),1)
                for val in ('Centrar','Recortar','Estirar'):
                    app.mode_combo.set(val)
                    app.update()
                    self.assertIsNotNone(app.preview)
        finally:
            app.destroy()
