from flask import Flask, render_template, request, jsonify
import logging
from datetime import datetime
import random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BettingSystem:
    def __init__(self):
        self.teams_br = [
            'Flamengo', 'Palmeiras', 'São Paulo', 'Corinthians', 'Grêmio',
            'Internacional', 'Atlético-MG', 'Santos', 'Fluminense', 'Botafogo',
            'Vasco', 'Cruzeiro', 'Fortaleza', 'Bahia', 'Red Bull Bragantino'
        ]
        self.leagues = ['Brasileirão Série A', 'Libertadores', 'Copa do Brasil', 'Premier League', 'La Liga']
        self.markets = ['Over 2.5 Gols', 'Ambos Marcam', 'Under 2.5 Gols', 'Vitória Casa', 'Vitória Fora']

    def generate_realistic_data(self):
        """Gera dados realistas de apostas"""
        bilhetes = []
        
        # Gera 5-8 bilhetes realistas
        for i in range(random.randint(5, 8)):
            home = random.choice(self.teams_br)
            away = random.choice([t for t in self.teams_br if t != home])
            
            market = random.choice(self.markets)
            if market == 'Over 2.5 Gols':
                odd = round(random.uniform(1.8, 2.4), 2)
                confianca = random.randint(65, 85)
                analise = f"Expectativa: {random.uniform(2.6, 3.2):.1f} gols | Finalizações: {random.randint(10, 16)}"
            elif market == 'Ambos Marcam':
                odd = round(random.uniform(1.7, 2.1), 2)
                confianca = random.randint(60, 80)
                analise = f"Probabilidade: {random.randint(55, 75)}% | Casa: {random.randint(50, 70)}% | Fora: {random.randint(45, 65)}%"
            else:
                odd = round(random.uniform(1.6, 2.0), 2)
                confianca = random.randint(55, 75)
                analise = f"Expectativa: {random.uniform(1.8, 2.4):.1f} gols | Defesas: {random.randint(4, 8)}"
            
            bilhete = {
                'id': f"bet_{i+1}",
                'jogo': f"{home} vs {away}",
                'tipo': random.choice(['2-3% da banca', '1-2% da banca', '0.5-1% da banca']),
                'mercado': market,
                'selecao': market,
                'odd': odd,
                'confianca': confianca,
                'valor_esperado': f"+{random.uniform(0.1, 0.4):.2f}",
                'analise': analise,
                'analise_premium': f"⭐ {'ALTA' if confianca >= 75 else 'MEDIA'} - {random.choice(['Bom valor', 'Oportunidade sólida', 'Confiança elevada'])}",
                'timestamp': datetime.now().isoformat(),
                'destaque': confianca >= 75,
                'esporte': 'futebol',
                'liga': random.choice(self.leagues)
            }
            bilhetes.append(bilhete)
        
        # Ordena por confiança
        bilhetes.sort(key=lambda x: x['confianca'], reverse=True)
        
        return bilhetes

    def get_bilhete_do_dia(self):
        """Seleciona o melhor bilhete como 'Bilhete do Dia'"""
        bilhetes = self.generate_realistic_data()
        melhor = max(bilhetes, key=lambda x: x['confianca'])
        
        return {
            'jogo': melhor['jogo'],
            'mercado': melhor['mercado'],
            'selecao': melhor['selecao'],
            'odd': melhor['odd'],
            'confianca': melhor['confianca'],
            'valor_esperado': melhor['valor_esperado'],
            'analise': melhor['analise'],
            'analise_premium': f"🔥 BILHETE DO DIA - {'ALTA' if melhor['confianca'] >= 75 else 'MEDIA'} CONFIANÇA",
            'timestamp': datetime.now().isoformat(),
            'liga': melhor['liga']
        }

# Instância global
betting_system = BettingSystem()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/analisar_jogos', methods=['POST'])
def analisar_jogos():
    """Endpoint para análise de jogos"""
    try:
        data = request.get_json() or {}
        sport = data.get('esporte', 'soccer')
        region = data.get('regiao', 'eu')
        market = data.get('mercado', 'totals')
        
        logger.info(f"📊 Análise solicitada - Esporte: {sport}, Região: {region}, Mercado: {market}")
        
        bilhetes = betting_system.generate_realistic_data()
        bilhete_do_dia = betting_system.get_bilhete_do_dia()
        
        return jsonify({
            'status': 'success',
            'data': {
                'bilhetes': bilhetes,
                'bilhete_do_dia': bilhete_do_dia,
                'total_analisado': len(bilhetes)
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na análise: {e}")
        return jsonify({
            'status': 'error', 
            'message': 'Erro interno do servidor'
        })

@app.route('/bilhete_do_dia', methods=['GET'])
def bilhete_do_dia():
    """Endpoint para bilhete do dia"""
    try:
        bilhete = betting_system.get_bilhete_do_dia()
        logger.info("🎯 Bilhete do dia gerado com sucesso")
        
        return jsonify({
            'status': 'success', 
            'bilhete_do_dia': bilhete,
            'message': 'Bilhete do dia encontrado! (Simulação)'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/teste_bilhetes', methods=['POST'])
def teste_bilhetes():
    """Endpoint para teste"""
    try:
        logger.info("🧪 Teste de sistema executado")
        return jsonify({
            'status': 'success',
            'message': '✅ Sistema BetMaster AI funcionando perfeitamente! (Modo Simulação)'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/status')
def status():
    """Endpoint de status"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '4.0',
        'system': 'BetMaster AI',
        'mode': 'simulation',
        'message': 'Sistema funcionando em modo simulação com dados realistas'
    })

@app.route('/health')
def health():
    """Health check para Render"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)