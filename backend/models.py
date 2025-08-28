from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class DraftArticle(db.Model):
    __tablename__ = 'draft_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    ai_text = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    url = db.Column(db.String(1000), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'original_text': self.original_text,
            'ai_text': self.ai_text,
            'source': self.source,
            'category': self.category,
            'url': self.url,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<DraftArticle {self.id}: {self.title[:50]}...>'