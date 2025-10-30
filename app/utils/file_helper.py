import os
from tkinter import filedialog
from app.utils.LogManager import get_logger
from CTkMessagebox import CTkMessagebox
from pathlib import Path
import fitz

class FileHelper:
    """Hanlder file I/O and dialog operations."""
    def __init__(self):
        self.logger = get_logger()

    def open_pdf_dialog(self)-> str | None:
        """Open a PDF file dialog and select a PDF"""
        file_path = filedialog.askopenfilename(
            title="Select a PDF",
            filetypes=(("PDF files", "*.pdf"), ("all files", "*.*")),
        )
        if file_path:
            self.logger.info(f"selected PDF file: {file_path}")
            CTkMessagebox(icon="info",title="PDF file", message=f"Selected PDF file: {file_path}")
        else:
            self.logger.error("no PDF file")
            CTkMessagebox(icon="cancel",title="no PDF file", message="no PDF file")
        return file_path

    def read_pdf(self, file_path: Path) -> str:
        """Extract text from the given PDF file and store per-page content."""
        try:
            text_content = ""
            texts = []
            with fitz.open(file_path) as pdf:
                for page_num, page in enumerate(pdf, start=1):
                    page_text = page.get_text("text")
                    text_content += page_text + "\n\n"
                    pages = {"page_num": page_num, "text_content": page_text}
                    texts.append(pages)

            self.logger.info(f"PDF read successfully: {file_path}")
            CTkMessagebox(icon="info", title="PDF file", message=f"PDF read successfully: {file_path}")

            return text_content.strip()
        except Exception as e:
            self.logger.error(f"Failed to read PDF: {file_path} error: {e}")
            CTkMessagebox(icon='cancel', title="PDF file", message=f"Failed to read PDF: {file_path} error: {e}")
            return ""

