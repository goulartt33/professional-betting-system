from flask import Flask, render_template, request, jsonify 
from datetime import datetime 
import random 
 
app = Flask(__name__) 
 
class BettingSystem: 
    def __init__(self): 
        self.teams_br = ['Flamengo', 'Palmeiras', 'Sao Paulo', 'Corinthians', 'Gremio'] 
        self.leagues = ['Brasileirao Serie A', 'Libertadores', 'Premier League'] 
        self.markets = ['Over 2.5 Gols', 'Ambos Marcam', 'Under 2.5 Gols'] 
 
    def generate_data(self): 
        bilhetes = [] 
        for i in range(6): 
            home = random.choice(self.teams_br) 
            away = random.choice([t for t in self.teams_br if t != home]) 
 
            market = random.choice(self.markets) 
            if market == 'Over 2.5 Gols': 
                odd = round(random.uniform(1.8, 2.4), 2) 
                confianca = random.randint(65, 85) 
                analise = f"Expectativa: {random.uniform(2.6, 3.2):.1f} gols" 
            else: 
                odd = round(random.uniform(1.7, 2.1), 2) 
                confianca = random.randint(60, 80) 
                analise = f"Probabilidade: {random.randint(55, 75)}%%" 
 
            bilhete = { 
                'id': f"bet_{i+1}", 
                'jogo': f"{home} vs {away}", 
                'tipo': '1-2%% da banca', 
                'mercado': market, 
                'selecao': market, 
                'odd': odd, 
                'confianca': confianca, 
                'valor_esperado': f"+{random.uniform(0.1, 0.4):.2f}", 
                'analise': analise, 
                'analise_premium': f"? {'ALTA' if confianca >= 75 else 'MEDIA'}", 
                'timestamp': datetime.now().isoformat(), 
                'destaque': confianca 
                'esporte': 'futebol', 
                'liga': random.choice(self.leagues) 
            } 
            bilhetes.append(bilhete) 
 
        bilhetes.sort(key=lambda x: x['confianca'], reverse=True) 
        return bilhetes 
 
betting_system = BettingSystem() 
 
@app.route('/') 
def index(): 
    return render_template('index.html') 
 
@app.route('/analisar_jogos', methods=['POST']) 
def analisar_jogos(): 
    bilhetes = betting_system.generate_data() 
    bilhete_do_dia = max(bilhetes, key=lambda x: x['confianca']) 
 
    return jsonify({ 
        'status': 'success', 
        'data': { 
            'bilhetes': bilhetes, 
            'bilhete_do_dia': bilhete_do_dia, 
            'total_analisado': len(bilhetes) 
        } 
    }) 
 
@app.route('/bilhete_do_dia', methods=['GET']) 
def bilhete_do_dia(): 
    bilhetes = betting_system.generate_data() 
    bilhete = max(bilhetes, key=lambda x: x['confianca']) 
 
    return jsonify({ 
        'status': 'success', 
        'bilhete_do_dia': bilhete, 
        'message': 'Bilhete do dia encontrado!' 
    }) 
 
@app.route('/teste_bilhetes', methods=['POST']) 
def teste_bilhetes(): 
    return jsonify({ 
        'status': 'success', 
        'message': '? Sistema funcionando!' 
    }) 
 
@app.route('/status') 
def status(): 
    return jsonify({'status': 'online', 'system': 'BetMaster AI'}) 
 
if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000, debug=False) 
