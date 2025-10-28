from app.utils.config import Config
from app.utils.LogManager import get_logger
from app.core.summerizer import Summarizer , HuggingFaceSummarization
from PIL import ImageTk, Image
import ttkbootstrap as tkb
from ttkbootstrap.constants import *
import threading

class PDFViewerPro(tkb.window):
    """Setting up all the application"""
    def __init__(self):
        self.config = Config()
        self.logger = get_logger()
        self.summerizer = Summarizer(strategy=HuggingFaceSummarization())
        super().__init__(themename='superhero',title=self.config.TITLE,iconphoto=)
        self.geometry(self.config.SIZE)
        self.title(self.config.TITLE)
        self.configure_layout()
        self.create_widgets()
        self.current_document = None
        self.is_processing = False
        self.Lock = threading.Lock()
        self._set_window_icon(self.config.LOGO_PATH)


    def _set_window_icon(self,path):
        """Setting icon photo"""
        try:
            logo_icon = ImageTk.PhotoImage(Image.open(path))
            self.iconphoto(False, logo_icon)
            self.after(250, lambda: self.iconphoto(False, logo_icon))
            self.logger.info("Setting icon")
        except Exception as e:
            self.logger.warning(f"Setting icon failed with this error:{e}")

    def configure_layout(self):
        """Configuring layout"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def create_widgets(self):
        """Create widgets"""
        # Header
        self.header_frame = ctk.CtkFrame(self)
        