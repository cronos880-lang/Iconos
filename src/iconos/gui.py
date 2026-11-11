"""Interfaz nativa compacta para Windows, independiente del motor de conversión."""
from __future__ import annotations
import queue
import threading
import base64
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk, ImageOps
from .core import ConversionOptions, ConversionError, EXTENSIONS, SIZES, convert_file
from .auto_filter import recommend_filter

BG = '#151b25'
PANEL = '#202936'
FIELD = '#293545'
TEXT = '#eaf0f8'
MUTED = '#aab9ce'
BLUE = '#3089e9'

# Icono original de la aplicación, embebido para que funcione también al compilar el EXE.
_ICON_PNG_BASE64 = (
    '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'
    'RK5CYII='
)


class IconosApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Iconos — V0.1.5')
        self.geometry(f'{min(960, self.winfo_screenwidth()-80)}x{min(690, self.winfo_screenheight()-120)}')
        self.minsize(700, 460)
        self.configure(bg=BG)
        # Mantener referencia para evitar que Tkinter libere la imagen.
        self._app_icon = tk.PhotoImage(data=_ICON_PNG_BASE64)
        self.iconphoto(True, self._app_icon)
        self.sources: list[Path] = []
        self.events: queue.Queue = queue.Queue()
        self.working = False
        self.preview = None
        self.output = tk.StringVar(value=str(Path.home() / 'Desktop'))
        self.output_name = tk.StringVar()
        self._name_source = None
        self.mode = tk.StringVar(value='center')
        self.filter = tk.StringVar(value='auto')
        self.filter_recommendation = None
        self.filter_info = tk.StringVar(value='Automático: añade una imagen para analizarla.')
        self.status = tk.StringVar(value='Añade imágenes para comenzar.')
        self.flags = {n: tk.BooleanVar(value=True) for n in SIZES}
        self._styles()
        self._make_ui()
        # En Windows abrir maximizada, sin ocultar los controles de la ventana.
        # Se solicita tras crear los widgets, para que el gestor de ventanas
        # aplique correctamente el estado maximizado al mostrar la GUI.
        if self.tk.call('tk', 'windowingsystem') == 'win32':
            self.after_idle(lambda: self.state('zoomed'))
        self.protocol('WM_DELETE_WINDOW', self._exit_app)
        self.after(100, self._poll)

    def _styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background=BG)
        style.configure('TLabel', background=BG, foreground=TEXT, font=('Segoe UI', 10))
        style.configure('Sub.TLabel', foreground=MUTED, background=BG, font=('Segoe UI', 9))
        style.configure('TButton', font=('Segoe UI', 10), padding=(10, 7), background=FIELD, foreground=TEXT, borderwidth=0)
        style.map('TButton', background=[('active', '#38495e')])
        style.configure('Accent.TButton', background=BLUE, foreground='white', font=('Segoe UI Semibold', 10), padding=(15, 9))
        style.map('Accent.TButton', background=[('active', '#2074cb')])
        # Forzar colores coherentes incluso en estado readonly/focus/active en Windows.
        style.configure('Iconos.TCombobox', fieldbackground=FIELD, background=FIELD,
                        foreground=TEXT, arrowcolor=TEXT, bordercolor='#3b4b60',
                        lightcolor=FIELD, darkcolor=FIELD, selectforeground=TEXT,
                        selectbackground=FIELD, padding=3)
        style.map('Iconos.TCombobox',
                  fieldbackground=[('disabled', FIELD), ('readonly', FIELD), ('focus', FIELD), ('active', FIELD)],
                  background=[('disabled', FIELD), ('readonly', FIELD), ('active', FIELD)],
                  foreground=[('disabled', MUTED), ('readonly', TEXT), ('focus', TEXT), ('active', TEXT)],
                  selectforeground=[('readonly', TEXT), ('focus', TEXT)],
                  selectbackground=[('readonly', FIELD), ('focus', FIELD)],
                  arrowcolor=[('disabled', MUTED), ('readonly', TEXT), ('active', TEXT)])
        self.option_add('*TCombobox*Listbox.background', FIELD)
        self.option_add('*TCombobox*Listbox.foreground', TEXT)
        self.option_add('*TCombobox*Listbox.selectBackground', '#225d96')
        self.option_add('*TCombobox*Listbox.selectForeground', '#ffffff')
        style.configure('TCheckbutton', background=BG, foreground=TEXT, font=('Segoe UI', 9))
        style.map('TCheckbutton', background=[('active', BG)], foreground=[('active', TEXT)])
        style.configure('Horizontal.TProgressbar', troughcolor=FIELD, background=BLUE)

    def _make_ui(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill='x', padx=22, pady=(18, 12))
        # Identidad visual propia: icono junto al título y botón Salir.
        self._header_icon = self._app_icon.subsample(2, 2)
        tk.Label(header, image=self._header_icon, bg=BG).pack(side='left', padx=(0, 12))
        tk.Label(header, text='ICONOS', bg=BG, fg=TEXT, font=('Segoe UI Semibold', 20)).pack(side='left')
        ttk.Button(header, text='Salir', command=self._exit_app).pack(side='right', padx=(14, 0))
        tk.Label(header, text='Conversor ICO   ·   V0.1.5 PRUEBAS', bg=BG, fg=MUTED, font=('Segoe UI', 10)).pack(side='right', pady=9)
        # Zona central desplazable: los controles nunca deben quedar fuera de pantalla.
        body_wrap = ttk.Frame(self)
        body_wrap.pack(fill='both', expand=True, padx=12)
        self.body_canvas = tk.Canvas(body_wrap, bg=BG, highlightthickness=0, bd=0)
        self.body_canvas.pack(side='left', fill='both', expand=True)
        self.body_scroll = ttk.Scrollbar(body_wrap, orient='vertical', command=self.body_canvas.yview)
        self.body_scroll.pack(side='right', fill='y')
        self.body_canvas.configure(yscrollcommand=self.body_scroll.set)
        body = ttk.Frame(self.body_canvas)
        body_window = self.body_canvas.create_window((0, 0), window=body, anchor='nw')
        body.bind('<Configure>', lambda e: self.body_canvas.configure(scrollregion=self.body_canvas.bbox('all')))
        self.body_canvas.bind('<Configure>', lambda e: self.body_canvas.itemconfigure(body_window, width=e.width))
        # Nunca usar bind_all para la rueda: al desplegar un Combobox podía
        # desplazar toda la página y hacer desaparecer la vista previa.
        self.body_canvas.bind('<MouseWheel>', self._on_mousewheel)
        top = ttk.Frame(body)
        top.pack(fill='x', padx=10)
        left = ttk.Frame(top)
        left.pack(side='left', fill='x', expand=True)
        right = ttk.Frame(top)
        right.pack(side='right', fill='y', padx=(18, 0))
        ttk.Label(left, text='Imágenes de origen').pack(anchor='w', pady=(0, 7))
        listbox_frame = tk.Frame(left, bg=FIELD, highlightthickness=1, highlightbackground='#3b4b60')
        listbox_frame.pack(fill='x')
        self.listbox = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED, font=('Segoe UI', 10), bg=FIELD, fg=TEXT, selectbackground='#225d96', selectforeground='white', activestyle='none', bd=0, highlightthickness=0, height=5, exportselection=False)
        self.listbox.pack(side='left', fill='x', expand=True, padx=8, pady=8)
        self.listbox.bind('<<ListboxSelect>>', self._on_select)
        scroll = ttk.Scrollbar(listbox_frame, command=self.listbox.yview)
        scroll.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=scroll.set)
        actions = ttk.Frame(left)
        actions.pack(fill='x', pady=(9, 15))
        ttk.Button(actions, text='+ Añadir imágenes', command=self._add).pack(side='left')
        ttk.Button(actions, text='Quitar selección', command=self._remove).pack(side='left', padx=(8, 0))
        ttk.Button(actions, text='Vaciar', command=self._clear).pack(side='left', padx=(8, 0))
        ttk.Label(right, text='Vista previa').pack(anchor='w', pady=(0, 7))
        self.preview_canvas = tk.Canvas(right, width=205, height=205, bg=FIELD, highlightthickness=1, highlightbackground='#3b4b60')
        self.preview_canvas.pack()
        self.preview_canvas.create_text(103, 103, text='Sin imagen', fill=MUTED, font=('Segoe UI', 11))
        ttk.Label(right, text='PNG · JPG · WebP', style='Sub.TLabel').pack(anchor='w', pady=(9, 0))
        sep = tk.Frame(body, bg='#334257', height=1)
        sep.pack(fill='x', padx=10, pady=(0, 12))
        dest_frame = ttk.Frame(body)
        dest_frame.pack(fill='x', padx=10)
        ttk.Label(dest_frame, text='Carpeta de destino').pack(anchor='w')
        dest = ttk.Frame(dest_frame)
        dest.pack(fill='x', pady=(6, 12))
        entry = tk.Entry(dest, textvariable=self.output, bg=FIELD, fg=TEXT, insertbackground=TEXT, relief='flat', font=('Segoe UI', 10), highlightthickness=1, highlightbackground='#3b4b60')
        entry.pack(side='left', fill='x', expand=True, ipady=8)
        ttk.Button(dest, text='Examinar', command=self._destination).pack(side='right', padx=(10, 0))
        name_row = ttk.Frame(dest_frame)
        name_row.pack(fill='x', pady=(0, 12))
        ttk.Label(name_row, text='Nombre del archivo ICO').pack(side='left', padx=(0, 12))
        self.name_entry = tk.Entry(name_row, textvariable=self.output_name, bg=FIELD, fg=TEXT,
                                   insertbackground=TEXT, relief='flat', font=('Segoe UI', 10),
                                   highlightthickness=1, highlightbackground='#3b4b60')
        self.name_entry.pack(side='left', fill='x', expand=True, ipady=6)
        self.name_hint = ttk.Label(dest_frame, text='Para varios archivos se conserva el nombre de cada imagen.', style='Sub.TLabel')
        self._update_name_state()
        opts = ttk.Frame(body)
        opts.pack(fill='x', padx=10)
        ttk.Label(opts, text='Ajuste de imagen').grid(row=0, column=0, sticky='w')
        ttk.Label(opts, text='Filtro').grid(row=0, column=1, sticky='w', padx=(18, 0))
        self.mode_combo = ttk.Combobox(opts, values=('Centrar', 'Recortar', 'Estirar'), state='readonly', width=18, style='Iconos.TCombobox')
        self.mode_combo.current(0)
        self.mode_combo.grid(row=1, column=0, sticky='w', pady=(5, 10))
        self.filter_combo = ttk.Combobox(opts, values=('Automático', 'Lanczos', 'Bicubic'), state='readonly', width=17, style='Iconos.TCombobox')
        self.filter_combo.current(0)
        self.filter_combo.bind('<<ComboboxSelected>>', self._on_filter_mode_change)
        self.filter_combo.grid(row=1, column=1, sticky='w', padx=(18, 0), pady=(5, 10))
        self.filter_info_label = ttk.Label(opts, textvariable=self.filter_info, style='Sub.TLabel', wraplength=440)
        self.filter_info_label.grid(row=2, column=0, columnspan=2, sticky='w', pady=(0, 7))
        ttk.Label(body, text='Resoluciones (píxeles)').pack(anchor='w', padx=10)
        sizes = ttk.Frame(body)
        sizes.pack(fill='x', padx=10, pady=(6, 14))
        for n in SIZES:
            ttk.Checkbutton(sizes, text=str(n), variable=self.flags[n]).pack(side='left', padx=(0, 20))
        tk.Frame(self, bg='#334257', height=1).pack(fill='x', padx=12, pady=(4, 8))
        foot = ttk.Frame(self)
        foot.pack(side='bottom', fill='x', padx=18, pady=(0, 10))
        ttk.Label(foot, textvariable=self.status, style='Sub.TLabel', wraplength=550).pack(side='left', fill='x', expand=True)
        self.go = ttk.Button(foot, text='Convertir a ICO', style='Accent.TButton', command=self._start)
        self.go.pack(side='right')
        self.progress = ttk.Progressbar(self, mode='determinate', maximum=100)
        self.progress.pack(side='bottom', fill='x', padx=18, pady=(0, 6))

    def _on_mousewheel(self, event):
        if event.delta:
            self.body_canvas.yview_scroll(-int(event.delta / 120), 'units')

    def _on_filter_mode_change(self, event=None):
        selected = self.filter_combo.get()
        if selected == 'Automático':
            self._update_auto()
        else:
            self.filter_info.set('Filtro manual: ' + selected + '. No se realizará selección automática.')

    def _exit_app(self):
        if self.working and not messagebox.askyesno(
            'Iconos',
            'Hay una conversión en curso. ¿Quieres cerrar el programa?'
        ):
            return
        self.destroy()

    def _add(self):
        files = filedialog.askopenfilenames(title='Seleccionar imágenes', filetypes=[('Imágenes', '*.png *.jpg *.jpeg *.webp'), ('Todos los archivos', '*.*')])
        existing = {str(p).casefold() for p in self.sources}
        for name in files:
            path = Path(name)
            if str(path).casefold() not in existing and path.suffix.lower() in EXTENSIONS:
                self.sources.append(path)
                self.listbox.insert('end', path.name)
                existing.add(str(path).casefold())
        self._update_name_state()
        self._on_filter_mode_change()
        if self.sources:
            self.listbox.selection_clear(0, 'end')
            self.listbox.selection_set(len(self.sources) - 1)
            self._on_select()
            self.status.set(f'{len(self.sources)} imagen(es) seleccionada(s).')

    def _remove(self):
        for index in reversed(self.listbox.curselection()):
            self.listbox.delete(index)
            self.sources.pop(index)
        self._update_name_state()
        self._on_filter_mode_change()
        self._on_select()

    def _clear(self):
        self.sources.clear()
        self.listbox.delete(0, 'end')
        self._update_name_state()
        self._on_filter_mode_change()
        self._on_select()

    def _update_auto(self):
        self.filter_recommendation = None
        if not self.sources:
            self.filter_info.set('Automático: añade una imagen para analizarla.')
            return
        try:
            # En lotes se analiza cada imagen de forma independiente durante la conversión.
            if len(self.sources) > 1:
                self.filter_info.set('Automático: cada imagen del lote tendrá su propio filtro.')
            else:
                suggestion = recommend_filter(self.sources[0])
                self.filter_recommendation = suggestion.filter_name
                self.filter_info.set('Automático aconseja ' + suggestion.filter_name.capitalize() + ': ' + suggestion.reason)
        except (OSError, ValueError, Image.DecompressionBombError) as exc:
            self.filter_recommendation = 'lanczos'
            self.filter_info.set('No se pudo analizar; se usará Lanczos. ' + str(exc)[:90])

    def _on_select(self, event=None):
        self.preview_canvas.delete('all')
        self.preview = None
        indices = self.listbox.curselection()
        if not indices:
            self.preview_canvas.create_text(103, 103, text='Sin imagen', fill=MUTED, font=('Segoe UI', 11))
            return
        try:
            with Image.open(self.sources[indices[0]]) as im:
                frame = ImageOps.exif_transpose(im).convert('RGBA')
                frame.thumbnail((190, 190), Image.Resampling.LANCZOS)
                self.preview = ImageTk.PhotoImage(frame)
                self.preview_canvas.create_image(103, 103, image=self.preview)
        except (OSError, ValueError, Image.DecompressionBombError):
            self.preview_canvas.create_text(103, 103, text='Vista previa no disponible', fill=MUTED)

    def _update_name_state(self):
        # El nombre personalizado solo se aplica cuando hay una imagen.
        if len(self.sources) == 1:
            self.name_entry.config(state='normal')
            selected_source = str(self.sources[0])
            if self._name_source != selected_source:
                self.output_name.set(self.sources[0].stem + '.ico')
                self._name_source = selected_source
            self.name_hint.pack_forget()
        else:
            self.name_entry.config(state='disabled')
            self.name_hint.pack(anchor='w', pady=(0, 7))
            if not self.sources:
                self.output_name.set('')
                self._name_source = None

    def _destination(self):
        current_dir = self.output.get()
        initial = current_dir if Path(current_dir).is_dir() else str(Path.home())
        if len(self.sources) == 1:
            filename = self.output_name.get().strip() or (self.sources[0].stem + '.ico')
            selected = filedialog.asksaveasfilename(
                title='Elegir destino y nombre del icono', initialdir=initial,
                initialfile=filename, defaultextension='.ico',
                filetypes=[('Icono Windows', '*.ico')]
            )
            if selected:
                target = Path(selected)
                self.output.set(str(target.parent))
                self.output_name.set(target.name)
        else:
            folder = filedialog.askdirectory(title='Elegir carpeta de destino', initialdir=initial)
            if folder:
                self.output.set(folder)

    def _start(self):
        if self.working:
            return
        if not self.sources:
            messagebox.showwarning('Iconos', 'Añade una o varias imágenes.')
            return
        destination = Path(self.output.get())
        if not destination.is_dir():
            messagebox.showerror('Iconos', 'Selecciona una carpeta de destino existente.')
            return
        sizes = tuple(n for n in SIZES if self.flags[n].get())
        try:
            filter_choice = ('auto', 'lanczos', 'bicubic')[self.filter_combo.current()]
            options = ConversionOptions(mode=('center', 'crop', 'stretch')[self.mode_combo.current()], sizes=sizes, resample='lanczos' if filter_choice == 'auto' else filter_choice)
            options.validate()
        except ConversionError as exc:
            messagebox.showerror('Iconos', str(exc))
            return
        # El motor permanece intacto: solo la GUI selecciona el nombre de salida.
        chosen_name = None
        if len(self.sources) == 1:
            chosen_name = self.output_name.get().strip()
            if not chosen_name:
                messagebox.showwarning('Iconos', 'Escribe un nombre para el archivo ICO.')
                return
            if chosen_name.lower().endswith('.ico'):
                chosen_name = chosen_name[:-4]
            if not chosen_name or chosen_name in {'.', '..'} or any(c in chosen_name for c in '<>:"/\\|?*') or chosen_name.endswith(('.', ' ')):
                messagebox.showerror('Iconos', 'El nombre del archivo ICO no es válido para Windows.')
                return
        # Conservar todos los resultados previos: nombres con sufijo incremental.
        sources = list(self.sources)
        self.working = True
        self.go.state(['disabled'])
        self.progress['value'] = 0
        self.status.set('Convirtiendo imágenes…')
        threading.Thread(target=self._worker, args=(sources, destination, options, chosen_name, filter_choice), daemon=True).start()

    def _worker(self, sources, destination, options, chosen_name=None, filter_choice='lanczos'):
        results = []
        for i, source in enumerate(sources, 1):
            try:
                base = destination / f'{chosen_name if chosen_name is not None else source.stem}.ico'
                candidate = base
                suffix = 1
                while candidate.exists():
                    candidate = destination / f'{chosen_name if chosen_name is not None else source.stem}_{suffix}.ico'
                    suffix += 1
                # Si otra aplicación crea ese archivo al mismo tiempo, no sobrescribimos.
                # Selector separado del core; todas las opciones del motor son originales.
                if filter_choice == 'auto':
                    try:
                        chosen_filter = recommend_filter(source).filter_name
                    except (OSError, ValueError, Image.DecompressionBombError):
                        chosen_filter = 'lanczos'
                    from dataclasses import replace
                    selected_options = replace(options, resample=chosen_filter)
                else:
                    chosen_filter = filter_choice
                    selected_options = options
                final_path = convert_file(source, candidate, selected_options)
                results.append((source.name, str(final_path), None))
                self.events.put(('filter_used', source.name, chosen_filter))
            except (ConversionError, OSError, ValueError) as exc:
                results.append((source.name, '', str(exc)))
            self.events.put(('progress', i / len(sources) * 100, i, len(sources)))
        self.events.put(('done', results))

    def _poll(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == 'filter_used':
                    self.filter_info.set(f'Última conversión: {event[1]} → {event[2].capitalize()}')
                elif event[0] == 'progress':
                    _, progress, current, total = event
                    self.progress['value'] = progress
                    self.status.set(f'Procesadas {current} de {total} imágenes.')
                elif event[0] == 'done':
                    results = event[1]
                    good = sum(error is None for _, _, error in results)
                    fail = len(results) - good
                    self.status.set(f'Finalizado: {good} correctas, {fail} errores.')
                    self.working = False
                    self.go.state(['!disabled'])
                    if fail:
                        detail = '\n'.join(f'{name}: {err}' for name, _, err in results if err)
                        messagebox.showwarning('Iconos — Resultados', f'Convertidas: {good}\nErrores: {fail}\n\n{detail[:2500]}')
                    else:
                        messagebox.showinfo('Iconos — Resultados', f'Se han creado {good} iconos correctamente.\n\nCarpeta: {self.output.get()}')
        except queue.Empty:
            pass
        self.after(100, self._poll)


def main():
    IconosApp().mainloop()

if __name__ == '__main__':
    main()
