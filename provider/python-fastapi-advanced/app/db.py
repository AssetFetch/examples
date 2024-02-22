import sqlite3
import os
from . import error

connection : sqlite3.Connection

def initialize(path : str):

	global connection 
	connection = sqlite3.connect(path)

