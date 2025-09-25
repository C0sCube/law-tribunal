import tkinter as tk
import threading

class AppUI:
    def __init__(self, root, run_callback):
        self.root = root
        root.title("Tribunal Scraper")
        root.configure(bg="#1e1e1e")  # dark mode

        # === Status log box ===
        self.log_box = tk.Text(
            root,
            height=20, width=80,
            state="disabled",
            bg="#252526", fg="#d4d4d4", insertbackground="white"
        )
        self.log_box.pack(padx=10, pady=10, fill="both", expand=True)

        # === Captcha frame ===
        captcha_frame = tk.Frame(root, bg="#1e1e1e")
        captcha_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(captcha_frame, text="CAPTCHA:", fg="white", bg="#1e1e1e").grid(row=0, column=0, sticky="w")
        self.captcha_var = tk.StringVar()
        self.captcha_entry = tk.Entry(
            captcha_frame, textvariable=self.captcha_var,
            font=("Consolas", 14), width=20,
            bg="#333333", fg="white", insertbackground="white"
        )
        self.captcha_entry.grid(row=0, column=1, padx=5)

        self.go_btn = tk.Button(
            captcha_frame, text="Go", command=self.confirm_captcha,
            bg="#007acc", fg="white", activebackground="#005a9e", activeforeground="white"
        )
        self.go_btn.grid(row=0, column=2, padx=5)

        # === Control buttons ===
        controls = tk.Frame(root, bg="#1e1e1e")
        controls.pack(padx=10, pady=10, fill="x")

        self.start_btn = tk.Button(
            controls, text="Start", command=self.start_scraper,
            bg="#a9cde6", fg="white", activebackground="#9fc6e4",
            activeforeground="white", width=12
        )
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = tk.Button(
            controls, text="End Program", command=self.stop_scraper,
            bg="#df655a", fg="white", activebackground="#f05757",
            activeforeground="white", width=12
        )
        self.stop_btn.pack(side="right", padx=5)

        # === New: Next Combo Button ===
        self.next_event = threading.Event()
        self.next_btn = tk.Button(
            controls, text="Next Combo", command=self.next_combo,
            bg="#5cb85c", fg="white", activebackground="#449d44",
            activeforeground="white", width=12
        )
        self.next_btn.pack(side="left", padx=5)

        # State
        self.running = False
        self.scraper_thread = None
        self.captcha_event = threading.Event()
        self.captcha_value = None
        self.run_callback = run_callback
        
        bench_frame = tk.Frame(root, bg="#1e1e1e")
        bench_frame.pack(padx=10, pady=5, fill="x")

        tk.Label(bench_frame, text="Bench:", fg="white", bg="#1e1e1e").pack(side="left")
        self.bench_var = tk.StringVar()
        self.bench_select = ttk.Combobox(
            bench_frame, textvariable=self.bench_var,
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
            width=30
        )
        self.bench_select.pack(side="left", padx=5)

    # === Logging ===
    def log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")

    # === Start / Stop ===
    def start_scraper(self):
        if not self.running:
            self.running = True
            self.log("Starting scraper...")
            self.scraper_thread = threading.Thread(target=self.run_callback, args=(self,))
            self.scraper_thread.start()

    def stop_scraper(self):
        self.log("Stopping program...")
        self.running = False
        self.root.quit()

    # === Captcha ===
    def show_captcha_guess(self, guess):
        self.captcha_var.set(guess)
        self.log(f"Detected CAPTCHA: {guess}")

    def confirm_captcha(self):
        self.captcha_value = self.captcha_var.get().strip()
        self.log(f"Using CAPTCHA: {self.captcha_value}")
        self.captcha_event.set()

    # === New: Manual stepping ===
    def next_combo(self):
        """Triggered by Next Combo button"""
        self.log("➡️ Proceeding to next combo...")
        self.next_event.set()

    def wait_for_next(self):
        """Block scraper until user presses Next Combo"""
        self.log("⏸ Waiting for user to press Next Combo...")
        self.next_event.clear()
        self.next_event.wait()
