from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

class MarketType(Enum):
    OVER_UNDER = "over_under"
    BOTH_TEAMS_SCORE = "both_teams_score"
    CORNER_KICKS = "corner_kicks"
    SHOTS_ON_TARGET = "shots_on_target"

class ConfidenceLevel(Enum):
    VERY_HIGH = "MUITO_ALTA"
    HIGH = "ALTA"
    MEDIUM = "MEDIA"
    LOW = "BAIXA"

@dataclass
class TeamStats:
    team_id: int
    team_name: str
    matches_played: int
    avg_goals_scored: float
    avg_goals_conceded: float
    avg_shots: float
    avg_shots_on_target: float
    avg_corners: float
    possession_avg: float
    btgs_percentage: float

@dataclass
class MatchData:
    match_id: int
    home_team: str
    away_team: str
    league: str
    date: datetime
    home_stats: TeamStats
    away_stats: TeamStats
    historical_meetings: List[Dict]

@dataclass
class BettingOpportunity:
    match: MatchData
    market_type: MarketType
    prediction: str
    confidence: ConfidenceLevel
    odds: float
    reasoning: str
    expected_value: float

@dataclass
class SmartTicket:
    ticket_id: str
    opportunities: List[BettingOpportunity]
    total_odds: float
    confidence_score: float
    stake_recommendation: str
    created_at: datetime