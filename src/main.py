import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

from config import APIConfig, AnalysisConfig
from data_collector import ProfessionalDataCollector
from ai_engine import AIBettingEngine
from ticket_generator import SmartTicketGenerator
from telegram_bot import ProfessionalTelegramBot

# Configuração de logging para Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Para Render logs
    ]
)

class ProfessionalBettingSystem:
    def __init__(self):
        self.config = APIConfig()
        self.analysis_config = AnalysisConfig()
        self.data_collector = ProfessionalDataCollector(self.config)
        self.ai_engine = AIBettingEngine()
        self.ticket_generator = SmartTicketGenerator()
        self.telegram_bot = ProfessionalTelegramBot(
            self.config.TELEGRAM_BOT_TOKEN,
            self.config.TELEGRAM_CHAT_ID
        )
        self.logger = logging.getLogger(__name__)

    async def run_daily_analysis(self):
        """Executa análise diária completa"""
        self.logger.info("🚀 Iniciando análise diária...")
        
        try:
            # Coleta dados
            async with self.data_collector as collector:
                matches = await collector.get_matches_today()
                
            if not matches:
                self.logger.warning("⚠️ Nenhum jogo encontrado para hoje")
                await self.telegram_bot._send_message("⚠️ *Nenhum jogo encontrado para análise hoje*")
                return

            self.logger.info(f"📊 Analisando {len(matches)} jogos...")
            
            # Análise com IA
            opportunities = []
            for match in matches:
                try:
                    over_under_opp = self.ai_engine.analyze_over_under(match)
                    btts_opp = self.ai_engine.analyze_both_teams_score(match)
                    corners_opp = self.ai_engine.analyze_corners(match)
                    
                    opportunities.extend([over_under_opp, btts_opp, corners_opp])
                    
                except Exception as e:
                    self.logger.error(f"❌ Erro analisando {match.home_team} vs {match.away_team}: {e}")
                    continue

            # Gera bilhetes inteligentes
            tickets = self.ticket_generator.generate_tickets(opportunities)
            
            # Envia para Telegram
            await self.telegram_bot.send_smart_tickets(tickets)
            
            self.logger.info(f"✅ Análise concluída. Gerados {len(tickets)} bilhetes")

        except Exception as e:
            self.logger.error(f"❌ Erro na análise diária: {e}")
            await self.telegram_bot._send_message(f"❌ *Erro no sistema:* {str(e)}")

    async def run_once(self):
        """Executa uma única análise (para Render)"""
        await self.run_daily_analysis()

async def main():
    system = ProfessionalBettingSystem()
    await system.run_once()

if __name__ == "__main__":
    # Para Render - executa uma vez e sai
    asyncio.run(main())