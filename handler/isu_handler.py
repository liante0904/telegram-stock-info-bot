import os
import sys
from telegram import Update, InputFile
from telegram.ext import CallbackContext
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.SQLiteManager import SQLiteManager