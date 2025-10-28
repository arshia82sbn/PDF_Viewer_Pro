import os
from tkinter import filedialog
from app.utils.LogManager import get_logger
from ttkbootstrap.dialogs import Messagebox

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
            Messagebox.show_info(title="PDF file", message=f"Selected PDF file: {file_path}",bootstyle="success")
        else:
            self.logger.error("no PDF file")
            Messagebox.show_error(title="no PDF file", message="no PDF file",bootstyle="danger")
        return file_path
    def read_pdf(self,file_path:str)->str:
        """Exctract text from the given PDF file"""
        import fitz
        try:
            text_content = ""
            with fitz.open(file_path) as pdf:
                for page in pdf:
                    text_content += page.getText("text") + "\n\n"
            self.logger.info(f"PDF read successfully: {file_path}")
            Messagebox.show_info(title="PDF file", message=f"PDF read successfully: {file_path}",bootstyle="success")
            return text_content.strip()
        except Exception as e:
            self.logger.error(f"Failed to read PDF: {file_path}")
            Messagebox.show_error(title="PDF file", message=f"Failed to read PDF: {file_path}",bootstyle="danger")
            return ""