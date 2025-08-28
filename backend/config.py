import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("sqlite:///"):
        # Convert relative sqlite path into absolute
        rel_path = db_url.replace("sqlite:///", "")
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, rel_path)}"
    else:
        SQLALCHEMY_DATABASE_URI = db_url or f"sqlite:///{os.path.join(BASE_DIR, 'data', 'drafts.db')}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # RSS Feed URLs
    RSS_FEEDS = [
        'https://feeds.bbci.co.uk/news/rss.xml',
        'https://rss.cnn.com/rss/edition.rss',
        'https://feeds.reuters.com/reuters/topNews',
        'https://techcrunch.com/feed/',
        'https://www.theguardian.com/world/rss'
    ]
    
    # AI Settings
    AI_REWRITE_SETTINGS = {
        'max_tokens': 1000,
        'temperature': 0.7,
        'default_tone': 'professional',
        'default_length': 'medium'
    }
