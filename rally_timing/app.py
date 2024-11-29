from datetime import datetime
from fpdf import FPDF
from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)

DATA_FILE = 'data/reg.json'

# Função para garantir que o arquivo de dados existe
def ensure_data_file():
    if not os.path.exists('data/reg.json'):
        with open('data/reg.json', 'w') as file:
            json.dump({}, file)  # Cria o arquivo com um dicionário vazio


def create_initial_data():
    # Função para criar dados iniciais caso o arquivo esteja vazio ou corrompido
    return {}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as file:
                data = json.load(file)
                print(f"Dados carregados: {data}")  # Debug: mostra os dados carregados
                return data
        except json.JSONDecodeError:
            print(f"Erro ao decodificar o arquivo {DATA_FILE}. Criando um novo arquivo.")
            return create_initial_data()
    else:
        print(f"Arquivo {DATA_FILE} não encontrado. Criando um novo arquivo.")
        return create_initial_data()

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4)
            print(f"Dados salvos: {data}")  # Debug: imprime os dados que estão sendo salvos
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add', methods=['POST'])
def add_record():
    # Carregar os dados atuais
    data = load_data()
    print(f"Dados carregados antes da adição: {data}")  # Log para depuração

    try:
        # Verifique se a requisição contém dados JSON
        if not request.is_json:
            return jsonify({"error": "A requisição deve ser no formato JSON."}), 400

        # Captura os dados enviados
        numero = request.json.get('numero')
        chegada = request.json.get('chegada')
        partida = request.json.get('partida', None)
        manga = request.json.get('manga', 'manga_1')  # Valor padrão para manga

        print(f"Recebido: {request.json}")  # Log para depuração

        # Verifica se todos os campos necessários estão presentes
        if not numero or not chegada:
            return jsonify({"error": "Campos 'numero' e 'chegada' são obrigatórios."}), 400

        # Verifica se a manga existe no dicionário, se não cria uma nova
        if manga not in data:
            data[manga] = {"geral": [], "classes": {}}

        # Adiciona o novo registro aos dados
        data[manga]["geral"].append({
            "numero": numero,
            "chegada": chegada,
            "partida": partida
        })

        print(f"Dados após adição: {data}")  # Log para depuração

        # Salva os dados no arquivo
        save_data(data)

        return jsonify({"message": "Registro adicionado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": f"Ocorreu um erro: {str(e)}"}), 500

# Rota para obter todos os registos
@app.route('/api/registos', methods=['GET'])
def get_records():
    ensure_data_file()
    data = load_data()
    return jsonify(data)

# Rota para exportar os registos para PDF
@app.route('/api/export/pdf', methods=['GET'])
def export_pdf():
    data = load_data()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Percorrer todos os registos e adicionar ao PDF
    for manga, registos in data.items():
        pdf.cell(200, 10, f'Manga: {manga}', ln=True, align='C')
        pdf.cell(40, 10, 'Numero', 1)
        pdf.cell(50, 10, 'Chegada', 1)
        pdf.cell(50, 10, 'Partida', 1)
        pdf.cell(50, 10, 'Tempo Total', 1)
        pdf.ln()

        # Adicionar cada registo à tabela no PDF
        for registo in registos['geral']:
            pdf.cell(40, 10, str(registo.get('numero', '')), 1)
            pdf.cell(50, 10, registo.get('chegada', ''), 1)
            pdf.cell(50, 10, registo.get('partida', ''), 1)
            pdf.cell(50, 10, registo.get('tempo_total', ''), 1)
            pdf.ln()

    # Gerar o arquivo PDF
    pdf_file = 'registos_rallye.pdf'
    pdf.output(pdf_file)

    return jsonify({"message": f"PDF exportado com sucesso: {pdf_file}"}), 200

if __name__ == '__main__':
    app.run(debug=True)
