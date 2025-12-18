import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from risk_predictor import predecir_riesgo, predecir_riesgo_neurona
from factor_explainer import explicacion_por_cada_factor

APP_TITLE = "AURA • Predicción de Riesgo Cardiovascular"
DEFAULT_MODEL_FILE = "modelo_random_forest_entrenado.joblib"


def clamp(v, vmin, vmax):
    return max(vmin, min(v, vmax))


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def draw_vertical_gradient(canvas: tk.Canvas, x0, y0, x1, y1, top_hex, bottom_hex, steps=180):
    top = hex_to_rgb(top_hex)
    bot = hex_to_rgb(bottom_hex)
    height = max(1, int(y1 - y0))
    steps = max(2, min(steps, height))
    for i in range(steps):
        t = i / (steps - 1)
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        y = y0 + int((height * i) / steps)
        canvas.create_rectangle(x0, y, x1, y + int(height / steps) + 2, outline="", fill=rgb_to_hex((r, g, b)), tags="grad")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x600")
        self.minsize(930, 560)

        self.model_path = os.path.join(os.path.dirname(__file__), DEFAULT_MODEL_FILE)
        self.model_type = tk.StringVar(value="random_forest")

        self.var_age = tk.StringVar()
        self.var_ef = tk.StringVar()
        self.var_crea = tk.StringVar()
        self.var_sodium = tk.StringVar()

        # Paleta moderna
        self.C_BG = "#0b1020"
        self.C_CARD = "#121a33"
        self.C_CARD2 = "#10172d"
        self.C_TEXT = "#e8ecff"
        self.C_MUTED = "#aab2d5"
        self.C_BORDER = "#22305c"
        self.C_ACCENT = "#7c5cff"
        self.C_ACCENT2 = "#29d6ff"
        self.C_DANGER = "#ff4d6d"
        self.C_WARN = "#ffb020"
        self.C_OK = "#33d69f"

        self._build_style()
        self._build_ui()
        self._redraw_background()
        self.bind("<Configure>", lambda e: self._redraw_background())

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(".", font=("Segoe UI", 10))
        style.configure("TFrame", background=self.C_BG)

        style.configure("Card.TFrame", background=self.C_CARD)
        style.configure("Card2.TFrame", background=self.C_CARD2)

        style.configure("TLabel", background=self.C_CARD, foreground=self.C_TEXT)
        style.configure("Muted.TLabel", background=self.C_CARD, foreground=self.C_MUTED)
        style.configure("Header.TLabel", background=self.C_CARD, foreground=self.C_TEXT, font=("Segoe UI Semibold", 18))
        style.configure("Title2.TLabel", background=self.C_CARD, foreground=self.C_TEXT, font=("Segoe UI Semibold", 12))

        style.configure("Card.TLabelframe", background=self.C_CARD, foreground=self.C_TEXT)
        style.configure("Card.TLabelframe.Label", background=self.C_CARD, foreground=self.C_TEXT, font=("Segoe UI Semibold", 10))

        style.configure("TEntry",
                        fieldbackground="#0e1530",
                        foreground=self.C_TEXT,
                        bordercolor=self.C_BORDER,
                        lightcolor=self.C_BORDER,
                        darkcolor=self.C_BORDER,
                        insertcolor=self.C_TEXT,
                        padding=8)
        style.map("TEntry",
                  bordercolor=[("focus", self.C_ACCENT)],
                  lightcolor=[("focus", self.C_ACCENT)],
                  darkcolor=[("focus", self.C_ACCENT)])

        style.configure("Primary.TButton",
                        background=self.C_ACCENT,
                        foreground="white",
                        padding=(14, 10),
                        borderwidth=0,
                        focusthickness=0)
        style.map("Primary.TButton",
                  background=[("active", "#6a49ff"), ("disabled", "#3a3560")],
                  foreground=[("disabled", "#c6c6c6")])

        style.configure("Ghost.TButton",
                        background=self.C_CARD2,
                        foreground=self.C_TEXT,
                        padding=(14, 10),
                        borderwidth=1,
                        relief="flat")
        style.map("Ghost.TButton",
                  background=[("active", "#18224a")],
                  foreground=[("disabled", "#7f86a8")])

        style.configure("TRadiobutton",
                        background=self.C_CARD,
                        foreground=self.C_TEXT,
                        indicatorcolor=self.C_ACCENT,
                        padding=6)

        style.configure("TProgressbar",
                        troughcolor="#0e1530",
                        bordercolor=self.C_BORDER,
                        background=self.C_ACCENT2,
                        lightcolor=self.C_ACCENT2,
                        darkcolor=self.C_ACCENT2)

    def _build_ui(self):
        # Fondo
        self.bg = tk.Canvas(self, highlightthickness=0, bd=0)
        self.bg.pack(fill="both", expand=True)

        self.root = ttk.Frame(self.bg, style="TFrame")
        self.root_id = self.bg.create_window(0, 0, anchor="nw", window=self.root)

        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # LEFT (ahora con GRID para garantizar botones visibles)
        self.left = ttk.Frame(self.root, style="Card.TFrame", padding=16)
        self.left.grid(row=0, column=0, sticky="nsw", padx=(16, 10), pady=16)
        self.left.columnconfigure(0, weight=1)
        self.left.rowconfigure(3, weight=1)  # zona flexible (inputs)

        # RIGHT
        self.right = ttk.Frame(self.root, style="Card.TFrame", padding=16)
        self.right.grid(row=0, column=1, sticky="nsew", padx=(10, 16), pady=16)
        self.right.rowconfigure(3, weight=1)
        self.right.columnconfigure(0, weight=1)

        # --- LEFT: Header
        head = ttk.Frame(self.left, style="Card.TFrame")
        head.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(head, text="AURA", style="Header.TLabel").pack(anchor="w")
        ttk.Label(head, text="Predicción de riesgo cardiovascular", style="Muted.TLabel").pack(anchor="w", pady=(2, 10))

        chip = tk.Label(head, text="IA • Random Forest / Neurona",
                        bg="#0e1530", fg=self.C_MUTED, padx=10, pady=6, font=("Segoe UI", 9))
        chip.pack(anchor="w")

        # --- LEFT: Modelo
        model_box = ttk.Labelframe(self.left, text="Modelo", style="Card.TLabelframe", padding=12)
        model_box.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        model_box.columnconfigure(0, weight=1)

        ttk.Radiobutton(model_box, text="Random Forest (joblib)",
                        value="random_forest", variable=self.model_type,
                        command=self._on_model_change).grid(row=0, column=0, sticky="w")

        ttk.Radiobutton(model_box, text="Neurona (Logística con pesos)",
                        value="neurona", variable=self.model_type,
                        command=self._on_model_change).grid(row=1, column=0, sticky="w", pady=(6, 0))

        path_row = ttk.Frame(model_box, style="Card.TFrame")
        path_row.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        path_row.columnconfigure(0, weight=1)

        self.lbl_model_path = ttk.Label(path_row, text=self._short_path(self.model_path), style="Muted.TLabel")
        self.lbl_model_path.grid(row=0, column=0, sticky="w")

        self.btn_pick_model = ttk.Button(path_row, text="Elegir .joblib", style="Ghost.TButton", command=self._pick_model_file)
        self.btn_pick_model.grid(row=0, column=1, sticky="e", padx=(10, 0))

        # --- LEFT: Inputs
        inp = ttk.Labelframe(self.left, text="Datos del paciente", style="Card.TLabelframe", padding=12)
        inp.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        inp.columnconfigure(1, weight=1)

        self._add_labeled_entry(inp, "Edad (años)", self.var_age, 0, "Ej: 60")
        self._add_labeled_entry(inp, "Fracción de eyección (%)", self.var_ef, 1, "Ej: 35")
        self._add_labeled_entry(inp, "Creatinina (mg/dL)", self.var_crea, 2, "Ej: 1.2")
        self._add_labeled_entry(inp, "Sodio (mEq/L)", self.var_sodium, 3, "Ej: 137")

        # --- LEFT: Botones (SIEMPRE abajo)
        btns = ttk.Frame(self.left, style="Card.TFrame")
        btns.grid(row=4, column=0, sticky="ew", pady=(6, 0))

        ttk.Button(btns, text="Calcular riesgo", style="Primary.TButton", command=self._predict).grid(row=0, column=0, sticky="ew")
        ttk.Button(btns, text="Limpiar", style="Ghost.TButton", command=self._clear).grid(row=1, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(btns, text="Guardar reporte (txt)", style="Ghost.TButton", command=self._save_report).grid(row=2, column=0, sticky="ew", pady=(10, 0))
        btns.columnconfigure(0, weight=1)

        # --- RIGHT: Resultado
        ttk.Label(self.right, text="Resultado", style="Title2.TLabel").grid(row=0, column=0, sticky="w")

        res_top = ttk.Frame(self.right, style="Card.TFrame")
        res_top.grid(row=1, column=0, sticky="ew", pady=(10, 12))
        res_top.columnconfigure(0, weight=1)

        self.lbl_risk = tk.Label(res_top, text="— %", bg=self.C_CARD, fg=self.C_TEXT,
                                 font=("Segoe UI Semibold", 34))
        self.lbl_risk.grid(row=0, column=0, sticky="w")

        self.badge = tk.Label(res_top, text="Nivel: —", bg="#0e1530", fg=self.C_MUTED,
                              padx=12, pady=6, font=("Segoe UI Semibold", 10))
        self.badge.grid(row=0, column=1, sticky="e", padx=(10, 0))

        self.pb = ttk.Progressbar(self.right, maximum=100, mode="determinate")
        self.pb.grid(row=2, column=0, sticky="ew")

        # --- RIGHT: Explicación
        explain_card = ttk.Frame(self.right, style="Card2.TFrame", padding=12)
        explain_card.grid(row=3, column=0, sticky="nsew", pady=(14, 0))
        explain_card.rowconfigure(1, weight=1)
        explain_card.columnconfigure(0, weight=1)

        ttk.Label(explain_card, text="Explicación y recomendaciones",
                  style="Title2.TLabel", background=self.C_CARD2).grid(row=0, column=0, sticky="w", pady=(0, 8))

        text_frame = tk.Frame(explain_card, bg=self.C_CARD2)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        self.txt = tk.Text(
            text_frame, wrap="word", font=("Segoe UI", 10),
            bg="#0e1530", fg=self.C_TEXT, insertbackground=self.C_TEXT,
            relief="flat", padx=12, pady=10
        )
        self.txt.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.txt.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.txt.configure(yscrollcommand=yscroll.set)

        self._on_model_change()

    def _redraw_background(self):
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10:
            return

        self.bg.configure(width=w, height=h)
        self.bg.coords(self.root_id, 0, 0)

        self.bg.delete("grad")
        draw_vertical_gradient(self.bg, 0, 0, w, h, "#070a14", "#101a3a", steps=220)

        # glows sutiles
        self.bg.create_oval(-200, 80, 380, 680, fill="#1b2b7a", outline="", tags="grad")
        self.bg.create_oval(w-420, -260, w+260, 320, fill="#2b1f7a", outline="", tags="grad")
        self.bg.itemconfigure("grad", stipple="gray50")

        self.bg.itemconfigure(self.root_id, width=w, height=h)

    def _add_labeled_entry(self, parent, label, var, row, hint=""):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=6)
        ttk.Entry(parent, textvariable=var).grid(row=row, column=1, sticky="ew", pady=6)
        if hint:
            ttk.Label(parent, text=hint, style="Muted.TLabel").grid(row=row, column=2, sticky="w", padx=(10, 0))

    def _short_path(self, p):
        if not p:
            return "—"
        return p if len(p) <= 52 else "…" + p[-51:]

    def _on_model_change(self):
        is_rf = self.model_type.get() == "random_forest"
        self.btn_pick_model.configure(state=("normal" if is_rf else "disabled"))
        self.lbl_model_path.configure(text=self._short_path(self.model_path if is_rf else "No aplica (neurona)"))

    def _pick_model_file(self):
        path = filedialog.askopenfilename(
            title="Seleccionar modelo .joblib",
            filetypes=[("Joblib model", "*.joblib"), ("All files", "*.*")]
        )
        if path:
            self.model_path = path
            self.lbl_model_path.configure(text=self._short_path(self.model_path))

    def _parse_inputs(self):
        try:
            age = float(self.var_age.get().strip())
            ef = float(self.var_ef.get().strip())
            crea = float(self.var_crea.get().strip())
            sodium = float(self.var_sodium.get().strip())
        except ValueError:
            raise ValueError("Campos inválidos: deben ser números (ej: 60, 35, 1.2, 137).")

        if not (0 < age < 120): raise ValueError("Edad fuera de rango (1–119).")
        if not (1 <= ef <= 90): raise ValueError("Fracción de eyección fuera de rango (1–90).")
        if not (0.1 <= crea <= 15): raise ValueError("Creatinina fuera de rango (0.1–15).")
        if not (90 <= sodium <= 200): raise ValueError("Sodio fuera de rango (90–200).")

        return {
            "age": age,
            "ejection_fraction": ef,
            "serum_creatinine": crea,
            "serum_sodium": sodium
        }

    def _set_badge(self, level_text, color_hex):
        self.badge.configure(text=f"Nivel: {level_text}", bg=color_hex, fg="white")

    def _predict(self):
        try:
            paciente = self._parse_inputs()
        except ValueError as e:
            messagebox.showerror("Datos inválidos", str(e))
            return

        try:
            if self.model_type.get() == "random_forest":
                if not os.path.exists(self.model_path):
                    messagebox.showerror("Modelo no encontrado",
                                         "No se encontró el archivo .joblib.\nSelecciona el modelo o colócalo en la misma carpeta.")
                    return
                risk = predecir_riesgo(paciente, self.model_path)
            else:
                risk = predecir_riesgo_neurona(paciente)

            risk_pct = clamp(float(risk) * 100.0, 0.0, 100.0)

        except Exception as e:
            messagebox.showerror("Error al predecir", f"Ocurrió un error:\n{e}")
            return

        self.pb["value"] = risk_pct
        self.lbl_risk.configure(text=f"{risk_pct:.1f}%")

        if risk_pct < 33:
            self._set_badge("Bajo", self.C_OK)
        elif risk_pct < 66:
            self._set_badge("Medio", self.C_WARN)
        else:
            self._set_badge("Alto", self.C_DANGER)

        self.txt.delete("1.0", "end")
        self.txt.insert("end", f"Modelo: {self.model_type.get()}\n")
        if self.model_type.get() == "random_forest":
            self.txt.insert("end", f"Archivo modelo: {self.model_path}\n")
        self.txt.insert("end", "-" * 70 + "\n")

        self.txt.insert("end", "Entrada del paciente:\n")
        self.txt.insert("end", f"  • Edad: {paciente['age']}\n")
        self.txt.insert("end", f"  • Fracción de eyección: {paciente['ejection_fraction']}%\n")
        self.txt.insert("end", f"  • Creatinina sérica: {paciente['serum_creatinine']} mg/dL\n")
        self.txt.insert("end", f"  • Sodio sérico: {paciente['serum_sodium']} mEq/L\n\n")

        self.txt.insert("end", "Explicación y recomendaciones:\n\n")
        recs = explicacion_por_cada_factor(paciente)
        for i, r in enumerate(recs, 1):
            self.txt.insert("end", f"{i}) {r}\n\n")

    def _clear(self):
        self.var_age.set("")
        self.var_ef.set("")
        self.var_crea.set("")
        self.var_sodium.set("")
        self.pb["value"] = 0
        self.lbl_risk.configure(text="— %")
        self.badge.configure(text="Nivel: —", bg="#0e1530", fg=self.C_MUTED)
        self.txt.delete("1.0", "end")

    def _save_report(self):
        content = self.txt.get("1.0", "end").strip()
        if not content:
            messagebox.showinfo("Sin contenido", "Primero calcula un riesgo para generar el reporte.")
            return

        path = filedialog.asksaveasfilename(
            title="Guardar reporte",
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt")]
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{APP_TITLE}\n")
            f.write("=" * 70 + "\n")
            f.write(content + "\n")

        messagebox.showinfo("Guardado", f"Reporte guardado en:\n{path}")


if __name__ == "__main__":
    App().mainloop()
