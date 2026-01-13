import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from .ui_interface import UserInterface


class TkinterUI(UserInterface):
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.attributes('-topmost', True)
        self.progress_win = None
        self.progress_bar = None
        self.progress_label = None

    def _get_top_level(self):
        return self.root

    def show_message(self, message: str, level: str = "info"):
        parent = self._get_top_level()
        if level == "error":
            messagebox.showerror("Error", message, parent=parent)
        elif level == "warning":
            messagebox.showwarning("Advertencia", message, parent=parent)
        elif level == "success":
            messagebox.showinfo("Éxito", message, parent=parent)
        else:
            messagebox.showinfo("Información", message, parent=parent)

    def get_input(self, prompt: str, default: str = None) -> str:
        parent = self._get_top_level()
        return simpledialog.askstring("Entrada requerida", prompt, initialvalue=default, parent=parent)

    def confirm(self, prompt: str) -> bool:
        parent = self._get_top_level()
        return messagebox.askyesno("Confirmación", prompt, parent=parent)

    def get_selection(self, prompt: str, options: list) -> str:
        """
        Crea una ventana personalizada con un Combobox para seleccionar opciones.
        """
        if not options:
            return None

        # Ventana modal personalizada
        dialog = tk.Toplevel(self.root)
        dialog.title("Selección")
        dialog.attributes("-topmost", True)
        dialog.geometry("300x150")
        dialog.resizable(False, False)

        # Centrar en pantalla (aprox)
        x = self.root.winfo_screenwidth() // 2 - 150
        y = self.root.winfo_screenheight() // 2 - 75
        dialog.geometry(f"+{x}+{y}")

        # Widgets
        ttk.Label(dialog, text=prompt, wraplength=280).pack(pady=10)

        selected_var = tk.StringVar()
        combo = ttk.Combobox(dialog, values=options,
                             textvariable=selected_var, state="readonly")
        combo.pack(pady=5, padx=10, fill="x")
        combo.current(0)  # Seleccionar el primero por defecto

        result = {"value": None}

        def on_ok():
            result["value"] = selected_var.get()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        # Botones
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Aceptar",
                   command=on_ok).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancelar",
                   command=on_cancel).pack(side="left", padx=5)

        # Esperar a que se cierre
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

        return result["value"]

    def show_table(self, headers: list, data: list):
        """Muestra una tabla en una ventana nueva con Scrollbar."""
        win = tk.Toplevel(self.root)
        win.title("Reporte de Datos")
        win.attributes("-topmost", True)
        win.geometry("600x400")

        # Frame contenedor
        frame = ttk.Frame(win)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview (Tabla)
        tree = ttk.Treeview(frame, columns=headers, show="headings")

        # Scrollbars
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        # Configurar cabeceras
        for col in headers:
            tree.heading(col, text=col)
            tree.column(col, width=100)  # Ancho base

        # Insertar datos
        for row in data:
            # Asegurar que sean strings
            clean_row = [str(item) for item in row]
            tree.insert("", "end", values=clean_row)

        # Botón Cerrar
        ttk.Button(win, text="Cerrar", command=win.destroy).pack(pady=5)

        # Bloquear ejecución hasta cerrar tabla (como el input de consola)
        win.transient(self.root)
        win.grab_set()
        self.root.wait_window(win)

    def progress_start(self, total: int, description: str):
        """Crea una ventana flotante con barra de carga."""
        if self.progress_win:
            self.progress_win.destroy()

        self.progress_win = tk.Toplevel(self.root)
        self.progress_win.title("Procesando...")
        self.progress_win.attributes("-topmost", True)
        self.progress_win.geometry("300x100")
        # Quitar bordes de ventana (estilo splash)
        self.progress_win.overrideredirect(True)

        # Centrar
        x = self.root.winfo_screenwidth() // 2 - 150
        y = self.root.winfo_screenheight() // 2 - 50
        self.progress_win.geometry(f"+{x}+{y}")

        # Marco con borde
        frame = tk.Frame(self.progress_win, relief="raised", borderwidth=2)
        frame.pack(fill="both", expand=True)

        self.progress_label = ttk.Label(frame, text=description)
        self.progress_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(
            frame, orient="horizontal", length=250, mode="determinate")
        self.progress_bar.pack(pady=10)
        self.progress_bar["maximum"] = total
        self.progress_bar["value"] = 0

        self.root.update()  # Forzar dibujado inmediato

    def progress_update(self, step: int = 1):
        if self.progress_bar:
            self.progress_bar["value"] += step
            # Importante: Actualizar la GUI para que no se congele
            self.root.update()

    def progress_stop(self):
        if self.progress_win:
            self.progress_win.destroy()
            self.progress_win = None
            self.root.update()
