import os

class Config:
    TITLE = "PDF Viewer Pro"
    SIZE = "1200x750"
    LOGO_PATH = os.path.join(os.path.dirname(__file__), 'logo/logo.png')
    SUMMARY_LOGO_PATH = os.path.join(os.path.dirname(__file__), 'logo/summary_logo.png')
