import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_manager import DataManager
from statistica import run_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("statistica_gui")

class StatisticaWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("STATISTICA Offline Analysis Tool")
        self.geometry("1024x720")
        self.configure(bg="#0f172a")
        
        self.active_file_path = None
        
        self._set_premium_styles()
        self._build_ui_layout()
        
    def _set_premium_styles(self):
        """Set custom color styles matching High Density theme."""
        style = ttk.Style(self)
        style.theme_use('clam')
        
        # Configure frames and labs
        style.configure("TFrame", background="#0f172a")
        style.configure("Sidebar.TFrame", background="#070b14")
        style.configure("Card.TFrame", background="#1e293b", borderwidth=1, relief="flat")
        
        # Labels style
        style.configure("TLabel", background="#0f172a", foreground="#cbd5e1", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#0f172a", foreground="#ffffff", font=("Segoe UI", 16, "bold"))
        style.configure("SidebarHeader.TLabel", background="#070b14", foreground="#ffffff", font=("Segoe UI", 12, "bold"))
        style.configure("Sub.TLabel", background="#0f172a", foreground="#64748b", font=("Segoe UI", 9))
        style.configure("CardTitle.TLabel", background="#1e293b", foreground="#f1f5f9", font=("Segoe UI", 11, "bold"))
        
        # Buttons
        style.configure("Action.TButton", background="#2563eb", foreground="#ffffff", borderwidth=0, font=("Segoe UI", 10, "bold"), padding=8)
        style.map("Action.TButton", background=[("active", "#1d4ed8")])
        
        style.configure("Secondary.TButton", background="#334155", foreground="#f1f5f9", borderwidth=0, font=("Segoe UI", 10), padding=6)
        style.map("Secondary.TButton", background=[("active", "#475569")])
        
        # Progress bar
        style.configure("TProgressbar", thickness=12, troughcolor="#1e293b", background="#2563eb")

    def _build_ui_layout(self):
        """Organize Sidebar + Dashboard columns."""
        # Top-Level Layout split
        self.sidebar_frame = ttk.Frame(self, style="Sidebar.TFrame", width=260)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)
        
        self.main_frame = ttk.Frame(self, style="TFrame")
        self.main_frame.pack(side="right", fill="both", expand=True)
        
        # 1. BUILD SIDEBAR
        # Logo placeholder
        logo_label = ttk.Label(self.sidebar_frame, text="STATISTICA", style="SidebarHeader.TLabel", padding=(20, 30, 20, 10))
        logo_label.configure(background="#070b14")
        logo_label.pack(fill="x")
        
        # Nav item blocks dummy
        nav_info = ttk.Label(self.sidebar_frame, text="ANALYSIS CONTROL", background="#070b14", font=("Segoe UI", 8, "bold"), foreground="#475569", padding=(20, 20, 20, 5))
        nav_info.pack(fill="x")
        
        self.btn_load = ttk.Button(self.sidebar_frame, text="1. Load Dataset File", style="Action.TButton", command=self._browse_dataset)
        self.btn_load.pack(fill="x", padx=20, pady=10)
        
        # Dynamic check boxes for routine overrides
        self.var_stats = tk.BooleanVar(value=True)
        self.var_psych = tk.BooleanVar(value=True)
        self.var_finance = tk.BooleanVar(value=True)
        
        check_stats = tk.Checkbutton(self.sidebar_frame, text="Descriptive & Regression", variable=self.var_stats, bg="#070b14", fg="#cbd5e1", selectcolor="#070b14", activebackground="#070b14", activeforeground="#ffffff", font=("Segoe UI", 10), anchor="w")
        check_stats.pack(fill="x", padx=25, pady=4)
        
        check_psych = tk.Checkbutton(self.sidebar_frame, text="Psychometrics Module", variable=self.var_psych, bg="#070b14", fg="#cbd5e1", selectcolor="#070b14", activebackground="#070b14", activeforeground="#ffffff", font=("Segoe UI", 10), anchor="w")
        check_psych.pack(fill="x", padx=25, pady=4)

        check_fin = tk.Checkbutton(self.sidebar_frame, text="Advanced Financial Asset", variable=self.var_finance, bg="#070b14", fg="#cbd5e1", selectcolor="#070b14", activebackground="#070b14", activeforeground="#ffffff", font=("Segoe UI", 10), anchor="w")
        check_fin.pack(fill="x", padx=25, pady=4)

        # Trigger button
        self.btn_start = ttk.Button(self.sidebar_frame, text="Generate Reports", style="Action.TButton", command=self._run_dispatch)
        self.btn_start.pack(fill="x", padx=20, pady=30)
        self.btn_start.config(state="disabled")

        # 2. BUILD MAIN DASHBOARD CONTAINER
        header_frame = ttk.Frame(self.main_frame, style="TFrame", padding=(30, 25, 30, 10))
        header_frame.pack(fill="x")
        
        title_lbl = ttk.Label(header_frame, text="STATISTICA Offline Dashboard", style="Header.TLabel")
        title_lbl.pack(side="left")
        
        self.status_badge = ttk.Label(header_frame, text="DISCONNECTED", font=("Segoe UI", 9, "bold"), foreground="#ef4444", background="#ef4444/10", borderwidth=1, relief="solid", padding=(6, 2))
        self.status_badge.pack(side="right")
        
        # Body panels grid
        body_container = ttk.Frame(self.main_frame, style="TFrame", padding=30)
        body_container.pack(fill="both", expand=True)
        
        # Left Panel: File detail card
        self.card_meta = ttk.Frame(body_container, style="Card.TFrame", padding=20)
        self.card_meta.place(relx=0, rely=0, relwidth=0.48, relheight=0.45)
        
        meta_title = ttk.Label(self.card_meta, text="Dataset Metadata Scanning", style="CardTitle.TLabel")
        meta_title.pack(anchor="w", mb=10)
        
        self.meta_txt = tk.Text(self.card_meta, bg="#1e293b", fg="#94a3b8", font=("Consolas", 10), wrap="word", relief="flat", bd=0)
        self.meta_txt.pack(fill="both", expand=True, pt=10)
        self.meta_txt.insert("1.0", "Drag or import an Excel/CSV spreadsheet to begin analyzing statistical features automatically...")
        self.meta_txt.config(state="disabled")
        
        # Right Panel: Workflow recommendation
        self.card_recs = ttk.Frame(body_container, style="Card.TFrame", padding=20)
        self.card_recs.place(relx=0.52, rely=0, relwidth=0.48, relheight=0.45)
        
        recs_title = ttk.Label(self.card_recs, text="AI Recommendations Engine", style="CardTitle.TLabel")
        recs_title.pack(anchor="w")
        
        self.recs_txt = tk.Text(self.card_recs, bg="#1e293b", fg="#60a5fa", font=("Segoe UI italic", 10), wrap="word", relief="flat", bd=0)
        self.recs_txt.pack(fill="both", expand=True, pt=10)
        self.recs_txt.insert("1.0", "Our framework automatically identifies numeric scales, time axes, classification labels, and advises relevant academic routines...")
        self.recs_txt.config(state="disabled")
        
        # Bottom Console panel
        self.card_console = ttk.Frame(body_container, style="Card.TFrame", padding=20)
        self.card_console.place(relx=0, rely=0.5, relwidth=1.0, relheight=0.48)
        
        console_title = ttk.Label(self.card_console, text="Engine Process Stream & Diagnostics", style="CardTitle.TLabel")
        console_title.pack(anchor="w")
        
        self.progress = ttk.Progressbar(self.card_console, mode="determinate")
        self.progress.pack(fill="x", pady=10)
        
        self.console_txt = tk.Text(self.card_console, bg="#070b14", fg="#34d399", font=("Consolas", 9), wrap="word", bd=0)
        self.console_txt.pack(fill="both", expand=True)
        self.console_txt.insert("1.0", "[SYS]: Main thread initialized. Waiting for offline dataset compilation...\n")
        self.console_txt.config(state="disabled")
        
    def _browse_dataset(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Spreadsheets", "*.xlsx *.xls *.csv"), ("Excel Binary", "*.xlsx"), ("CSV files", "*.csv")]
        )
        if file_path:
            self._process_selected_file(file_path)
            
    def _process_selected_file(self, file_path):
        self.active_file_path = file_path
        self.status_badge.config(text="METRICS CONNECTED", foreground="#10b981")
        self.btn_start.config(state="normal")
        
        # Scrape and fill diagnostics
        try:
            dm = DataManager(file_path)
            dm.load_data()
            summary = dm.get_summary_stats()
            
            # Format text
            self.meta_txt.config(state="normal")
            self.meta_txt.delete("1.0", "end")
            self.meta_txt.insert("end", f"File Name: {summary['fileName']}\n")
            self.meta_txt.insert("end", f"Total Records: {summary['rows']} rows\n")
            self.meta_txt.insert("end", f"Parameters: {summary['columns']} columns\n")
            self.meta_txt.insert("end", f"Duplicate Rows: {summary['duplicates']}\n\n")
            self.meta_txt.insert("end", "Columns details:\n")
            for col, d in summary["columnsDetails"].items():
                self.meta_txt.insert("end", f" - {col}: {d['type']} ({d['unique_count']} uniques)\n")
            self.meta_txt.config(state="disabled")
            
            # Recommendations write
            self.recs_txt.config(state="normal")
            self.recs_txt.delete("1.0", "end")
            for rec in summary["recommendations"]:
                self.recs_txt.insert("end", f"✓ {rec}\n\n")
            self.recs_txt.config(state="disabled")
            
            self._log_console(f"[SYS]: Scanned metadata files successfully for: {summary['fileName']}")
        except Exception as e:
            messagebox.showerror("Error Reading Metadata", str(e))
            
    def _log_console(self, text):
        self.console_txt.config(state="normal")
        self.console_txt.insert("end", f"{text}\n")
        self.console_txt.see("end")
        self.console_txt.config(state="disabled")

    def _run_dispatch(self):
        if not self.active_file_path:
            return
            
        self.progress.start(10)
        self.btn_start.config(state="disabled")
        self._log_console("[SYS]: Starting background math computations thread...")
        
        # Run pipeline in a background thread to prevent Tkinter window from freezing
        t = threading.Thread(target=self._exec_computation)
        t.daemon = True
        t.start()
        
    def _exec_computation(self):
        try:
            base_name = os.path.splitext(os.path.basename(self.active_file_path))[0]
            output_dir = os.path.abspath(f"./output/{base_name}")
            
            run_pipeline(self.active_file_path, output_dir)
            
            self.after(0, lambda: self._process_success(output_dir))
        except Exception as e:
            self.after(0, lambda: self._process_failed(str(e)))
            
    def _process_success(self, output_dir):
        self.progress.stop()
        self.btn_start.config(state="normal")
        self._log_console(f"[READY]: Generated visual items inside: {output_dir}")
        self._log_console("✓ High resolution Word Dossier & HTML Dashboard created successfully!")
        
        # open target explorer option
        ans = messagebox.askyesno("Pipeline Complete", "Full diagnostic dispatch has run successfully offline!\n\nWould you like to reveal the output compilation folder on disk?")
        if ans:
            import subprocess
            if sys.platform == "win32":
                os.startfile(output_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", output_dir])
            else:
                subprocess.Popen(["xdg-open", output_dir])
                
    def _process_failed(self, err_msg):
        self.progress.stop()
        self.btn_start.config(state="normal")
        self._log_console(f"[FATAL]: Pipeline exited with error: {err_msg}")
        messagebox.showerror("Analytical Failure", f"Computation thread crashed:\n{err_msg}")

if __name__ == "__main__":
    app = StatisticaWindow()
    app.mainloop()
