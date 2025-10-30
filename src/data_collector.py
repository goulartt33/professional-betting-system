import aiohttp
import asyncio
import pandas as pd
from typing import List, Dict, Optional
import logging
from models import MatchData, TeamStats
from config import APIConfig

class ProfessionalDataCollector:
    def __init__(self, config: APIConfig):
        self.config = config
        self.headers = {'X-Auth-Token': config.FOOTBALL_API_KEY}
        self.session = None
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def get_matches_today(self) -> List[MatchData]:
        """Busca jogos do dia atual usando API gratuita"""
        try:
            today = pd.Timestamp.now().strftime('%Y-%m-%d')
            
            # Tenta primeiro a API Football Data
            matches = await self._get_football_data_matches(today)
            
            # Se não encontrar jogos, usa dados simulados
            if not matches:
                matches = await self._get_simulated_matches()
                
            return matches
            
        except Exception as e:
            self.logger.error(f"Error fetching matches: {e}")
            return await self._get_simulated_matches()

    async def _get_football_data_matches(self, date: str) -> List[MatchData]:
        """Busca jogos da API Football Data"""
        try:
            async with self.session.get(
                f"{self.config.FOOTBALL_API_URL}/matches",
                params={'dateFrom': date, 'dateTo': date, 'limit': 20}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._process_matches_data(data.get('matches', []))
                else:
                    self.logger.warning(f"Football Data API returned {response.status}")
                    return []
        except Exception as e:
            self.logger.error(f"Football Data API error: {e}")
            return []

    async def _get_simulated_matches(self) -> List[MatchData]:
        """Gera dados simulados quando API não está disponível"""
        self.logger.info("Using simulated data for demonstration")
        
        simulated_matches = [
            {
                'home_team': 'Flamengo', 'away_team': 'Palmeiras',
                'league': 'Brasileirão Série A', 'date': pd.Timestamp.now()
            },
            {
                'home_team': 'São Paulo', 'away_team': 'Corinthians', 
                'league': 'Brasileirão Série A', 'date': pd.Timestamp.now()
            },
            {
                'home_team': 'Real Madrid', 'away_team': 'Barcelona',
                'league': 'La Liga', 'date': pd.Timestamp.now()
            }
        ]
        
        matches = []
        for match_data in simulated_matches:
            match = MatchData(
                match_id=hash(f"{match_data['home_team']}_{match_data['away_team']}"),
                home_team=match_data['home_team'],
                away_team=match_data['away_team'],
                league=match_data['league'],
                date=match_data['date'],
                home_stats=self._create_simulated_stats(match_data['home_team'], is_home=True),
                away_stats=self._create_simulated_stats(match_data['away_team'], is_home=False),
                historical_meetings=[]
            )
            matches.append(match)
            
        return matches

    def _create_simulated_stats(self, team_name: str, is_home: bool) -> TeamStats:
        """Cria estatísticas realistas simuladas"""
        import random
        
        # Times brasileiros tendem a ter mais gols em casa
        if 'Flamengo' in team_name or 'Palmeiras' in team_name or 'São Paulo' in team_name:
            avg_goals = random.uniform(1.5, 2.2) if is_home else random.uniform(1.2, 1.8)
            avg_shots = random.uniform(12, 16) if is_home else random.uniform(10, 14)
        else:
            avg_goals = random.uniform(1.3, 2.0) if is_home else random.uniform(1.0, 1.6)
            avg_shots = random.uniform(10, 14) if is_home else random.uniform(8, 12)
            
        return TeamStats(
            team_id=hash(team_name),
            team_name=team_name,
            matches_played=random.randint(15, 30),
            avg_goals_scored=round(avg_goals, 2),
            avg_goals_conceded=round(random.uniform(0.8, 1.5), 2),
            avg_shots=round(avg_shots, 1),
            avg_shots_on_target=round(avg_shots * 0.35, 1),
            avg_corners=round(random.uniform(4.5, 7.5), 1),
            possession_avg=round(random.uniform(45.0, 60.0), 1),
            btgs_percentage=round(random.uniform(45.0, 65.0), 1)
        )

    async def get_real_odds(self, match: MatchData) -> Dict:
        """Busca odds reais da The Odds API"""
        try:
            async with self.session.get(
                f"{self.config.THE_ODDS_API_URL}/sports/upcoming/odds",
                params={
                    'apiKey': self.config.THE_ODDS_API_KEY,
                    'regions': 'eu',
                    'markets': 'h2h,totals',
                    'oddsFormat': 'decimal'
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._find_match_odds(data, match)
                return {}
        except Exception as e:
            self.logger.error(f"Error fetching odds: {e}")
            return {}

    def _find_match_odds(self, odds_data: List, match: MatchData) -> Dict:
        """Encontra odds para o jogo específico"""
        for event in odds_data:
            if (match.home_team.lower() in event['home_team'].lower() and 
                match.away_team.lower() in event['away_team'].lower()):
                return event
        return {}