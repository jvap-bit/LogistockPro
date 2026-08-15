import subprocess
import sys
import customtkinter as ctk

# --- INSTALAÇÃO AUTOMÁTICA ---
def instalar_dependencias():
    libs = ["customtkinter", "pandas", "openpyxl", "requests", "reportlab", "qrcode", "pillow", "opencv-python", "pyzbar", "pymupdf"]
    for lib in libs:
        try: __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

instalar_dependencias()

from styles import *

# Tema escuro fixo (igual ao site web)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
from database import init_db
from logic_utils import LogicMixin
from interface_utils import InterfaceMixin

class App(ctk.CTk, LogicMixin, InterfaceMixin):
    def __init__(self):
        super().__init__()
        init_db()
        self.title("LogiStock Pro - Sistema de Gestão")
        self.configure(fg_color=NAVY)
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        self.sidebar_aberta = False
        self.tela_login()

if __name__ == "__main__":
    app = App()
    app.mainloop()