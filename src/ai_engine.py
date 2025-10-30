import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple
import logging
from models import MatchData, BettingOpportunity, MarketType, ConfidenceLevel

class AIBettingEngine:
    def __init__(self):
        self.scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)

    def calculate_confidence(self, probability: float) -> ConfidenceLevel:
        """Calcula nível de confiança baseado na probabilidade"""
        if probability >= 0.80:
            return ConfidenceLevel.VERY_HIGH
        elif probability >= 0.70:
            return ConfidenceLevel.HIGH
        elif probability >= 0.60:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def analyze_over_under(self, match: MatchData) -> BettingOpportunity:
        """Analisa mercado Over/Under"""
        try:
            total_goals_expected = match.home_stats.avg_goals_scored + match.away_stats.avg_goals_conceded
            
            # Fatores de ponderação
            goal_factor = total_goals_expected / 2.5
            shots_factor = (match.home_stats.avg_shots_on_target + match.away_stats.avg_shots_on_target) / 6
            btgs_factor = (match.home_stats.btgs_percentage + match.away_stats.btgs_percentage) / 200
            
            probability = min(0.95, (goal_factor * 0.5 + shots_factor * 0.3 + btgs_factor * 0.2))
            
            if total_goals_expected >= 2.8 and probability >= 0.65:
                prediction = "Over 2.5"
                odds = max(1.5, 3.0 - (total_goals_expected - 2.5) * 0.3)
            else:
                prediction = "Under 2.5"
                odds = max(1.3, 1.0 + (2.5 - total_goals_expected) * 0.5)

            return BettingOpportunity(
                match=match,
                market_type=MarketType.OVER_UNDER,
                prediction=prediction,
                confidence=self.calculate_confidence(probability),
                odds=round(odds, 2),
                reasoning=f"Expectativa: {total_goals_expected:.2f} gols | Finalizações: {(match.home_stats.avg_shots_on_target + match.away_stats.avg_shots_on_target):.1f}",
                expected_value=probability * odds - 1
            )
        except Exception as e:
            self.logger.error(f"Erro na análise Over/Under: {e}")
            raise

    def analyze_both_teams_score(self, match: MatchData) -> BettingOpportunity:
        """Analisa mercado Ambos Marcam"""
        try:
            home_btgs = match.home_stats.btgs_percentage / 100
            away_btgs = match.away_stats.btgs_percentage / 100
            
            probability = (home_btgs * 0.6 + away_btgs * 0.4)
            
            if probability >= 0.60:
                prediction = "Ambos Marcam - Sim"
                odds = max(1.6, 2.5 - (probability - 0.5) * 2)
            else:
                prediction = "Ambos Marcam - Não"
                odds = max(1.4, 1.0 + (0.5 - probability) * 1.5)

            return BettingOpportunity(
                match=match,
                market_type=MarketType.BOTH_TEAMS_SCORE,
                prediction=prediction,
                confidence=self.calculate_confidence(probability),
                odds=round(odds, 2),
                reasoning=f"Probabilidade: {probability:.2%} | Casa: {home_btgs:.2%} | Fora: {away_btgs:.2%}",
                expected_value=probability * odds - 1
            )
        except Exception as e:
            self.logger.error(f"Erro na análise BTTS: {e}")
            raise

    def analyze_corners(self, match: MatchData) -> BettingOpportunity:
        """Analisa mercado de Escanteios"""
        try:
            total_corners_expected = match.home_stats.avg_corners + match.away_stats.avg_corners
            
            if total_corners_expected >= 9:
                prediction = "Over 8.5 Escanteios"
                probability = min(0.9, total_corners_expected / 10)
                odds = max(1.5, 2.2 - (total_corners_expected - 8.5) * 0.2)
            else:
                prediction = "Under 8.5 Escanteios"
                probability = min(0.9, (8.5 - total_corners_expected) / 5)
                odds = max(1.3, 1.0 + (8.5 - total_corners_expected) * 0.3)

            return BettingOpportunity(
                match=match,
                market_type=MarketType.CORNER_KICKS,
                prediction=prediction,
                confidence=self.calculate_confidence(probability),
                odds=round(odds, 2),
                reasoning=f"Expectativa: {total_corners_expected:.1f} escanteios | Casa: {match.home_stats.avg_corners:.1f} | Fora: {match.away_stats.avg_corners:.1f}",
                expected_value=probability * odds - 1
            )
        except Exception as e:
            self.logger.error(f"Erro na análise de escanteios: {e}")
            raise