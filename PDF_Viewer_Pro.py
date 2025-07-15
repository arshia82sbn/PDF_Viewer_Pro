from customtkinter import *
import fitz  # PyMuPDF
import threading
from PIL import Image, ImageTk
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import defaultdict
from threading import Lock

nltk.download('punkt')
nltk.download('stopwords')

class PDFViewerApp(CTk):
    def __init__(self):
        super().__init__()
        self.title("PDF Viewer Pro")
        self.geometry("1200x750")
        self.configure_layout()
        self.create_widgets()
        self.current_document = None
        self.is_processing = False
        self.lock = Lock()  # Lock for thread safety
        # Logo icon
        logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
        logo_icon = ImageTk.PhotoImage(Image.open(logo_path))
        self.iconphoto(False, logo_icon)
        self.after(250, lambda: self.iconphoto(False, logo_icon))

    def configure_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def create_widgets(self):
        # Header Section
        self.header_frame = CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        
        # Open Button
        self.open_btn = CTkButton(
            self.header_frame,
            text="📄 Open PDF",
            command=self.open_pdf,
            width=150,
            height=45,
            corner_radius=10,
            font=("Arial", 14))
        self.open_btn.pack(side="left", padx=10)

        # Close Button
        self.close_btn = CTkButton(
            self.header_frame,
            text="❌ Close PDF",
            command=self.close_pdf,
            width=150,
            height=45,
            corner_radius=10,
            font=("Arial", 14),
            state="disabled")
        self.close_btn.pack(side="left", padx=10)
        
        self.summarize_btn = CTkButton(
            self.header_frame,
            text="🧠 Summarize",
            command=self.summarize_pdf_text,
            width=150,
            height=40,
            corner_radius=8,
            font=("Arial", 14),
        )
        self.summarize_btn.pack(side="left", padx=10)
        
        self.file_label = CTkLabel(
            self.header_frame,
            text="No file selected",
            anchor="w",
            width=300,
            font=("Arial", 12))
        self.file_label.pack(side="left", padx=10)

        self.progress_bar = CTkProgressBar(
            self.header_frame,
            width=350,
            height=8,
            progress_color="green")
        self.progress_bar.pack(side="left", padx=10)
        self.progress_bar.set(0)

        # Text Display
        self.text_area = CTkTextbox(
            self,
            wrap="word",
            font=("Consolas", 12),
            activate_scrollbars=True)
        self.text_area.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")

        # Status Bar
        self.status_bar = CTkLabel(
            self,
            text="Ready",
            anchor="w",
            height=25,
            fg_color=("#E0E0E0", "#2D2D2D"),
            font=("Arial", 10))
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=15, pady=5)

    def open_pdf(self):
        if self.is_processing:
            return

        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf")])
        
        if file_path:
            with self.lock:
                self.is_processing = True
                self.current_document = None
                self.file_label.configure(text=os.path.basename(file_path))
                self.text_area.delete("1.0", "end")
                self.progress_bar.set(0)
                self.update_status("Loading PDF...", "blue")
                self.close_btn.configure(state="normal")
            
            threading.Thread(
                target=self.process_pdf,
                args=(file_path,),
                daemon=True).start()

    def summarize_pdf_text(self):
        if self.is_processing:
            self.update_status("Please wait for the current PDF to finish processing.", "#FFA000")
            return
        full_text = self.text_area.get("1.0", "end").strip()
        if not full_text:
            self.update_status("No text available to summarize.", "#F44336")
            return
        self.update_status("Summarizing...", "#0288D1")
        summary = self._summarize_pages(full_text, max_sentences=5)  # Increased to 5
        self._show_summary(summary)

    def _summarize_pages(self, full_text: str, max_sentences: int) -> str:
        pages = full_text.split("\n\n")
        summaries = []
        for idx, page_text in enumerate(pages, start=1):
            if page_text.strip():
                page_summary = self._summarize_single_page(page_text, max_sentences)
                summaries.append(f"[Page {idx} Summary]\n{page_summary}")
        return "\n\n".join(summaries)

    def _summarize_single_page(self, text: str, max_sentences: int) -> str:
        stop_words = set(stopwords.words("english"))
        words = [w.lower() for w in word_tokenize(text) if w.isalpha()]
        freq_table = defaultdict(int)
        for w in words:
            if w not in stop_words:
                freq_table[w] += 1
        sentences = sent_tokenize(text)
        sentence_scores = {s: sum(freq_table.get(w.lower(), 0) for w in word_tokenize(s)) for s in sentences}
        ranked = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences]
        ordered = [s for s in sentences if s in ranked]
        return " ".join(ordered)

    def _show_summary(self, summary: str):
        win = CTkToplevel()
        win.title("Summary")
        win.geometry("800x400")
        logo_path = os.path.join(os.path.dirname(__file__), 'summary_logo.png')
        logo_icon = ImageTk.PhotoImage(Image.open(logo_path))
        win.iconphoto(False, logo_icon)
        win.after(250, lambda: win.iconphoto(False, logo_icon))
        
        tb = CTkTextbox(win, wrap="word", font=("Consolas", 12))
        tb.pack(expand=True, fill="both", padx=10, pady=10)
        tb.insert("1.0", summary)
        
        self.copy_btn = CTkButton(
            win,
            text="📋 Copy All",
            command=lambda: (
                self.clipboard_clear(),
                self.clipboard_append(tb.get("1.0", "end").strip()),
                self.update_status("Copied to clipboard ✅", "green")
            ),
            width=100,
            height=40,
            corner_radius=8,
            font=("Arial", 14)
        )
        self.copy_btn.pack(side="bottom", padx=15, pady=10)

        # Add close button for the summary window
        CTkButton(win, text="✖ Close", command=win.destroy, width=100, height=40, corner_radius=8).pack(side="bottom", pady=10)

    def process_pdf(self, file_path):
        try:
            doc = fitz.open(file_path)
            self.current_document = doc
            total_pages = len(doc)
        
            for page_num, page in enumerate(doc):
                with self.lock:
                    if not self.is_processing:
                        break
                text = page.get_text()
                self.update_text_area(f"Page {page_num+1}\n{text}\n\n")
                progress = (page_num + 1) / total_pages
                self.update_progress(progress)
        
            self.update_status(f"Loaded {total_pages} pages", "green")
        
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "red")
        finally:
            with self.lock:
                if self.current_document:
                    self.current_document.close()
                    self.current_document = None
                    self.is_processing = False
                self.update_progress(0)

    def close_pdf(self):
        with self.lock:
            self.is_processing = False
            if self.current_document:
                try:
                    self.current_document.close()
                except:
                    pass
                self.current_document = None
            self.file_label.configure(text="No file selected")
            self.text_area.delete("1.0", "end")
            self.progress_bar.set(0)
            self.update_status("PDF closed", "orange")
            self.close_btn.configure(state="disabled")

    def update_text_area(self, text):
        self.after(0, lambda: self.text_area.insert("end", text))

    def update_progress(self, value):
        self.after(0, lambda: self.progress_bar.set(value))

    def update_status(self, message, color="black"):
        self.after(0, lambda: self.status_bar.configure(text=message, text_color=color))

    def on_close(self):
        self.close_pdf()
        self.destroy()

if __name__ == "__main__":
    app = PDFViewerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()