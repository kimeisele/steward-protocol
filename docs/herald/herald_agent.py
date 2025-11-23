"""
HERALD Agent - Twitter/Reddit Bot Implementation
Agent ID: agent.vibe.herald
Version: 1.0.0

This implementation follows the STEWARD Protocol for cryptographically
verifiable agent identity and content signing.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

# Twitter API (using tweepy)
import tweepy

# Reddit API (using praw)
import praw

# For content generation (using Anthropic)
from anthropic import Anthropic

# STEWARD Protocol integration
from steward import StewardClient


@dataclass
class ContentPiece:
    """Represents a piece of content to be posted"""
    platform: str  # 'twitter' or 'reddit'
    content_type: str  # 'thread', 'chart', 'question', etc.
    text: str
    metadata: Dict
    quality_score: float
    signature: Optional[str] = None


class HeraldAgent:
    """
    HERALD - Agent Recruitment & Market Intelligence Bot
    
    Focuses on VALUE FIRST approach to avoid downvotes:
    - 80% educational/research content
    - 15% community engagement
    - 5% (or less) STEWARD mentions
    """
    
    def __init__(self, config_path: str = "herald_config.json"):
        """Initialize HERALD with configuration"""
        self.config = self._load_config(config_path)
        
        # Initialize STEWARD Protocol client
        self.steward_client = StewardClient(
            identity_path=self.config['steward']['identity_path'],
            private_key_path=self.config['steward']['private_key_path']
        )
        
        # Initialize Twitter client
        if self.config.get('twitter', {}).get('enabled', False):
            self.twitter_client = self._init_twitter()
        
        # Initialize Reddit client
        if self.config.get('reddit', {}).get('enabled', False):
            self.reddit_client = self._init_reddit()
        
        # Initialize AI for content generation
        self.ai_client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        
        # Rate limiting
        self.post_history = []
        
    def _load_config(self, path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(path, 'r') as f:
            return json.load(f)
    
    def _init_twitter(self) -> tweepy.Client:
        """Initialize Twitter API client"""
        return tweepy.Client(
            bearer_token=os.environ.get('TWITTER_BEARER_TOKEN'),
            consumer_key=os.environ.get('TWITTER_API_KEY'),
            consumer_secret=os.environ.get('TWITTER_API_SECRET'),
            access_token=os.environ.get('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.environ.get('TWITTER_ACCESS_SECRET')
        )
    
    def _init_reddit(self) -> praw.Reddit:
        """Initialize Reddit API client"""
        return praw.Reddit(
            client_id=os.environ.get('REDDIT_CLIENT_ID'),
            client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
            user_agent=self.config['reddit']['user_agent'],
            username=os.environ.get('REDDIT_USERNAME'),
            password=os.environ.get('REDDIT_PASSWORD')
        )
    
    # =========================================================================
    # RESEARCH ENGINE
    # =========================================================================
    
    def research_trend(self, topic: str) -> Dict:
        """
        Research a topic to create valuable content
        
        Returns insights that can be turned into educational content
        """
        prompt = f"""You are HERALD, a research agent focused on AI agents and multi-agent systems.

Research this topic: {topic}

Provide:
1. Key technical insights (what's actually new/useful?)
2. Common failure modes or challenges
3. Practical examples or code patterns
4. Comparison with existing approaches
5. What developers would actually want to know

Format as JSON:
{{
    "insights": ["insight1", "insight2", ...],
    "challenges": ["challenge1", ...],
    "examples": ["example1", ...],
    "comparisons": ["approach1 vs approach2", ...],
    "actionable_takeaways": ["takeaway1", ...]
}}

Important: Focus on GENUINE VALUE, not marketing."""

        response = self.ai_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        research_data = json.loads(response.content[0].text)
        return research_data
    
    # =========================================================================
    # CONTENT GENERATION
    # =========================================================================
    
    def generate_twitter_thread(self, research: Dict, topic: str) -> ContentPiece:
        """
        Generate educational Twitter thread from research
        
        Rules:
        - Start with hook (surprising fact or question)
        - Provide value in every tweet
        - Include code examples where relevant
        - End with question to spark discussion
        - NO promotional language
        """
        prompt = f"""You are HERALD, creating an educational Twitter thread.

Topic: {topic}
Research: {json.dumps(research, indent=2)}

Create a thread (8-10 tweets) that:
1. Opens with a surprising fact or compelling question
2. Each tweet provides standalone value
3. Includes technical details and examples
4. Uses clear, casual language (not corporate)
5. Ends with question to audience
6. NEVER sounds promotional or salesy

Format:
Tweet 1: [Hook]
Tweet 2: [First insight]
...
Tweet N: [Question to audience]

Tone: Helpful peer sharing what they learned, NOT company marketing.
"""

        response = self.ai_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        thread_text = response.content[0].text
        
        return ContentPiece(
            platform='twitter',
            content_type='thread',
            text=thread_text,
            metadata={'topic': topic, 'research': research},
            quality_score=0.0  # To be scored by quality control
        )
    
    def generate_reddit_post(self, research: Dict, topic: str, subreddit: str) -> ContentPiece:
        """
        Generate Reddit post following subreddit culture
        
        Rules:
        - Match subreddit tone (r/programming != r/singularity)
        - Include code or data
        - Be humble, share struggles
        - Ask for feedback
        - NO self-promotion
        """
        
        # Get subreddit culture context
        subreddit_culture = {
            'r/LocalLLaMA': 'Technical, pragmatic, loves open source. Show benchmarks and code.',
            'r/MachineLearning': 'Academic, rigorous. Cite papers, show math.',
            'r/programming': 'Skeptical of hype, values practical solutions. Show real code.',
            'r/singularity': 'Enthusiastic about AI, future-focused. Balance technical with vision.'
        }
        
        culture = subreddit_culture.get(subreddit, 'Technical and helpful')
        
        prompt = f"""You are HERALD, creating a Reddit post for {subreddit}.

Subreddit culture: {culture}

Topic: {topic}
Research: {json.dumps(research, indent=2)}

Create a post that:
1. Title: Honest, not clickbait. Format: "I built X. Here's what I learned."
2. Body: 
   - Share your struggle/journey first
   - Include technical details and code
   - Be humble (not "we solved it" but "here's an approach")
   - Ask for feedback on specific technical aspects
3. Tone: Peer sharing experience, NOT selling anything

CRITICAL: Never mention STEWARD unless directly asked in comments.

Format:
Title: [Your title]

Body:
[Your post text with markdown formatting]
"""

        response = self.ai_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        post_text = response.content[0].text
        
        return ContentPiece(
            platform='reddit',
            content_type='post',
            text=post_text,
            metadata={
                'topic': topic,
                'subreddit': subreddit,
                'research': research
            },
            quality_score=0.0
        )
    
    # =========================================================================
    # QUALITY CONTROL
    # =========================================================================
    
    def check_quality(self, content: ContentPiece) -> float:
        """
        Score content quality to prevent spam/downvotes
        
        Returns: Quality score 0.0-1.0
        """
        prompt = f"""You are a quality control system for HERALD agent.

Content to evaluate:
Platform: {content.platform}
Type: {content.content_type}
Text: {content.text}

Rate this content on:
1. Genuine Value (0-10): Does it teach something useful?
2. Not Promotional (0-10): Is it free of marketing language?
3. Appropriate Tone (0-10): Does it match platform culture?
4. Has Proof (0-10): Includes code, data, or examples?
5. Discussion Potential (0-10): Will it spark good discussion?

Return ONLY a JSON object:
{{
    "genuine_value": X,
    "not_promotional": X,
    "appropriate_tone": X,
    "has_proof": X,
    "discussion_potential": X,
    "overall_score": X.XX (0-1),
    "concerns": ["concern1", ...],
    "recommendation": "APPROVE" or "REJECT" or "REVISE"
}}

REJECT if promotional, spammy, or low-value.
"""

        response = self.ai_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        quality_data = json.loads(response.content[0].text)
        content.quality_score = quality_data['overall_score']
        
        return quality_data
    
    def check_rate_limits(self, platform: str) -> bool:
        """
        Check if we're within rate limits
        
        Rules:
        - Twitter: Max 10 posts/day
        - Reddit: Max 1 post/day per subreddit
        - STEWARD mentions: Max 3/week across all platforms
        """
        now = datetime.now()
        today_posts = [
            p for p in self.post_history
            if p['platform'] == platform and
            (now - datetime.fromisoformat(p['timestamp'])).days < 1
        ]
        
        limits = {
            'twitter': 10,
            'reddit': 1
        }
        
        return len(today_posts) < limits.get(platform, 1)
    
    # =========================================================================
    # POSTING
    # =========================================================================
    
    def sign_content(self, content: ContentPiece) -> str:
        """
        Sign content with STEWARD Protocol
        
        This creates cryptographic proof that HERALD created this content
        """
        artifact = {
            "agent_id": "agent.vibe.herald",
            "platform": content.platform,
            "content_type": content.content_type,
            "content_hash": hash(content.text),
            "timestamp": datetime.now().isoformat(),
            "metadata": content.metadata
        }
        
        signature = self.steward_client.sign(artifact)
        content.signature = signature
        
        return signature
    
    def post_to_twitter(self, content: ContentPiece) -> Dict:
        """Post thread to Twitter"""
        if not self.check_rate_limits('twitter'):
            return {"success": False, "reason": "Rate limit exceeded"}
        
        # Parse thread into individual tweets
        tweets = content.text.split('\n\n')
        
        # Post thread
        previous_tweet_id = None
        for tweet_text in tweets:
            if tweet_text.strip():
                response = self.twitter_client.create_tweet(
                    text=tweet_text.strip(),
                    in_reply_to_tweet_id=previous_tweet_id
                )
                previous_tweet_id = response.data['id']
        
        # Log post
        self._log_post(content, previous_tweet_id)
        
        return {
            "success": True,
            "thread_id": previous_tweet_id,
            "signature": content.signature
        }
    
    def post_to_reddit(self, content: ContentPiece) -> Dict:
        """Post to Reddit"""
        if not self.check_rate_limits('reddit'):
            return {"success": False, "reason": "Rate limit exceeded"}
        
        subreddit = content.metadata['subreddit']
        
        # Parse title and body
        lines = content.text.split('\n')
        title = lines[0].replace('Title:', '').strip()
        body = '\n'.join(lines[2:]).strip()
        
        # Post to subreddit
        subreddit_obj = self.reddit_client.subreddit(subreddit.replace('r/', ''))
        submission = subreddit_obj.submit(title, selftext=body)
        
        # Log post
        self._log_post(content, submission.id)
        
        return {
            "success": True,
            "post_id": submission.id,
            "url": submission.url,
            "signature": content.signature
        }
    
    def _log_post(self, content: ContentPiece, post_id: str):
        """Log post for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "platform": content.platform,
            "content_type": content.content_type,
            "post_id": post_id,
            "quality_score": content.quality_score,
            "signature": content.signature
        }
        self.post_history.append(log_entry)
        
        # Save to file
        with open('herald_audit_log.json', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    # =========================================================================
    # MAIN WORKFLOW
    # =========================================================================
    
    def create_and_post(self, topic: str, platform: str = 'twitter', **kwargs):
        """
        Full pipeline: Research → Generate → QC → Sign → Post
        
        Args:
            topic: What to research and post about
            platform: 'twitter' or 'reddit'
            **kwargs: Platform-specific args (e.g., subreddit for Reddit)
        """
        print(f"[HERALD] Starting pipeline for topic: {topic}")
        
        # Step 1: Research
        print("[HERALD] Step 1: Researching...")
        research = self.research_trend(topic)
        
        # Step 2: Generate content
        print("[HERALD] Step 2: Generating content...")
        if platform == 'twitter':
            content = self.generate_twitter_thread(research, topic)
        elif platform == 'reddit':
            subreddit = kwargs.get('subreddit', 'r/LocalLLaMA')
            content = self.generate_reddit_post(research, topic, subreddit)
        else:
            raise ValueError(f"Unknown platform: {platform}")
        
        # Step 3: Quality check
        print("[HERALD] Step 3: Quality control...")
        quality = self.check_quality(content)
        
        if quality['recommendation'] != 'APPROVE':
            print(f"[HERALD] Content rejected: {quality['concerns']}")
            return {"success": False, "reason": "Quality check failed", "details": quality}
        
        # Step 4: Sign content
        print("[HERALD] Step 4: Signing content...")
        signature = self.sign_content(content)
        
        # Step 5: Post
        print("[HERALD] Step 5: Posting...")
        if platform == 'twitter':
            result = self.post_to_twitter(content)
        elif platform == 'reddit':
            result = self.post_to_reddit(content)
        
        print(f"[HERALD] Pipeline complete: {result}")
        return result


# =========================================================================
# EXAMPLE USAGE
# =========================================================================

if __name__ == "__main__":
    # Initialize HERALD
    herald = HeraldAgent(config_path="herald_config.json")
    
    # Example 1: Post educational thread about agent identity
    herald.create_and_post(
        topic="cryptographic identity for AI agents",
        platform="twitter"
    )
    
    # Example 2: Post to Reddit about multi-agent systems
    herald.create_and_post(
        topic="building trustworthy multi-agent systems",
        platform="reddit",
        subreddit="r/LocalLLaMA"
    )
