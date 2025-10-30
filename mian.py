from app.core.pdf_viewer import PDFViewerPro
import os

#run all

if __name__ == '__main__':
    app = PDFViewerPro()
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress TensorFlow INFO and WARNING logs
    os.environ["TRANSFORMERS_VERBOSITY"] = "error"  # Hide Hugging Face loading spamo
    app.mainloop()
