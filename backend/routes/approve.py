from flask import Blueprint, jsonify, request
from ..models import db, DraftArticle
from ..services.storage import StorageService
import logging

logger = logging.getLogger(__name__)

approve_bp = Blueprint('approve', __name__)

@approve_bp.route('/approve/<int:article_id>', methods=['POST'])
def approve_article(article_id):
    """Approve an article and move it to approved storage"""
    try:
        article = DraftArticle.query.get_or_404(article_id)
        
        if article.status == 'approved':
            return jsonify({'error': 'Article already approved'}), 400
        
        # Initialize storage service
        storage_service = StorageService()
        
        # Save to approved articles JSON
        article_data = article.to_dict()
        success = storage_service.save_approved_article(article_data)
        
        if success:
            # Update status in database
            article.status = 'approved'
            db.session.commit()
            
            return jsonify({
                'message': 'Article approved successfully',
                'article': article.to_dict()
            })
        else:
            return jsonify({'error': 'Failed to save approved article'}), 500
            
    except Exception as e:
        logger.error(f"Error approving article {article_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to approve article'}), 500

@approve_bp.route('/approved', methods=['GET'])
def get_approved_articles():
    """Get all approved articles"""
    try:
        storage_service = StorageService()
        approved_articles = storage_service.load_approved_articles()
        
        # Sort by approval date (newest first)
        approved_articles.sort(
            key=lambda x: x.get('approved_at', ''), 
            reverse=True
        )
        
        return jsonify(approved_articles)
        
    except Exception as e:
        logger.error(f"Error fetching approved articles: {str(e)}")
        return jsonify({'error': 'Failed to fetch approved articles'}), 500

@approve_bp.route('/approved/<int:article_id>', methods=['GET'])
def get_approved_article(article_id):
    """Get specific approved article"""
    try:
        storage_service = StorageService()
        article = storage_service.get_approved_article_by_id(article_id)
        
        if article:
            return jsonify(article)
        else:
            return jsonify({'error': 'Approved article not found'}), 404
            
    except Exception as e:
        logger.error(f"Error fetching approved article {article_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch approved article'}), 500

@approve_bp.route('/approved/<int:article_id>', methods=['DELETE'])
def delete_approved_article(article_id):
    """Delete an approved article"""
    try:
        storage_service = StorageService()
        success = storage_service.delete_approved_article(article_id)
        
        if success:
            return jsonify({'message': 'Approved article deleted successfully'})
        else:
            return jsonify({'error': 'Approved article not found'}), 404
            
    except Exception as e:
        logger.error(f"Error deleting approved article {article_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete approved article'}), 500

@approve_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get statistics about approved articles"""
    try:
        storage_service = StorageService()
        stats = storage_service.get_statistics()
        
        # Also get draft statistics
        draft_count = DraftArticle.query.filter_by(status='pending').count()
        approved_count = DraftArticle.query.filter_by(status='approved').count()
        
        stats.update({
            'draft_count': draft_count,
            'approved_count': approved_count,
            'total_processed': draft_count + approved_count
        })
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@approve_bp.route('/export', methods=['GET'])
def export_approved_articles():
    """Export approved articles"""
    try:
        storage_service = StorageService()
        format_type = request.args.get('format', 'json')
        
        exported_data = storage_service.export_approved_articles(format_type)
        
        return jsonify({
            'data': exported_data,
            'format': format_type
        })
        
    except Exception as e:
        logger.error(f"Error exporting approved articles: {str(e)}")
        return jsonify({'error': 'Failed to export approved articles'}), 500