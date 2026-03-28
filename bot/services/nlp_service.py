# file: bot/services/nlp_service.py
"""NLP/AI service for profile suggestions and moderation"""

import logging
import httpx
from typing import Optional
from config import config

logger = logging.getLogger(__name__)


class NLPService:
    """Service for AI-powered features"""
    
    def __init__(self):
        self.api_base = config.AI_API_BASE_URL
        self.api_key = config.AI_API_KEY
        self.enabled = config.AI_ENABLED
    
    async def generate_profile_bio_suggestion(self, user_context: dict) -> Optional[str]:
        """Generate a profile bio suggestion using AI"""
        
        if not self.enabled:
            logger.warning("AI service not configured")
            return None
        
        try:
            prompt = f"""Generate a fun, engaging dating profile bio for someone who:
- Name: {user_context.get('name')}
- Age: {user_context.get('age')}
- Interests: {user_context.get('interests')}
- Purpose: {user_context.get('purpose')}

Make it 1-2 sentences, funny and authentic. No emojis."""
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 100
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                bio = data["choices"][0]["message"]["content"].strip()
                return bio
        
        except Exception as e:
            logger.error(f"Error generating bio suggestion: {e}")
            return None
    
    async def suggest_opening_line(self, match_profile: dict) -> Optional[str]:
        """Suggest an opening line for a match"""
        
        if not self.enabled:
            return None
        
        try:
            prompt = f"""Generate a fun, flirty opening line for a dating match with:
- Name: {match_profile.get('name')}
- Interests: {match_profile.get('interests')}
- Bio: {match_profile.get('bio')}

Make it 1 sentence, genuine, not cheesy. No emojis."""
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 50
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                line = data["choices"][0]["message"]["content"].strip()
                return line
        
        except Exception as e:
            logger.error(f"Error generating opening line: {e}")
            return None
    
    async def moderate_message(self, text: str) -> bool:
        """Check if message is appropriate (returns True if OK)"""
        
        if not self.enabled:
            return True  # Allow by default if AI disabled
        
        try:
            prompt = f"""Is this message appropriate for a dating app? Reply only SAFE or UNSAFE.

Message: "{text}" """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 10
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                result = data["choices"][0]["message"]["content"].strip().upper()
                return "SAFE" in result
        
        except Exception as e:
            logger.error(f"Error moderating message: {e}")
            return True  # Allow if error


# Global NLP service instance
nlp_service = NLPService()
