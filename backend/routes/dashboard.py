from flask import Blueprint, jsonify, request
from ..models import db, DraftArticle
from ..services.fetcher import FetcherService
from ..services.ai_service import AIService
from ..config import Config
import logging

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/drafts', methods=['GET'])
def get_drafts():
    """Get all draft articles"""
    try:
        drafts = DraftArticle.query.filter_by(status='pending').order_by(DraftArticle.created_at.desc()).all()
        return jsonify([draft.to_dict() for draft in drafts])
    except Exception as e:
        logger.error(f"Error fetching drafts: {str(e)}")
        return jsonify({'error': 'Failed to fetch drafts'}), 500

@dashboard_bp.route('/article/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """Get specific article by ID"""
    try:
        article = DraftArticle.query.get_or_404(article_id)
        return jsonify(article.to_dict())
    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {str(e)}")
        return jsonify({'error': 'Article not found'}), 404

@dashboard_bp.route('/fetch-articles', methods=['POST'])
def fetch_articles():
    """Fetch new articles from RSS feeds"""
    try:
        fetcher = FetcherService(Config.RSS_FEEDS)
        articles = fetcher.fetch_articles(limit=10)
        
        saved_count = 0
        for article_data in articles:
            # Check if article already exists (by title and source)
            existing = DraftArticle.query.filter_by(
                title=article_data['title'],
                source=article_data['source']
            ).first()
            
            if not existing:
                draft = DraftArticle(
                    title=article_data['title'],
                    original_text=article_data['original_text'],
                    source=article_data['source'],
                    category=article_data.get('category'),
                    url=article_data.get('url'),
                    status='pending'
                )
                db.session.add(draft)
                saved_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully fetched {saved_count} new articles',
            'total_fetched': len(articles),
            'saved_count': saved_count
        })
        
    except Exception as e:
        logger.error(f"Error fetching articles: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to fetch articles'}), 500

@dashboard_bp.route('/rewrite/<int:article_id>', methods=['POST'])
def rewrite_article(article_id):
    """Generate AI rewrite for article"""
    try:
        article = DraftArticle.query.get_or_404(article_id)
        
        # Get rewrite options from request
        data = request.get_json() or {}
        tone = data.get('tone', 'professional')
        length = data.get('length', 'medium')
        language = data.get('language', 'en')
        
        # Initialize AI service
        if not Config.GEMINI_API_KEY:
            return jsonify({'error': 'Gemini API key not configured'}), 500
        
        ai_service = AIService(Config.GEMINI_API_KEY)
        
        # Generate rewrite
        ai_text = ai_service.rewrite_article(
            article.original_text,
            tone=tone,
            length=length,
            language=language
        )
        
        if ai_text:
            article.ai_text = ai_text
            db.session.commit()
            
            return jsonify({
                'message': 'Article rewritten successfully',
                'ai_text': ai_text
            })
        else:
            return jsonify({'error': 'Failed to generate AI rewrite'}), 500
            
    except Exception as e:
        logger.error(f"Error rewriting article {article_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to rewrite article'}), 500

@dashboard_bp.route('/delete/<int:article_id>', methods=['DELETE'])
def delete_draft(article_id):
    """Delete a draft article"""
    try:
        article = DraftArticle.query.get_or_404(article_id)
        db.session.delete(article)
        db.session.commit()
        
        return jsonify({'message': 'Draft deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting draft {article_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete draft'}), 500