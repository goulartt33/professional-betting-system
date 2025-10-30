import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class APIConfig:
    # Football Data API (sua chave)
    FOOTBALL_API_KEY: str = os.getenv('FOOTBALL_API_KEY', '0b9721f26cfd44d188b5630223a1d1ac')
    FOOTBALL_API_URL: str = "https://api.football-data.org/v4"
    
    # The Odds API (sua chave)
    THE_ODDS_API_KEY: str = os.getenv('THE_ODDS_API_KEY', '4a627e98c2fadda0bb5722841fb5dc35')
    THE_ODDS_API_URL: str = "https://api.the-odds-api.com/v4"
    
    # Telegram (sua configuração)
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '8318020293:AAGgOHxsvCUQ4o0ArxKAevIe3KlL5DeWbwI')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '5538926378')

@dataclass
class AnalysisConfig:
    MIN_MATCHES_ANALYSIS: int = 5
    CONFIDENCE_THRESHOLD: float = 0.70
    OVER_25_GOAL_THRESHOLD: float = 2.5
    HIGH_SHOTS_THRESHOLD: int = 10
    RISKY_ODD_LIMIT: float = 3.0
    MAX_TICKETS_PER_DAY: int = 3