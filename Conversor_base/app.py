# app.py
from flask import Flask, render_template, request
from conversor import converter_para_decimal, converter_de_decimal

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        base_origem = int(request.form["base_origem"])
        numero = request.form["numero"]
        base_destino = int(request.form["base_destino"])

        # Converter o número da base de origem para decimal
        numero_decimal = converter_para_decimal(numero, base_origem)

        if numero_decimal is None:
            resultado = "Número ou base de origem inválida!"
        else:
            # Converter o número decimal para a base de destino
            resultado = converter_de_decimal(numero_decimal, base_destino)

        return render_template("index.html", resultado=resultado, numero=numero,
                               base_origem=base_origem, base_destino=base_destino)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

