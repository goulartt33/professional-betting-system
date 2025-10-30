from typing import List, Dict
import uuid
from datetime import datetime
from models import BettingOpportunity, SmartTicket, ConfidenceLevel
import numpy as np
import logging

class SmartTicketGenerator:
    def __init__(self, max_tickets: int = 5, min_confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM):
        self.max_tickets = max_tickets
        self.min_confidence = min_confidence
        self.logger = logging.getLogger(__name__)

    def generate_tickets(self, opportunities: List[BettingOpportunity]) -> List[SmartTicket]:
        """Gera bilhetes inteligentes baseados nas oportunidades"""
        # Filtra oportunidades por confiança mínima
        valid_opportunities = [
            opp for opp in opportunities 
            if self._get_confidence_value(opp.confidence) >= self._get_confidence_value(self.min_confidence)
            and opp.expected_value > -0.1
        ]

        if not valid_opportunities:
            self.logger.info("No valid opportunities found for ticket generation")
            return []

        # Ordena por valor esperado
        valid_opportunities.sort(key=lambda x: x.expected_value, reverse=True)

        tickets = []
        
        # Bilhete Conservador (Alta Confiança)
        conservative_opps = [opp for opp in valid_opportunities 
                           if opp.confidence in [ConfidenceLevel.VERY_HIGH, ConfidenceLevel.HIGH]]
        if len(conservative_opps) >= 2:
            tickets.append(self._create_ticket(conservative_opps[:3], "CONSERVADOR"))

        # Bilhete Balanceado
        if len(valid_opportunities) >= 3:
            balanced_opps = valid_opportunities[:4]
            tickets.append(self._create_ticket(balanced_opps, "BALANCEADO"))

        # Bilhete de Valor (Melhor EV)
        value_opps = [opp for opp in valid_opportunities if opp.expected_value > 0.1]
        if value_opps:
            tickets.append(self._create_ticket(value_opps[:4], "VALOR"))

        return tickets[:self.max_tickets]

    def _create_ticket(self, opportunities: List[BettingOpportunity], strategy: str) -> SmartTicket:
        """Cria um bilhete específico"""
        total_odds = np.prod([opp.odds for opp in opportunities])
        confidence_score = np.mean([self._get_confidence_value(opp.confidence) for opp in opportunities])
        
        # Recomendação de stake baseada na estratégia e confiança
        if strategy == "CONSERVADOR" and confidence_score >= 0.8:
            stake = "2-3% da banca"
        elif strategy == "BALANCEADO" and confidence_score >= 0.7:
            stake = "1-2% da banca"
        else:
            stake = "0.5-1% da banca"

        return SmartTicket(
            ticket_id=str(uuid.uuid4())[:8].upper(),
            opportunities=opportunities,
            total_odds=round(total_odds, 2),
            confidence_score=round(confidence_score, 2),
            stake_recommendation=stake,
            created_at=datetime.now()
        )

    def _get_confidence_value(self, confidence: ConfidenceLevel) -> float:
        """Converte nível de confiança para valor numérico"""
        confidence_map = {
            ConfidenceLevel.VERY_HIGH: 0.9,
            ConfidenceLevel.HIGH: 0.75,
            ConfidenceLevel.MEDIUM: 0.6,
            ConfidenceLevel.LOW: 0.4
        }
        return confidence_map.get(confidence, 0.5)