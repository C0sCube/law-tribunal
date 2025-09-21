import tkinter as tk
from tkinter import ttk
import threading
from app.constant import DEFAULT_TODAY_DATE

APPEALS = [
    ("ITA", "Income Tax Appeal"),
    ("CO", "Cross Objection"),
    ("ITSSA", "Search & Seizure Appeal"),
    ("ITTPA", "Transfer Pricing Appeal"),
    ("ITITA", "International Taxation Appeal"),
    ("WTA", "Wealth Tax Appeal"),
    ("BMA", "Black Money Appeal"),
    ("EDA", "Estate Duty Appeal"),
    ("INTTA", "Interest Tax Appeal"),
    ("GTA", "Gift Tax Appeal"),
    ("TDS", "TDS Appeal"),
    ("STTA", "Security Transaction Tax Appeal"),
    ("ETA", "Expenditure Tax Appeal"),
    ("STA", "Sur Tax Appeal"),
    ("HCD", "High Court Decision"),
    ("SA", "Stay Application"),
    ("MA", "Miscellaneous Application"),
    ("RA", "Reference Application"),
]

class AppUI:
    def __init__(self, root, run_callback):
        self.root = root
        self.run_callback = run_callback
        root.title("Tribunal Scraper")
        root.configure(bg="#1e1e1e")

        # === Main frame: split left/right ===
        main_frame = tk.Frame(root, bg="#1e1e1e")
        main_frame.pack(fill="both", expand=True)

        # Left panel (narrow)
        left_panel = tk.Frame(main_frame, bg="#1e1e1e", width=300)
        left_panel.pack(side="left", fill="y", padx=10, pady=10)
        left_panel.pack_propagate(False)  # keep fixed width

        # Right panel (log box)
        right_panel = tk.Frame(main_frame, bg="#1e1e1e")
        right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # === Date ===
        tk.Label(left_panel, text="Date:", fg="white", bg="#1e1e1e").pack(anchor="w")
        self.date_var = tk.StringVar(value=DEFAULT_TODAY_DATE)
        self.date_entry = tk.Entry(left_panel, textvariable=self.date_var,
                                   width=20, bg="#333333", fg="white", insertbackground="white")
        self.date_entry.pack(anchor="w", pady=5)

        # === Bench dropdown ===
        tk.Label(left_panel, text="Bench:", fg="white", bg="#1e1e1e").pack(anchor="w")
        self.bench_var = tk.StringVar()
        self.bench_select = ttk.Combobox(
            left_panel, textvariable=self.bench_var,
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
            width=28
        )
        self.bench_select.pack(anchor="w", pady=5)

        # === Captcha ===
        tk.Label(left_panel, text="CAPTCHA:", fg="white", bg="#1e1e1e").pack(anchor="w")
        captcha_frame = tk.Frame(left_panel, bg="#1e1e1e")
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

        # === Appeals (vertical radio buttons) ===
        tk.Label(left_panel, text="Appeals:", fg="white", bg="#1e1e1e").pack(anchor="w", pady=(10, 0))
        self.appeal_var = tk.StringVar(value=APPEALS[0][0])  # default = ITA
        for code, name in APPEALS:
            tk.Radiobutton(
                left_panel, text=name, variable=self.appeal_var, value=code,
                fg="white", bg="#1e1e1e", selectcolor="#333333",
                anchor="w", justify="left"
            ).pack(anchor="w")

        # === Go button ===
        self.scrape_btn = tk.Button(left_panel, text="Go", command=self.start_scraper,
                                    bg="#5cb85c", fg="white", width=20)
        self.scrape_btn.pack(pady=10)

        # === Start / End buttons pinned bottom ===
        bottom_frame = tk.Frame(left_panel, bg="#1e1e1e")
        bottom_frame.pack(side="bottom", fill="x", pady=10)
        self.start_btn = tk.Button(bottom_frame, text="Start", command=self.start_scraper,
                                   bg="#a9cde6", fg="white", width=12)
        self.start_btn.pack(side="left", padx=5)
        self.stop_btn = tk.Button(bottom_frame, text="End Program", command=self.stop_scraper,
                                  bg="#df655a", fg="white", width=12)
        self.stop_btn.pack(side="right", padx=5)

        # === Log box fills right panel ===
        self.log_box = tk.Text(
            right_panel, state="disabled",
            bg="#252526", fg="#d4d4d4", insertbackground="white"
        )
        self.log_box.pack(fill="both", expand=True)

        # === State ===
        self.running = False
        self.scraper_thread = None
        self.captcha_event = threading.Event()
        self.captcha_value = None
        self.next_event = threading.Event()

    # === Logging ===
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
        self.log("➡️ Proceeding to next combo...")
        self.next_event.set()

    def wait_for_next(self):
        self.log("⏸ Waiting for user to press Next Combo...")
        self.next_event.clear()
        self.next_event.wait()


# import tkinter as tk
# from tkinter import ttk   # <-- added for Combobox
# import threading
# from app.constant import DEFAULT_TODAY_DATE

# class AppUI:
#     def __init__(self, root, run_callback):
#         self.root = root
#         root.title("Tribunal Scraper")
#         root.configure(bg="#1e1e1e")  # dark mode

#         # === Status log box ===
#         self.log_box = tk.Text(
#             root,
#             height=20, width=80,
#             state="disabled",
#             bg="#252526", fg="#d4d4d4", insertbackground="white"
#         )
#         self.log_box.pack(padx=10, pady=10, fill="both", expand=True)

#         # === Bench & Date frame (NEW) ===
#         bench_frame = tk.Frame(root, bg="#1e1e1e")
#         bench_frame.pack(padx=10, pady=10, fill="x")

#         tk.Label(bench_frame, text="Bench:", fg="white", bg="#1e1e1e").grid(row=0, column=0, sticky="w")
#         self.bench_var = tk.StringVar()
#         self.bench_select = ttk.Combobox(
#             bench_frame, textvariable=self.bench_var,
#             values=[
#                 "203 - Agra", "205 - Ahmedabad", "207 - Allahabad", "209 - Amritsar",
#                 "211 - Bangalore", "215 - Chandigarh", "217 - Chennai", "219 - Cochin",
#                 "221 - Cuttack", "260 - Dehradun", "201 - Delhi", "223 - Guwahati",
#                 "225 - Hyderabad", "227 - Indore", "229 - Jabalpur", "231 - Jaipur",
#                 "233 - Jodhpur", "235 - Kolkata", "237 - Lucknow", "199 - Mumbai",
#                 "239 - Nagpur", "241 - Panaji", "243 - Patna", "245 - Pune",
#                 "247 - Raipur", "249 - Rajkot", "251 - Ranchi", "256 - Surat",
#                 "258 - Varanasi", "253 - Visakhapatnam"
#             ],
#             width=30
#         )
#         self.bench_select.grid(row=0, column=1, padx=5)

#         tk.Label(bench_frame, text="Date:", fg="white", bg="#1e1e1e").grid(row=0, column=2, sticky="w")
#         self.date_var = tk.StringVar(value=DEFAULT_TODAY_DATE)
#         self.date_entry = tk.Entry(
#             bench_frame, textvariable=self.date_var,
#             width=12, bg="#333333", fg="white", insertbackground="white"
#         )
#         self.date_entry.grid(row=0, column=3, padx=5)

#         # === Captcha frame ===
#         captcha_frame = tk.Frame(root, bg="#1e1e1e")
#         captcha_frame.pack(padx=10, pady=10, fill="x")

#         tk.Label(captcha_frame, text="CAPTCHA:", fg="white", bg="#1e1e1e").grid(row=0, column=0, sticky="w")
#         self.captcha_var = tk.StringVar()
#         self.captcha_entry = tk.Entry(
#             captcha_frame, textvariable=self.captcha_var,
#             font=("Consolas", 14), width=20,
#             bg="#333333", fg="white", insertbackground="white"
#         )
#         self.captcha_entry.grid(row=0, column=1, padx=5)

#         self.go_btn = tk.Button(
#             captcha_frame, text="Go", command=self.confirm_captcha,
#             bg="#007acc", fg="white", activebackground="#005a9e", activeforeground="white"
#         )
#         self.go_btn.grid(row=0, column=2, padx=5)

#         # === Control buttons ===
#         controls = tk.Frame(root, bg="#1e1e1e")
#         controls.pack(padx=10, pady=10, fill="x")

#         self.start_btn = tk.Button(
#             controls, text="Start", command=self.start_scraper,
#             bg="#a9cde6", fg="white", activebackground="#9fc6e4",
#             activeforeground="white", width=12
#         )
#         self.start_btn.pack(side="left", padx=5)

#         self.stop_btn = tk.Button(
#             controls, text="End Program", command=self.stop_scraper,
#             bg="#df655a", fg="white", activebackground="#f05757",
#             activeforeground="white", width=12
#         )
#         self.stop_btn.pack(side="right", padx=5)

#         # === Next Combo Button ===
#         self.next_event = threading.Event()
#         self.next_btn = tk.Button(
#             controls, text="Next Combo", command=self.next_combo,
#             bg="#5cb85c", fg="white", activebackground="#449d44",
#             activeforeground="white", width=12
#         )
#         self.next_btn.pack(side="left", padx=5)

#         # State
#         self.running = False
#         self.scraper_thread = None
#         self.captcha_event = threading.Event()
#         self.captcha_value = None
#         self.run_callback = run_callback

#     # === Logging ===
#     def log(self, message):
#         self.log_box.config(state="normal")
#         self.log_box.insert(tk.END, message + "\n")
#         self.log_box.see(tk.END)
#         self.log_box.config(state="disabled")

#     # === Start / Stop ===
#     def start_scraper(self):
#         if not self.running:
#             self.running = True
#             self.log("Starting scraper...")
#             self.scraper_thread = threading.Thread(target=self.run_callback, args=(self,))
#             self.scraper_thread.start()

#     def stop_scraper(self):
#         self.log("Stopping program...")
#         self.running = False
#         self.root.quit()

#     # === Captcha ===
#     def show_captcha_guess(self, guess):
#         self.captcha_var.set(guess)
#         self.log(f"Detected CAPTCHA: {guess}")

#     def confirm_captcha(self):
#         self.captcha_value = self.captcha_var.get().strip()
#         self.log(f"Using CAPTCHA: {self.captcha_value}")
#         self.captcha_event.set()

#     # === Manual stepping ===
#     def next_combo(self):
#         self.log("➡️ Proceeding to next combo...")
#         self.next_event.set()

#     def wait_for_next(self):
#         self.log("⏸ Waiting for user to press Next Combo...")
#         self.next_event.clear()
#         self.next_event.wait()
