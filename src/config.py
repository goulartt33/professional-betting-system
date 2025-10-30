import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class APIConfig:
    FOOTBALL_API_KEY: str = os.getenv('FOOTBALL_API_KEY', 'your_football_api_key_here')
    FOOTBALL_API_URL: str = "https://api.football-data.org/v4"
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', 'your_telegram_bot_token')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', 'your_telegram_chat_id')

@dataclass
class AnalysisConfig:
    MIN_MATCHES_ANALYSIS: int = 10
    CONFIDENCE_THRESHOLD: float = 0.75
    OVER_25_GOAL_THRESHOLD: float = 2.8
    HIGH_SHOTS_THRESHOLD: int = 12
    RISKY_ODD_LIMIT: float = 3.0
    MAX_TICKETS_PER_DAY: int = 5