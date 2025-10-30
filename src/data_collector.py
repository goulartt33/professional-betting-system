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
        """Busca jogos do dia atual"""
        try:
            today = pd.Timestamp.now().strftime('%Y-%m-%d')
            async with self.session.get(
                f"{self.config.FOOTBALL_API_URL}/matches",
                params={'dateFrom': today, 'dateTo': today}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._process_matches_data(data.get('matches', []))
                else:
                    self.logger.error(f"API Error: {response.status}")
                    return []
        except Exception as e:
            self.logger.error(f"Error fetching today's matches: {e}")
            return []

    async def get_team_statistics(self, team_id: int, season: int = 2024) -> Optional[TeamStats]:
        """Busca estatísticas detalhadas do time"""
        try:
            # Simulação de dados - substitua com API real
            return self._simulate_team_stats(team_id, f"Team_{team_id}")
        except Exception as e:
            self.logger.error(f"Error fetching team stats {team_id}: {e}")
            return None

    def _simulate_team_stats(self, team_id: int, team_name: str) -> TeamStats:
        """Simula estatísticas do time para demonstração"""
        import random
        return TeamStats(
            team_id=team_id,
            team_name=team_name,
            matches_played=random.randint(20, 38),
            avg_goals_scored=round(random.uniform(1.0, 2.5), 2),
            avg_goals_conceded=round(random.uniform(0.8, 2.2), 2),
            avg_shots=round(random.uniform(8.0, 15.0), 1),
            avg_shots_on_target=round(random.uniform(3.0, 7.0), 1),
            avg_corners=round(random.uniform(4.0, 8.0), 1),
            possession_avg=round(random.uniform(40.0, 65.0), 1),
            btgs_percentage=round(random.uniform(40.0, 70.0), 1)
        )

    async def _process_matches_data(self, matches: List[Dict]) -> List[MatchData]:
        """Processa dados dos jogos"""
        processed_matches = []
        
        for match in matches:
            try:
                home_team = match.get('homeTeam', {})
                away_team = match.get('awayTeam', {})
                
                if not home_team or not away_team:
                    continue

                home_team_id = home_team.get('id', 1)
                away_team_id = away_team.get('id', 2)
                home_team_name = home_team.get('name', 'Home Team')
                away_team_name = away_team.get('name', 'Away Team')

                # Busca estatísticas dos times
                home_stats = await self.get_team_statistics(home_team_id)
                away_stats = await self.get_team_statistics(away_team_id)

                if home_stats and away_stats:
                    match_data = MatchData(
                        match_id=match.get('id', 0),
                        home_team=home_team_name,
                        away_team=away_team_name,
                        league=match.get('competition', {}).get('name', 'Unknown League'),
                        date=pd.to_datetime(match.get('utcDate', pd.Timestamp.now())),
                        home_stats=home_stats,
                        away_stats=away_stats,
                        historical_meetings=[]
                    )
                    processed_matches.append(match_data)

            except Exception as e:
                self.logger.error(f"Error processing match: {e}")
                continue

        return processed_matches