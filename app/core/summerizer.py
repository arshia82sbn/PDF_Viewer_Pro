from __future__ import annotations
from app.utils.LogManager import get_logger
from ttkbootstrap.dialogs import Messagebox
from typing import List
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM,pipeline
import abc
import threading

# Resource Manager
class HFModelManager:
    """
    Singleton to load and cache the Hugging Face summarization model.
    Thread-safe.
    """
    _instance = None
    _lock = threading.Lock()
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    def __init__(self):
        self.logger = get_logger()
        if getattr(self, "_initialized",False):
            return
        try:
            # Load model and tokenizer
            model_name = "shorecode/t5-efficient-tiny-summarizer-general-purpose-v2"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            self.summarizer = pipeline("summarization",model=self.model,tokenizer=self.tokenizer)
            Messagebox.show_info(title="Model Summarization",message="Hugging Face summarization model loaded",bootstyle="success")
            self.logger.info("Hugging Face summarization model loaded")
            self._initialized = True
        except Exception as e:
            Messagebox.show_error(title="Model Summarization",message=f"Failed to load HFModelManager: {e}",bootstyle="danger")
            self.logger.info("Failed to load HFModelManager")
# Strategy base class
class Summerization(abc.ABC):
    @abc.abstractmethod
    def summarize_page(self,text:str,max_sentences:int=5)->str:
        raise NotImplementedError

# Hugging face summarizer strategy
class HuggingFaceSummarization(Summerization):
    """
    Summarizes text using Hugging Face t5-efficient-tiny model.
    Splits pages and runs summarization.
    """
    def __init__(self):
        self.logger = get_logger()
        self._hf_manager = HFModelManager()

    def summarize_page(self,text:str,max_sentences:int=5)->str:
        # HF model does not use max_sentences, approximate by truncating long text
        if not text.strip():
            self.logger.info("No text provided")
            return ""
        try:
            # Limit input length for tiny model
            MAX_INPUT_LENGTH = 512
            input_text = text
            if len(text.split()) > MAX_INPUT_LENGTH:
                input_text = " ".join(text.split()[:MAX_INPUT_LENGTH])
            self.logger.info(f"Summarizing {input_text[:50]}...")
            Messagebox.show_info(title="Summarization",message=f"Summarizing {input_text[:50]}...",bootstyle="success")
            result = self._hf_manager.summarizer(input_text,max_length=150,min_length=40,do_sample=False)
            return result[0]["summary_text"]
        except Exception as e:
            self.logger.error(f"Failed to summarize: {e}")
            Messagebox.show_error(title="Summarization",message=f"Failed to summarize: {e}",bootstyle="danger")
            return ""

#context class
class Summarizer:
    """
    Context class that uses a SummarizerStrategy to summarize
    an entire document divided into pages.
    """
    def __init__(self,strategy: Summerization = None):
        self._strategy = strategy if strategy else HuggingFaceSummarization()
        self.logger = get_logger()

    def set_strategy(self,strategy:Summerization):
        self._strategy = strategy

    def summarize(self,full_text:str,max_sentences_per_pages:int=5)->dict:
        """
        full_text: entire document text, pages separated by double newlines '\n\n'
        returns a composed summary with each page's summary preceded by a header.
        """
        if not full_text.strip():
            return ""
        try:
            pages = [p for p in full_text.split("\n\n") if p.strip()]
            summaries:List[str] = []

            for idx , page in enumerate(pages,start=1):
                page_summary = self._strategy.summarize_page(page,max_sentences_per_pages)
                summaries.append(page_summary)
            self.logger.info(f"Summarizing {len(pages)} pages...")
            Messagebox.show_error(title="Summarization", message=f"Summarizing {len(pages)} pages.", bootstyle="success")
            return {"text":f"{"\n\n".join(summaries)}","pages":pages}
        except Exception as e:
            self.logger.error(f"Failed to summarize: {e}")
            Messagebox.show_error(title="Summarization",message=f"Failed to summarize: {e}",bootstyle="danger")
            return {"text":"","pages":0}