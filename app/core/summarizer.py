# summarizer.py (fast & stable version)
from CTkMessagebox import CTkMessagebox
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import threading
from app.utils.LogManager import get_logger
import traceback
import os


# ============================================================
#  Base Strategy Interface
# ============================================================
class SummarizationStrategy:
    """Defines the summarization interface."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.is_loaded = False
        self.load_lock = threading.Lock()

    def load_model(self):
        raise NotImplementedError()

    def summarize(self, text: str) -> str:
        raise NotImplementedError()


# ============================================================
#  Hugging Face Transformers Strategy
# ============================================================

class HuggingFaceSummarization(SummarizationStrategy):
    """Fast and safe Hugging Face summarization strategy."""

    def __init__(self, model_name: str = "t5-small"):
        super().__init__(model_name)
        self.logger = get_logger()
        self.cache_dir = os.path.join(os.getcwd(), "models_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def load_model(self):
        """Safely loads model with caching."""
        if self.is_loaded:
            return True

        with self.load_lock:
            if self.is_loaded:
                return True
            try:
                # ---------------------------
                # 🔍 Auto-detect and prepare cache directory
                # ---------------------------
                project_root = os.path.dirname(os.path.abspath(__file__))
                possible_paths = [
                    os.path.join(project_root, "models_cache"),  # same folder as summarizer.py
                    os.path.join(project_root, "..", "models_cache"),  # one level up
                    os.path.join(os.getcwd(), "models_cache"),  # current working dir
                    os.path.join(project_root, "..", "app", "models_cache"),  # inside app
                ]

                # Pick first valid or create new
                for path in possible_paths:
                    if os.path.exists(path):
                        self.cache_dir = os.path.abspath(path)
                        break
                else:
                    self.cache_dir = os.path.abspath(possible_paths[0])
                    os.makedirs(self.cache_dir, exist_ok=True)

                self.logger.info(f"📂 Using cache directory: {self.cache_dir}")
                CTkMessagebox(icon="info",title="Loading",message=f"[Summarizer] Cache directory: {self.cache_dir}")
                try:
                    self.logger.info(f"[Summarizer] Loading model '{self.model_name}' from cache: {self.cache_dir}")
                    self.logger.info(f"Loading summarization model: {self.model_name}")
                    self.cache_dir = os.path.join(os.getcwd(), "models_cache")
                    os.makedirs(self.cache_dir, exist_ok=True)
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        self.model_name,
                        cache_dir=self.cache_dir,
                        local_files_only=False,  # Set True if model is already downloaded
                    )

                    self.model = AutoModelForSeq2SeqLM.from_pretrained(
                        self.model_name,
                        cache_dir=self.cache_dir,
                        local_files_only=False,  # Set True to force offline mode
                    )

                    # Use the summarization pipeline
                    self.pipeline = pipeline(
                        "summarization",
                        model=self.model,
                        tokenizer=self.tokenizer,
                        device_map="auto",
                    )

                    self.is_loaded = True

                    # Warm-up (improves first inference speed)
                    _ = self.pipeline("Warm up summarization model.", max_length=30, min_length=5)

                    self.logger.info(f"Hugging Face summarizer '{self.model_name}' loaded successfully.")
                    CTkMessagebox(icon="info",title="Success",message="Model loaded and warmed up ✅")
                    return True

                except Exception as e:
                    self.logger.error(f"Failed to load model '{self.model_name}': {e}")
                    return False
            except Exception as e:
                self.logger.error(f"Failed to load model '{self.model_name}': {e}")
                CTkMessagebox(icon="cancel",title="Error",message=f"Failed to load model '{self.model_name}': {e}")
                return False

    def summarize(self, text: str) -> str:
        """Perform summarization."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        if not text.strip():
            return "[No text provided]"

        try:
            result = self.pipeline(
                text,
                max_length=200,
                min_length=30,
                do_sample=False,
                truncation=True
            )
            return result[0]["summary_text"]
        except Exception as e:
            self.logger.error(f"Error during summarization: {e}")
            return "[Summarization failed]"


# ============================================================
#  Dummy Summarizer
# ============================================================

class DummySummarization(SummarizationStrategy):
    """Fallback summarizer for offline or failed models."""

    def load_model(self):
        self.is_loaded = True
        return True

    def summarize(self, text: str) -> str:
        sentences = text.split(".")
        preview = ". ".join(sentences[:3]) + "."
        return f"[Dummy summary]\n{preview.strip()}"


# ============================================================
#  Factory Pattern
# ============================================================

class SummarizerFactory:
    """Creates summarizer strategy instances."""

    @staticmethod
    def create(strategy="huggingface", model_name="t5-small") -> SummarizationStrategy:
        strategy = strategy.lower()
        if strategy == "huggingface":
            return HuggingFaceSummarization(model_name)
        elif strategy == "dummy":
            return DummySummarization(model_name="none")
        else:
            raise ValueError(f"Unknown strategy: {strategy}")


# ============================================================
#  Summarizer Context
# ============================================================

class Summarizer:
    """Manages model loading and summarization safely."""

    def __init__(self, strategy: SummarizationStrategy):
        self.strategy = strategy
        self.logger = get_logger()
        self._is_loading = False
        self._load_thread = None

    def load_model_async(self, callback=None):
        """Load model in background."""

        def _load():
            self._is_loading = True
            self.logger.info("[Summarizer] Loading model asynchronously...")
            success = self.strategy.load_model()
            self._is_loading = False

            if not success:
                CTkMessagebox(icon="cancel",title="Error",message="[Summarizer] Model load failed — switching to DummySummarization.")
                self.strategy = DummySummarization("none")
                self.strategy.load_model()

            if callback:
                callback(success)

        if not self.strategy.is_loaded and not self._is_loading:
            self._load_thread = threading.Thread(target=_load, daemon=True)
            self._load_thread.start()

    def summarize(self, text: str) -> str:
        """Run summarization safely."""
        if not self.strategy.is_loaded:
            self.logger.warning("Model not loaded yet. Returning dummy summary.")
            return "[Model not loaded yet]"
        return self.strategy.summarize(text)
