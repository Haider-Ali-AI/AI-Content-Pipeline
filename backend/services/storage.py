import json
import os
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, approved_file_path: str = 'data/approved_articles.json'):
        self.approved_file_path = approved_file_path
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.approved_file_path), exist_ok=True)
        
        # Create approved articles file if it doesn't exist
        if not os.path.exists(self.approved_file_path):
            self._save_approved_articles([])
    
    def save_approved_article(self, article_data: Dict[str, Any]) -> bool:
        """Save an approved article to JSON file"""
        try:
            approved_articles = self.load_approved_articles()
            
            # Add metadata
            article_data['approved_at'] = datetime.utcnow().isoformat()
            article_data['status'] = 'approved'
            
            approved_articles.append(article_data)
            
            return self._save_approved_articles(approved_articles)
            
        except Exception as e:
            logger.error(f"Error saving approved article: {str(e)}")
            return False
    
    def load_approved_articles(self) -> List[Dict[str, Any]]:
        """Load approved articles from JSON file"""
        try:
            if os.path.exists(self.approved_file_path):
                with open(self.approved_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
            
        except Exception as e:
            logger.error(f"Error loading approved articles: {str(e)}")
            return []
    
    def _save_approved_articles(self, articles: List[Dict[str, Any]]) -> bool:
        """Save approved articles list to JSON file"""
        try:
            with open(self.approved_file_path, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            return True
            
        except Exception as e:
            logger.error(f"Error saving approved articles: {str(e)}")
            return False
    
    def get_approved_article_by_id(self, article_id: int) -> Dict[str, Any]:
        """Get approved article by ID"""
        approved_articles = self.load_approved_articles()
        
        for article in approved_articles:
            if article.get('id') == article_id:
                return article
        
        return None
    
    def delete_approved_article(self, article_id: int) -> bool:
        """Delete approved article by ID"""
        try:
            approved_articles = self.load_approved_articles()
            
            # Filter out the article to delete
            updated_articles = [a for a in approved_articles if a.get('id') != article_id]
            
            if len(updated_articles) < len(approved_articles):
                return self._save_approved_articles(updated_articles)
            
            return False  # Article not found
            
        except Exception as e:
            logger.error(f"Error deleting approved article: {str(e)}")
            return False
    
    def export_approved_articles(self, format: str = 'json') -> str:
        """Export approved articles in specified format"""
        approved_articles = self.load_approved_articles()
        
        if format == 'json':
            return json.dumps(approved_articles, indent=2, ensure_ascii=False)
        
        # Add other formats as needed (CSV, XML, etc.)
        return json.dumps(approved_articles, indent=2, ensure_ascii=False)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about approved articles"""
        approved_articles = self.load_approved_articles()
        
        if not approved_articles:
            return {
                'total_articles': 0,
                'sources': [],
                'categories': [],
                'latest_approval': None
            }
        
        sources = list(set(article.get('source', 'Unknown') for article in approved_articles))
        categories = list(set(article.get('category', 'Uncategorized') for article in approved_articles if article.get('category')))
        
        # Find latest approval
        latest_approval = None
        for article in approved_articles:
            if article.get('approved_at'):
                if not latest_approval or article['approved_at'] > latest_approval:
                    latest_approval = article['approved_at']
        
        return {
            'total_articles': len(approved_articles),
            'sources': sources,
            'categories': categories,
            'latest_approval': latest_approval
        }