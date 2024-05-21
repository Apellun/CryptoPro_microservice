import os
import pathlib
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
cwd = pathlib.Path(__file__).parent.resolve()