import asyncio
import logging
from typing import List
from models import SmartTicket

class ProfessionalTelegramBot:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.logger = logging.getLogger(__name__)

    async def send_smart_tickets(self, tickets: List[SmartTicket]):
        """Envia bilhetes inteligentes para o Telegram"""
        if not tickets:
            await self._send_message("⚠️ *Nenhuma oportunidade identificada hoje*")
            return

        for ticket in tickets:
            message = self._format_ticket_message(ticket)
            await self._send_message(message)
            await asyncio.sleep(1)  # Rate limiting

    async def _send_message(self, text: str):
        """Envia mensagem para o chat configurado"""
        try:
            # Simulação de envio - implemente com biblioteca Telegram real
            self.logger.info(f"📤 Telegram Message:\n{text}")
            print(f"📤 Telegram Message:\n{text}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem: {e}")
            return False

    def _format_ticket_message(self, ticket: SmartTicket) -> str:
        """Formata bilhete para mensagem do Telegram"""
        message = f"""
🎯 *BILHETE {ticket.ticket_id}* 🎯
*Estratégia: {ticket.stake_recommendation}*
*Confiança: {ticket.confidence_score:.0%}*
*Odd Total: {ticket.total_odds:.2f}*

"""

        for i, opp in enumerate(ticket.opportunities, 1):
            message += f"""
*{i}. {opp.match.home_team} vs {opp.match.away_team}*
🏆 {opp.match.league}
🎲 *Mercado:* {opp.prediction}
📊 *Confiança:* {opp.confidence.value}
💰 *Odd:* {opp.odds:.2f}
📈 *Valor Esperado:* {opp.expected_value:+.2f}
💡 *Análise:* {opp.reasoning}
"""

        message += f"""
💡 *Recomendação de Stake:* {ticket.stake_recommendation}
⏰ *Gerado em:* {ticket.created_at.strftime('%d/%m/%Y %H:%M')}

⚠️ *Aposte com responsabilidade*
        """

        return message