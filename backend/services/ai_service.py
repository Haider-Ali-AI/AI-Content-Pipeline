import google.generativeai as genai
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def rewrite_article(self, 
                       original_text: str, 
                       tone: str = 'professional', 
                       length: str = 'medium',
                       language: str = 'en') -> Optional[str]:
        """Rewrite article using Gemini AI"""
        try:
            prompt = self._build_rewrite_prompt(original_text, tone, length, language)
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text.strip()
            else:
                logger.error("No text in Gemini response")
                return None
                
        except Exception as e:
            logger.error(f"Error rewriting article: {str(e)}")
            return None
    
    def _build_rewrite_prompt(self, text: str, tone: str, length: str, language: str) -> str:
        """Build prompt for article rewriting"""
        length_instructions = {
            'short': 'Keep it concise, around 100-150 words',
            'medium': 'Write a medium-length article, around 200-300 words',
            'long': 'Write a comprehensive article, around 400-500 words'
        }
        
        tone_instructions = {
            'professional': 'Use a professional, journalistic tone',
            'casual': 'Use a casual, conversational tone',
            'formal': 'Use a formal, academic tone'
        }
        
        prompt = f"""
Please rewrite the following news article with these specifications:

TONE: {tone_instructions.get(tone, 'professional')}
LENGTH: {length_instructions.get(length, 'medium-length')}
LANGUAGE: {language}

Requirements:
- Maintain all factual information
- Make it engaging and well-structured
- Use clear, readable language
- Add appropriate transitions between paragraphs
- Ensure proper grammar and spelling

Original Article:
{text}

Rewritten Article:
"""
        return prompt
    
    def generate_summary(self, text: str, max_length: int = 150) -> Optional[str]:
        """Generate a summary of the article"""
        try:
            prompt = f"""
Please provide a concise summary of this article in {max_length} characters or less:

{text}

Summary:
"""
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                summary = response.text.strip()
                return summary[:max_length] if len(summary) > max_length else summary
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return None
    
    def extract_key_points(self, text: str) -> Optional[list]:
        """Extract key points from article"""
        try:
            prompt = f"""
Extract 3-5 key points from this article as bullet points:

{text}

Key Points:
"""
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                points = response.text.strip().split('\n')
                return [point.strip() for point in points if point.strip()]
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return None
    
    def translate_article(self, text: str, target_language: str) -> Optional[str]:
        """Translate article to target language"""
        try:
            prompt = f"""
Translate the following article to {target_language}. Maintain the journalistic style and all factual information:

{text}

Translation:
"""
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Error translating article: {str(e)}")
            return None