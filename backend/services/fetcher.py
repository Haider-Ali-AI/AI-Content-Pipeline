import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class FetcherService:
    def __init__(self, rss_feeds: List[str]):
        self.rss_feeds = rss_feeds
        
    def fetch_articles(self, limit: int = 10) -> List[Dict]:
        """Fetch articles from RSS feeds"""
        articles = []
        
        for feed_url in self.rss_feeds:
            try:
                articles.extend(self._fetch_from_feed(feed_url, limit // len(self.rss_feeds)))
            except Exception as e:
                logger.error(f"Error fetching from {feed_url}: {str(e)}")
                continue
                
        return articles[:limit]
    
    def _fetch_from_feed(self, feed_url: str, limit: int) -> List[Dict]:
        """Fetch articles from a single RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            articles = []
            
            for entry in feed.entries[:limit]:
                article = {
                    'title': entry.get('title', 'No Title'),
                    'original_text': self._extract_content(entry),
                    'source': feed.feed.get('title', 'Unknown Source'),
                    'url': entry.get('link', ''),
                    'category': self._extract_category(entry),
                    'published': entry.get('published', '')
                }
                articles.append(article)
                
            return articles
            
        except Exception as e:
            logger.error(f"Error parsing feed {feed_url}: {str(e)}")
            return []
    
    def _extract_content(self, entry) -> str:
        """Extract content from RSS entry"""
        # Try different content fields
        content = ''
        
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value if isinstance(entry.content, list) else entry.content
        elif hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        
        # Clean HTML tags (basic cleaning)
        import re
        content = re.sub(r'<[^>]+>', '', content)
        content = content.strip()
        
        return content[:1000] if content else 'No content available'
    
    def _extract_category(self, entry) -> Optional[str]:
        """Extract category from RSS entry"""
        if hasattr(entry, 'tags') and entry.tags:
            return entry.tags[0].term if entry.tags else None
        return None
    
    def validate_feed_url(self, url: str) -> bool:
        """Validate if URL is a valid RSS feed"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                return len(feed.entries) > 0
        except Exception:
            pass
        return False