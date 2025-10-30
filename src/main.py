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

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/betting_system.log'),
        logging.StreamHandler()
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

            self.logger.info(f"📊 Encontrados {len(matches)} jogos para análise")
            
            # Análise com IA
            opportunities = []
            for match in matches:
                try:
                    # Análise de diferentes mercados
                    over_under_opp = self.ai_engine.analyze_over_under(match)
                    btts_opp = self.ai_engine.analyze_both_teams_score(match)
                    corners_opp = self.ai_engine.analyze_corners(match)
                    
                    opportunities.extend([over_under_opp, btts_opp, corners_opp])
                    
                except Exception as e:
                    self.logger.error(f"❌ Erro analisando jogo {match.home_team} vs {match.away_team}: {e}")
                    continue

            # Gera bilhetes inteligentes
            tickets = self.ticket_generator.generate_tickets(opportunities)
            
            # Envia para Telegram
            await self.telegram_bot.send_smart_tickets(tickets)
            
            self.logger.info(f"✅ Análise concluída. Gerados {len(tickets)} bilhetes")

        except Exception as e:
            self.logger.error(f"❌ Erro na análise diária: {e}")
            await self.telegram_bot._send_message(f"❌ *Erro no sistema:* {str(e)}")

    async def run(self):
        """Executa o sistema continuamente"""
        self.logger.info("🤖 Sistema Profissional de Apostas Iniciado")
        
        # Executa análise imediatamente na primeira vez
        await self.run_daily_analysis()
        
        while True:
            try:
                # Verifica se é horário de análise (09:00 AM)
                now = datetime.now()
                if now.hour == 9 and now.minute == 0:
                    self.logger.info("⏰ Horário de análise - Executando...")
                    await self.run_daily_analysis()
                    await asyncio.sleep(60)  # Espera 1 minuto para evitar repetição
                else:
                    await asyncio.sleep(30)  # Verifica a cada 30 segundos
                    
            except Exception as e:
                self.logger.error(f"❌ Erro no loop principal: {e}")
                await asyncio.sleep(60)

async def main():
    system = ProfessionalBettingSystem()
    await system.run()

if __name__ == "__main__":
    # Cria diretório de logs se não existir
    os.makedirs('logs', exist_ok=True)
    asyncio.run(main())