"""
Configuration module for University Research Opportunity Portal.
Loads environment variables and sets up database connection parameters.
Supports execution from both the project root and the backend directory.
"""
import os
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

# Resolve potential .env locations
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

ENV_LOCATIONS = [
    Path.cwd() / '.env',       # Current working directory
    PROJECT_ROOT / '.env',     # Project root directory
    CURRENT_DIR / '.env',      # Backend directory
]

# Load first existing .env file
for env_file in ENV_LOCATIONS:
    if env_file.is_file():
        load_dotenv(dotenv_path=env_file, override=False)
        break
else:
    # Fallback to default search
    load_dotenv(override=False)


class Config:
    """Application configuration using environment variables."""
    # Database connection parameters
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'portal_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'research_portal')

    # URL-encode password in case it contains special characters (@, %, :, etc.)
    _encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

    # SQLAlchemy Database URI (using PyMySQL driver)
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{_encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'false').lower() in ('true', '1')

    # Security configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
