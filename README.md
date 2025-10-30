# PDF Viewer Pro Documentation

## 📘 Overview
**PDF Viewer Pro** is a modern desktop application built using **Python**, **Customtkinter**, and **PyMuPDF (fitz)**. It allows users to open, view, and summarize PDF files within a sleek and user-friendly interface.

The project follows a **modular structure** and **object-oriented design**, promoting maintainability, scalability, and readability. It uses **design patterns** for key functionalities such as summarization and UI handling.

---

## 🧱 Project Structure
```
PDF_Viewer_Pro/
│
├── main.py                  # Entry point of the application
├── summarizer.py            # Handles text summarization logic
├── pdf_viewer.py            # PDF rendering and management
├── ui/                      # User Interface components
│   ├── __init__.py
│   ├── toolbar.py           # Toolbar with buttons and controls
│   ├── text_area.py         # Custom text widget wrapper
│
├── models/                  # Design pattern implementations
│   ├── __init__.py
│   ├── summarizer_factory.py # Factory pattern for summarizer models
│   ├── observer.py           # Observer pattern for UI updates
│
├── assets/                  # Icons, images, and other static files
│
├── requirements.txt         # Dependencies
└── README.md                # Project documentation
```

---

## ⚙️ Core Components

### 1. `main.py`
The main entry point that initializes the `PDFViewerPro` app window. It handles the root UI structure, initializes widgets, and binds actions.

**Features:**
- Launches the main window.
- Handles open, close, and summarize actions.
- Integrates with the summarizer engine.

---

### 2. `pdf_viewer.py`
Responsible for rendering PDF pages using **PyMuPDF (fitz)** and displaying them as images inside a Customtkinter frame.

**Key Functions:**
- `load_pdf(path)` — Loads and displays the selected PDF.
- `close_pdf()` — Clears the canvas and resets UI.

---

### 3. `summarizer.py`
Implements an **object-oriented summarization system** using a **Factory Pattern** to switch between lightweight and high-performance summarizer models.

**Classes:**
- `BaseSummarizer` — Abstract base class.
- `LightSummarizer` — Fast, keyword-based summarizer.
- `TransformerSummarizer` — Deep learning model for high-accuracy summaries.
- `SummarizerFactory` — Returns appropriate summarizer instance.

**Usage Example:**
```python
from summarizer_factory import SummarizerFactory

summarizer = SummarizerFactory.get_summarizer(model="light")
summary = summarizer.summarize(text)
```

---

### 4. `ui/toolbar.py`
Contains button logic for opening, closing, and summarizing PDFs. It uses **Command Pattern** to decouple button actions from the main logic.

---

### 5. `ui/text_area.py`
Because `Customtkinter` does not natively support `insert()` and `delete()` methods in its text widget, a **custom wrapper** is implemented around `tk.Text` to emulate this behavior with additional style and control integration.

---

## 🧩 Design Patterns Used
| Pattern | Purpose | Implementation |
|----------|----------|----------------|
| **Factory** | Dynamically creates summarizer instances. | `SummarizerFactory` |
| **Strategy** | Switch summarization algorithms easily. | Different summarizer classes |
| **Observer** | Keeps UI in sync with background tasks. | UI progress updates |
| **Command** | Handles user actions cleanly. | Toolbar button commands |

---

## 🧠 Summarizer Models

### Lightweight Summarizer
- Algorithm: Frequency-based extraction
- Fast execution, low memory
- Best for short documents

### Transformer Summarizer
- Algorithm: BART / T5 / Pegasus (via Hugging Face Transformers)
- Higher accuracy, contextual understanding
- Suitable for long or complex documents

---

## 🚀 Installation & Run

### Requirements
Install dependencies:
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
python main.py
```

---

## 📂 .gitignore
Typical `.gitignore` content for this project:
```
__pycache__/
*.pyc
.env
*.log
.vscode/
.idea/
assets/__pycache__/
*.pdf
*.png
*.jpg
models/__pycache__/
``` 

---

## 🔮 Future Enhancements
- OCR-based PDF text extraction for scanned PDFs.
- Cloud summarization API integration.
- Multi-language support.
- Dark/light theme toggle.

---

## 👨‍💻 Author
**Arshia Saberian**  
Developed with ❤️ using Python, Customtkinter, and modern OOP design principles.

