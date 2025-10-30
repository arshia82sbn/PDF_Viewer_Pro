import os
import threading
from tkinter import filedialog
from PIL import ImageTk, Image
from customtkinter import *
import webbrowser

from app.utils.config import Config
from app.utils.LogManager import get_logger
from app.utils.file_helper import FileHelper
from app.core.summarizer import SummarizerFactory, Summarizer


class PDFViewerPro(CTk):
    """Main Application for PDF Viewer & Summarizer."""

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.logger = get_logger()
        self.helper = FileHelper()
        self.geometry(self.config.SIZE)
        self.title(self.config.TITLE)
        self._set_window_icon(self.config.LOGO_PATH)
        self._set_appearance_mode("dark")

        # UI setup
        self.configure_layout()
        self.create_widgets()

        # Summarizer initialization (fast + async)
        strategy = SummarizerFactory.create("huggingface", "t5-small")  # Faster than Falconsai
        self.summarizer = Summarizer(strategy)
        self.summarizer.load_model_async(
            lambda ok: self.update_status("Model Ready ✅" if ok else "Model Load Failed ❌")
        )

        self.update_status("Loading summarization model...", "blue")

        # State
        self.current_document = None
        self.is_processing = False
        self.lock = threading.Lock()

    # -------------------------------
    # 🧩 UI Setup
    # -------------------------------
    def _set_window_icon(self, path):
        try:
            logo_icon = ImageTk.PhotoImage(Image.open(path))
            self.iconphoto(False, logo_icon)
            self.after(250, lambda: self.iconphoto(False, logo_icon))
            self.logger.info("Window icon set.")
        except Exception as e:
            self.logger.warning(f"Icon setup failed: {e}")

    def configure_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def create_widgets(self):
        # Header
        self.header_frame = CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ew")

        # Buttons
        self.open_btn = CTkButton(self.header_frame, text="📄 Open PDF", command=self.open_pdf)
        self.open_btn.pack(side="left", padx=10)

        self.close_btn = CTkButton(
            self.header_frame, text="❌ Close PDF", command=self.close_pdf, state="disabled"
        )
        self.close_btn.pack(side="left", padx=10)

        self.summarize_btn = CTkButton(
            self.header_frame, text="🧠 Summarize", command=self.summarize_pdf_text
        )
        self.summarize_btn.pack(side="left", padx=10)

        # File label
        self.file_label = CTkLabel(self.header_frame, text="No file selected", width=300)
        self.file_label.pack(side="left", padx=10)

        # Progress bar
        self.progress_bar = CTkProgressBar(
            self.header_frame, width=350, height=8, progress_color="green"
        )
        self.progress_bar.pack(side="left", padx=10)
        self.progress_bar.set(0)

        # Text area
        self.text_area = CTkTextbox(self, wrap="word", font=("Consolas", 12))
        self.text_area.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")

        # Status bar
        self.status_bar = CTkLabel(
            self, text="Ready", anchor="w", height=25, fg_color=("#E0E0E0", "#2D2D2D")
        )
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=15, pady=5)

        self.coder_name = CTkLabel(self,
                                   text="Develpoer:Arshia Saberian\tEmail:arshia82sbn@gmail.com",
                                   font=("Consolas", 12),
                                   corner_radius=20)
        self.coder_name.grid(row=3, column=0, sticky="w", padx=5, pady=5)

        self.coder_github = CTkLabel(self,
                                     text="Github:https://github.com/arshia82sbn",
                                     text_color="blue",
                                     font=("Consolas", 12,"underline"),
                                     corner_radius=20)
        self.coder_github.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        # Make GitHub clickable
        def open_github(event):
            webbrowser.open("https://github.com/arshia82sbn")

        # Bind click events
        self.coder_github.bind("<Button-1>", lambda e: open_github(e))
    # -------------------------------
    # 🧠 Core Functionality
    # -------------------------------
    def open_pdf(self):
        if self.is_processing:
            return

        file_path = filedialog.askopenfilename(
            title="Select PDF File", filetypes=[("PDF Files", "*.pdf")]
        )
        if not file_path:
            return

        if not os.path.exists(file_path):
            self.update_status("File does not exist ❌", "red")
            return

        with self.lock:
            self.is_processing = True
            self.current_document = None
            self.file_label.configure(text=os.path.basename(file_path))
            self.text_area.delete("1.0", "end")
            self.progress_bar.set(0)
            self.update_status("Loading PDF...", "blue")
            self.close_btn.configure(state="normal")

        threading.Thread(target=self._load_pdf, args=(file_path,), daemon=True).start()

    def _load_pdf(self, file_path):
        text = self.helper.read_pdf(file_path)
        if text:
            self.after(0, lambda: self.text_area.insert("1.0", text))
            self.current_document = file_path
        with self.lock:
            self.is_processing = False
        self.update_status("PDF Loaded ✅", "green")

    def summarize_pdf_text(self):
        """Triggered when the Summarize button is clicked."""
        text = self.text_area.get("1.0", "end").strip()
        if not text:
            self.update_status("No text to summarize ❌", "red")
            return

        if not self.summarizer.strategy.is_loaded:
            self.update_status("Model still loading ⏳", "orange")
            return

        self.update_status("Summarizing...", "blue")

        def run_summary():
            try:
                summary = self.summarizer.summarize(text)
                self.after(0, lambda: self.text_area.delete("1.0", "end"))
                self.after(0, lambda: self.text_area.insert("1.0", summary))
                self.update_status("Summarization completed ✅", "green")
            except Exception as e:
                self.logger.error(f"Summarization failed: {e}")
                self.update_status("Summarization failed ❌", "red")

        threading.Thread(target=run_summary, daemon=True).start()

    # -------------------------------
    # 🧩 Helpers
    # -------------------------------
    def update_status(self, message, color="black"):
        self.after(0, lambda: self.status_bar.configure(text=message, text_color=color))

    def close_pdf(self):
        with self.lock:
            self.is_processing = False
            self.current_document = None
            self.file_label.configure(text="No file selected")
            self.text_area.delete("1.0", "end")
            self.progress_bar.set(0)
        self.update_status("PDF closed ✅", "gray")
