from flask import Flask, render_template, request, jsonify
import asyncio
import logging
import json
from datetime import datetime
from data_collector import ProfessionalDataCollector
from ai_engine import AIBettingEngine
from ticket_generator import SmartTicketGenerator
from telegram_bot import ProfessionalTelegramBot
from config import APIConfig, AnalysisConfig

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebBettingSystem:
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

    async def analyze_matches(self, sport='soccer', region='eu', market='totals'):
        """Analisa jogos e gera bilhetes"""
        try:
            # Coleta dados
            async with self.data_collector as collector:
                matches = await collector.get_matches_today()
                
            if not matches:
                return {'status': 'error', 'message': 'Nenhum jogo encontrado'}

            # Análise com IA
            opportunities = []
            for match in matches:
                try:
                    over_under_opp = self.ai_engine.analyze_over_under(match)
                    btts_opp = self.ai_engine.analyze_both_teams_score(match)
                    corners_opp = self.ai_engine.analyze_corners(match)
                    
                    opportunities.extend([over_under_opp, btts_opp, corners_opp])
                    
                except Exception as e:
                    logger.error(f"Erro analisando jogo: {e}")
                    continue

            # Gera bilhetes inteligentes
            tickets = self.ticket_generator.generate_tickets(opportunities)
            
            # Converte para formato web
            web_bilhetes = self._format_tickets_for_web(tickets)
            bilhete_do_dia = self._get_bilhete_do_dia(tickets)
            
            return {
                'status': 'success',
                'data': {
                    'bilhetes': web_bilhetes,
                    'bilhete_do_dia': bilhete_do_dia,
                    'total_analisado': len(matches)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            return {'status': 'error', 'message': str(e)}

    def _format_tickets_for_web(self, tickets):
        """Formata bilhetes para o formato web"""
        web_bilhetes = []
        
        for ticket in tickets:
            for opp in ticket.opportunities:
                bilhete_web = {
                    'id': f"{ticket.ticket_id}_{opp.market_type.value}",
                    'jogo': f"{opp.match.home_team} vs {opp.match.away_team}",
                    'tipo': ticket.stake_recommendation,
                    'mercado': opp.prediction,
                    'selecao': opp.prediction,
                    'odd': opp.odds,
                    'confianca': int(ticket.confidence_score * 100),
                    'valor_esperado': f"{opp.expected_value:+.2f}",
                    'analise': opp.reasoning,
                    'analise_premium': f"⭐ {opp.confidence.value} - {ticket.stake_recommendation}",
                    'timestamp': datetime.now().isoformat(),
                    'destaque': ticket.confidence_score >= 0.8,
                    'esporte': 'futebol',
                    'liga': opp.match.league
                }
                web_bilhetes.append(bilhete_web)
        
        return web_bilhetes

    def _get_bilhete_do_dia(self, tickets):
        """Seleciona o melhor bilhete do dia"""
        if not tickets:
            return None
            
        # Encontra o bilhete com maior confiança
        melhor_ticket = max(tickets, key=lambda x: x.confidence_score)
        if melhor_ticket.confidence_score >= 0.7:
            opp = melhor_ticket.opportunities[0]
            return {
                'jogo': f"{opp.match.home_team} vs {opp.match.away_team}",
                'mercado': opp.prediction,
                'selecao': opp.prediction,
                'odd': opp.odds,
                'confianca': int(melhor_ticket.confidence_score * 100),
                'valor_esperado': f"{opp.expected_value:+.2f}",
                'analise': opp.reasoning,
                'analise_premium': f"🔥 BILHETE DO DIA - {opp.confidence.value}",
                'timestamp': datetime.now().isoformat()
            }
        return None

    async def send_bilhete_do_dia_telegram(self):
        """Envia bilhete do dia para o Telegram"""
        try:
            result = await self.analyze_matches()
            if result['status'] == 'success' and result['data']['bilhete_do_dia']:
                bilhete = result['data']['bilhete_do_dia']
                
                # Formata mensagem para Telegram
                mensagem = f"""
🎯 *BILHETE DO DIA* 🎯

*{bilhete['jogo']}*
🏆 {bilhete.get('liga', 'Futebol')}
🎲 *Mercado:* {bilhete['mercado']}
💰 *Odd:* {bilhete['odd']:.2f}
📊 *Confiança:* {bilhete['confianca']}%
📈 *Valor Esperado:* {bilhete['valor_esperado']}

💡 *Análise:*
{bilhete['analise']}

⏰ *Gerado em:* {datetime.now().strftime('%d/%m/%Y %H:%M')}

🔥 *Oportunidade do Dia!*
                """
                
                await self.telegram_bot._send_message(mensagem)
                return {'status': 'success', 'message': 'Bilhete do dia enviado!'}
            else:
                return {'status': 'error', 'message': 'Nenhum bilhete digno do dia encontrado'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

# Instância global do sistema
betting_system = WebBettingSystem()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/analisar_jogos', methods=['POST'])
async def analisar_jogos():
    """Endpoint para análise de jogos"""
    try:
        data = request.get_json()
        sport = data.get('esporte', 'soccer')
        region = data.get('regiao', 'eu')
        market = data.get('mercado', 'totals')
        
        result = await betting_system.analyze_matches(sport, region, market)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/bilhete_do_dia', methods=['GET'])
async def bilhete_do_dia():
    """Endpoint para buscar bilhete do dia"""
    try:
        result = await betting_system.send_bilhete_do_dia_telegram()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/teste_bilhetes', methods=['POST'])
async def teste_bilhetes():
    """Endpoint para teste no Telegram"""
    try:
        # Gera bilhetes de teste
        result = await betting_system.analyze_matches()
        
        if result['status'] == 'success':
            mensagem = "🧪 *TESTE DO SISTEMA*\n\nSistema BetMaster AI funcionando perfeitamente!\n\n"
            mensagem += f"📊 {len(result['data']['bilhetes'])} bilhetes gerados\n"
            mensagem += f"⭐ {len([b for b in result['data']['bilhetes'] if b['confianca'] >= 75])} alta confiança\n"
            mensagem += f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            await betting_system.telegram_bot._send_message(mensagem)
            return jsonify({'status': 'success', 'message': 'Teste enviado com sucesso!'})
        else:
            return jsonify({'status': 'error', 'message': result['message']})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/status')
def status():
    """Endpoint de status do sistema"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '4.0',
        'system': 'BetMaster AI'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)