import tkinter as tk
from tkinter import ttk
import threading
from app.constant import DEFAULT_TODAY_DATE

class AppUI:
    def __init__(self, root, run_callback):
        self.root = root
        self.run_callback = run_callback
        root.title("Tribunal Scraper")
        root.configure(bg="#1e1e1e")

        # === Log box (right) ===
        self.log_box = tk.Text(
            root, height=25, width=80, state="disabled",
            bg="#252526", fg="#d4d4d4", insertbackground="white"
        )
        self.log_box.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # === Left controls ===
        control_panel = tk.Frame(root, bg="#1e1e1e")
        control_panel.pack(side="left", fill="y", padx=10, pady=10)

        # Date (auto-filled, read-only)
        tk.Label(control_panel, text="Date:", fg="white", bg="#1e1e1e").pack(anchor="w")
        self.date_var = tk.StringVar(value=DEFAULT_TODAY_DATE)
        self.date_entry = tk.Entry(
            control_panel, textvariable=self.date_var, state="readonly",
            width=15, bg="#333333", fg="white"
        )
        self.date_entry.pack(anchor="w", pady=5)

        # Captcha
        tk.Label(control_panel, text="CAPTCHA:", fg="white", bg="#1e1e1e").pack(anchor="w")
        captcha_frame = tk.Frame(control_panel, bg="#1e1e1e")
        captcha_frame.pack(anchor="w", pady=5)
        self.captcha_var = tk.StringVar()
        self.captcha_entry = tk.Entry(
            captcha_frame, textvariable=self.captcha_var,
            font=("Consolas", 14), width=15,
            bg="#333333", fg="white", insertbackground="white"
        )
        self.captcha_entry.pack(side="left", padx=2)
        self.go_btn = tk.Button(
            captcha_frame, text="Confirm", command=self.confirm_captcha,
            bg="#007acc", fg="white", width=10
        )
        self.go_btn.pack(side="left", padx=2)

        # Spacer
        tk.Label(control_panel, text="", bg="#1e1e1e").pack(pady=10)

        # City dropdown above buttons
        tk.Label(control_panel, text="Bench:", fg="white", bg="#1e1e1e").pack(anchor="w")
        self.bench_var = tk.StringVar()
        self.bench_select = ttk.Combobox(
            control_panel, textvariable=self.bench_var,
            values=[
                "203 - Agra", "205 - Ahmedabad", "207 - Allahabad", "209 - Amritsar",
                "211 - Bangalore", "215 - Chandigarh", "217 - Chennai", "219 - Cochin",
                "221 - Cuttack", "260 - Dehradun", "201 - Delhi", "223 - Guwahati",
                "225 - Hyderabad", "227 - Indore", "229 - Jabalpur", "231 - Jaipur",
                "233 - Jodhpur", "235 - Kolkata", "237 - Lucknow", "199 - Mumbai",
                "239 - Nagpur", "241 - Panaji", "243 - Patna", "245 - Pune",
                "247 - Raipur", "249 - Rajkot", "251 - Ranchi", "256 - Surat",
                "258 - Varanasi", "253 - Visakhapatnam"
            ],
            width=28, state="readonly"
        )
        self.bench_select.pack(anchor="w", pady=5)

        # Buttons row
        button_row = tk.Frame(control_panel, bg="#1e1e1e")
        button_row.pack(side="bottom", pady=10, fill="x")

        self.start_btn = tk.Button(
            button_row, text="Start", command=self.start_scraper,
            bg="#a9cde6", fg="white", width=12
        )
        self.start_btn.pack(side="left", padx=5)

        self.next_btn = tk.Button(
            button_row, text="Next Combo", command=self.next_combo,
            bg="#5cb85c", fg="white", width=12
        )
        self.next_btn.pack(side="left", padx=5)

        self.stop_btn = tk.Button(
            button_row, text="End Program", command=self.stop_scraper,
            bg="#df655a", fg="white", width=12
        )
        self.stop_btn.pack(side="right", padx=5)

        # === State ===
        self.running = False
        self.scraper_thread = None
        self.captcha_event = threading.Event()
        self.captcha_value = None
        self.next_event = threading.Event()

    # === Helpers ===
    def log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")

    def start_scraper(self):
        if not self.running:
            self.running = True
            self.log("Starting scraper...")
            self.scraper_thread = threading.Thread(target=self.run_callback, args=(self,))
            self.scraper_thread.start()

    def stop_scraper(self):
        self.running = False
        self.log("Stopping program...")
        self.root.quit()

    def show_captcha_guess(self, guess):
        self.captcha_var.set(guess)
        self.log(f"Detected CAPTCHA: {guess}")

    def confirm_captcha(self):
        self.captcha_value = self.captcha_var.get().strip()
        self.log(f"Using CAPTCHA: {self.captcha_value}")
        self.captcha_event.set()

    def next_combo(self):
        # Prevent Next if no city selected
        if not self.bench_var.get():
            self.log("⚠️ Please select a city before proceeding.")
            return
        self.log("➡️ Proceeding to next combo...")
        self.next_event.set()

    def wait_for_next(self):
        self.log("⏸ Waiting for user to press Next Combo...")
        self.next_event.clear()
        self.next_event.wait()
