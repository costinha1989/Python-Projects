import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import folium
from flask import Flask, render_template, request, redirect, url_for, send_file, session
from geopy.geocoders import Nominatim
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from file_operations import read_locations_from_file, save_locations_to_file

app = Flask(__name__)
app.secret_key = 'my_secret_key'  # Chave secreta para a sessão

registry = "registry.json"  # É o ficheiro que será guardado as recolhas realizadas pelos utilizadores


def verify_user(username, password):  # Função para verificação das credenciais do utilizador
    with open('users.json') as f:
        data = json.load(f)
        for user in data['users']:
            if user['username'] == username and user['password'] == password:
                return True
    return False


# Middleware para verificar a autenticação e a duração do login
@app.before_request
def check_login():
    if request.endpoint not in ['login', 'static']:
        if 'username' not in session or 'login_time' not in session:
            return redirect(url_for('login'))

        login_time = datetime.strptime(session['login_time'], '%Y-%m-%d %H:%M:%S')
        if datetime.now() - login_time > timedelta(
                minutes=20):  # indica que o tempo em que o login fica ativo, nesse caso são 20 minutos até ao logout automático
            session.pop('username', None)
            session.pop('login_time', None)
            return redirect(url_for('login'))


def geocode_location(city, country, locality=None):
    address = f"{locality + ', ' if locality else ''}{city}, {country}"
    geolocator = Nominatim(user_agent="map_app")
    location = geolocator.geocode(address)

    if location is None:
        print(f"Não foi possível encontrar a localização para o endereço: {address}")
        return None

    return location.latitude, location.longitude


def save_locations_to_file(locations, filename):
    with open(filename, "a") as file:
        for loc in locations:
            if loc['Location'] is not None:
                file.write(
                    f"{loc['JID']},{loc['Localidade']},{loc['Cidade']},{loc['País']},{loc['Grupo']},{loc['Divisão']},{loc['Location'][0]},{loc['Location'][1]}\n")
            else:
                print(f"Aviso: Localização ausente para o JID '{loc['JID']}'. Essa entrada não será salva.")


def read_locations_from_file(file_path):
    locations = []
    with open(file_path, 'r') as file:
        for line in file:
            values = line.strip().split(',')
            if len(values) != 8:
                # Skip the line if it doesn't contain the expected number of values
                continue

            jid, localidade, city, country, grupo, divisao, lat, lon = values
            location = {
                "JID": jid,
                "Localidade": localidade,
                "Cidade": city,
                "País": country,
                "Grupo": grupo,
                "Divisão": divisao,
                "Lat": float(lat),  # Convert latitude to float
                "Lon": float(lon),  # Convert longitude to float
            }
            location["Location"] = [location["Lat"], location["Lon"]]  # Add "Location" key
            locations.append(location)
    return locations


# Rota para a página de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if verify_user(username, password):
            session['username'] = username
            session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return redirect(url_for('index'))
        else:
            error_msg = "Nome de usuário ou senha inválidos."
            return render_template('login.html', error_msg=error_msg)
    return render_template('login.html')


@app.route('/index-outros-utilizadores')
def index_outros_utilizadores():
    if 'username' in session and 'login_time' in session:
        username = session['username']
        login_time = session['login_time']
        return render_template('index2.html', username=username, login_time=login_time)
    else:
        return redirect(url_for('login'))


# Rota para a página protegida (requer autenticação)
@app.route('/index.html')
def index():
    if 'username' in session and 'login_time' in session:
        username = session['username']
        login_time = session['login_time']

        # Verifica se o usuário é 'admin' ou 'crao'
        if username in ['admin', 'crao']:
            return render_template('index.html', username=username, login_time=login_time)
        else:
            return redirect(url_for('index_outros_utilizadores'))
    else:
        return redirect(url_for('login'))


@app.route('/pagina-inicial')
def pagina_inicial():
    if 'username' in session and 'login_time' in session:
        username = session['username']
        login_time = session['login_time']

        # Verifica se o usuário é 'admin' ou 'crao'
        if username in ['admin', 'crao']:
            return render_template('index.html', username=username, login_time=login_time)
        else:
            return redirect(url_for('index_outros_utilizadores'))
    else:
        return redirect(url_for('login'))


# Endpoint para fazer logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/introduzir-registo', methods=['GET', 'POST'])
def introduzir_registo():
    # lista de países
    countries = [
        "Afeganistão", "África do Sul", "Albânia", "Alemanha", "Andorra", "Angola", "Antiga e Barbuda",
        "Arábia Saudita",
        "Argélia", "Argentina", "Arménia", "Austrália", "Áustria", "Azerbaijão", "Bahamas", "Bangladesh", "Barbados",
        "Barém", "Bélgica", "Benim", "Bielorrússia", "Bolívia", "Bósnia e Herzegovina", "Botsuana", "Brasil", "Brunei",
        "Bulgária", "Burquina Faso", "Burúndi", "Butão", "Cabo Verde", "Camarões", "Camboja", "Canadá", "Catar",
        "Cazaquistão", "Chade", "Chile", "China", "Chipre", "Colômbia", "Comores", "Congo-Brazzaville",
        "Coreia do Norte",
        "Coreia do Sul", "Cosovo", "Costa do Marfim", "Costa Rica", "Croácia", "Cuaite", "Cuba", "Dinamarca",
        "Dominica",
        "Egito", "Emirados Árabes Unidos", "Equador", "Eritreia", "Eslováquia", "Eslovénia", "Espanha", "Essuatíni",
        "Estado da Palestina", "Estados Unidos", "Estónia", "Etiópia", "Fiji", "Filipinas", "Finlândia", "França",
        "Gabão",
        "Gâmbia", "Gana", "Geórgia", "Granada", "Grécia", "Guatemala", "Guiana", "Guiné", "Guiné Equatorial",
        "Guiné-Bissau",
        "Haiti", "Honduras", "Hungria", "Iémen", "Ilhas Marechal", "Índia", "Indonésia", "Irão", "Iraque", "Irlanda",
        "Islândia", "Israel", "Itália", "Jamaica", "Japão", "Jibuti", "Jordânia", "Laus", "Lesoto", "Letónia", "Líbano",
        "Libéria", "Líbia", "Listenstaine", "Lituânia", "Luxemburgo", "Macedónia do Norte", "Madagáscar", "Malásia",
        "Maláui", "Maldivas", "Mali", "Malta", "Marrocos", "Maurícia", "Mauritânia", "México", "Mianmar", "Micronésia",
        "Moçambique", "Moldávia", "Mónaco", "Mongólia", "Montenegro", "Namíbia", "Nauru", "Nepal", "Nicarágua", "Níger",
        "Nigéria", "Noruega", "Nova Zelândia", "Omã", "Países Baixos", "Palau", "Panamá", "Papua Nova Guiné",
        "Paquistão",
        "Paraguai", "Peru", "Polónia", "Portugal", "Quénia", "Quirguistão", "Quiribáti", "Reino Unido",
        "República Centro-Africana", "República Checa", "República Democrática do Congo", "República Dominicana",
        "Roménia", "Ruanda", "Rússia", "Salomão", "Salvador", "Samoa", "Santa Lúcia", "São Cristóvão e Neves",
        "São Marinho", "São Tomé e Príncipe", "São Vicente e Granadinas", "Seicheles", "Senegal", "Serra Leoa",
        "Sérvia",
        "Singapura", "Síria", "Somália", "Sri Lanca", "Sudão", "Sudão do Sul", "Suécia", "Suíça", "Suriname",
        "Tailândia",
        "Taiuã", "Tajiquistão", "Tanzânia", "Timor-Leste", "Togo", "Tonga", "Trindade e Tobago", "Tunísia",
        "Turcomenistão",
        "Turquia", "Tuvalu", "Ucrânia", "Uganda", "Uruguai", "Usbequistão", "Vanuatu", "Vaticano", "Venezuela",
        "Vietname",
        "Zâmbia", "Zimbábue"
    ]

    # lista de Grupos
    groups = [
        "39 - São Roque", "63 - Ribeirinha", "80 - Ponta Delgada", "97 - Água de Pau", "111 - Ribeira Seca RGR",
        "126 - Rabo de Peixe", "137 - Santo António", "186 - Fajã de Cima", "193 - Relva", "227 - Covoada"
    ]

    if request.method == 'POST':
        jid = request.form['jid']
        localidade = request.form['localidade']
        city = request.form['cidade']
        country = request.form['pais']
        grupo = request.form['grupo']
        divisao = request.form['divisao']

        location = geocode_location(city, country, localidade)
        new_location = {
            "JID": jid,
            "Localidade": localidade,
            "Cidade": city,
            "País": country,
            "Grupo": grupo,
            "Divisão": divisao,
            "Location": location
        }

        if os.path.exists(registry):
            locations = read_locations_from_file(registry)
        else:
            locations = []

        locations.append(new_location)
        save_locations_to_file([new_location], registry)
        return redirect(url_for('pagina_inicial'))

    return render_template('introduzir_registo.html', countries=countries, groups=groups)


@app.route('/visualizar-conteudo')
def visualizar_conteudo():
    if os.path.exists(registry):
        locations = read_locations_from_file(registry)
        return render_template('visualizar_conteudo.html', locations=locations)

    return render_template('visualizar_conteudo.html', locations=[])


@app.route('/visualizar-mapa')
def visualizar_mapa():
    if os.path.exists(registry):
        locations = read_locations_from_file(registry)
        if locations:
            map_osm = folium.Map(location=locations[0]["Location"], zoom_start=12)

            for loc in locations:
                popup_content = f"JID: {loc['JID']}<br>" \
                                f"Localidade: {loc['Localidade']}<br>" \
                                f"Cidade: {loc['Cidade']}<br>" \
                                f"País: {loc['País']}<br>" \
                                f"Grupo: {loc['Grupo']}<br>" \
                                f"Divisão: {loc['Divisão']}<br>"

                folium.Marker(location=loc["Location"], popup=popup_content).add_to(map_osm)

            map_file_path = "web_app/static/map.html"
            os.makedirs(os.path.dirname(map_file_path), exist_ok=True)  # Create the directory if it doesn't exist
            map_osm.save(map_file_path)

            return send_file(map_file_path, as_attachment=True)  # Return the file as an attachment for download
        else:
            error_msg = "Nenhuma localização encontrada."
            return render_template('visualizar_mapa.html', error_msg=error_msg)
    else:
        error_msg = "Nenhuma localização encontrada. Registre locais antes de visualizar o mapa."
        return render_template('visualizar_mapa.html', error_msg=error_msg)


@app.route('/exportar-pdf')
def exportar_pdf():
    if os.path.exists(registry):
        locations = read_locations_from_file(registry)
        if locations:
            pdf_file = f"{Path(registry).stem}.pdf"

            # Formatando os dados em formato de tabela
            headers = ["JID", "Localidade", "Cidade", "País", "Grupo", "Divisão"]
            data = []

            for loc in locations:
                row = [
                    loc.get("JID", ""),
                    loc.get("Localidade", ""),
                    loc.get("Cidade", ""),
                    loc.get("País", ""),
                    loc.get("Grupo", ""),
                    loc.get("Divisão", "")
                ]
                data.append(row)

            table_data = [headers] + data

            # Criar um documento PDF
            doc = SimpleDocTemplate(pdf_file, pagesize=letter)

            # Criar a tabela e definir estilos
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),  # Alinhar toda a tabela à direita
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            # Adicionar a tabela ao documento PDF
            doc.build([table])

            return send_file(pdf_file, as_attachment=True)

    return render_template('exportar_pdf.html', error_msg="Não existe dados para exportação.")


if __name__ == "__main__":
    app.run(debug=True)
