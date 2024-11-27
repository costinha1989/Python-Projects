import json
from flask import jsonify, Flask, render_template, redirect, url_for, request
import os
import data_manager
from file_handler import delete_json

app = Flask(__name__, template_folder='templates')


@app.route('/')
def home():
    message = request.args.get('message')
    return render_template('index.html', message=message)


import traceback


@app.route('/processar', methods=['POST'])
def processar():
    log = []

    def log_message(message):
        log.append(message)
        print(message)

    def save_log():
        """Função auxiliar para salvar o log em um arquivo"""
        with open('log.txt', 'a') as log_file:
            log_file.write("\n".join(log) + "\n")

    try:

        log_message("Eliminando os dados antigos...")
        delete_json()
        log_message("Dados eliminados com sucesso.")
        log_message("Importando dados...")
        data_manager.import_sheets(
            "https://docs.google.com/spreadsheets/d/1Nzk56Z3t17Gf1joCHnYGJ73ziU7abE7SeWK8hsyxW3I")
        log_message("Dados importados com sucesso.")
        log_message("Exportando o mapa...")
        save_path_html = 'static/map.html'
        data_manager.show_on_map(save_path_html)
        log_message(f"Mapa guardado com sucesso.")
        log_message("Processo concluído com sucesso.")

        return redirect(url_for('conversor', message="\n".join(log)))

    except Exception as e:
        log_message(f"Ocorreu um erro durante a execução do processo: {str(e)}")
        log_message(traceback.format_exc())

    finally:
        save_log()

    return redirect(url_for('conversor', message="\n".join(log)))


@app.route('/mapa')
def mapa():
    return render_template('mapa.html')


@app.route('/conversor', methods=['GET', 'POST'])
def conversor():
    message = ""

    # Se a requisição for POST, processe os dados
    if request.method == 'POST':
        message = "Processamento concluído com sucesso."
        return redirect(url_for('conversor', message=message))

    if 'message' in request.args:
        message = request.args.get('message')

    return render_template('conversor.html', message=message)


# API para exibir registros
@app.route('/api/registos')
def api_registos():
    try:
        file_path = 'data.json'
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo {file_path} não encontrado.")

        with open(file_path) as f:
            registos_data = json.load(f)
        return jsonify(registos_data)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/registos')
def registos():
    try:
        with open('data.json', encoding='utf-8') as f:
            registos_data = json.load(f)
        return render_template('registos.html', registos=registos_data)
    except Exception as e:
        return redirect(url_for('home', message=f"Erro ao carregar registros: {e}"))


@app.route('/tabela')
def tabela():
    try:
        with open('data.json', encoding='utf-8') as f:
            registos_data = json.load(f)
        return render_template('tabela.html', registos=registos_data)
    except Exception as e:
        return f"Erro ao carregar registros: {e}", 500


@app.route('/webchat')
def webchat():
    return render_template('webchat.html')


@app.route('/obter_log')
def obter_log():
    try:
        with open('log.txt', 'r') as f:
            log_content = f.read()
        return log_content
    except FileNotFoundError:
        return "Log não encontrado.", 404


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
