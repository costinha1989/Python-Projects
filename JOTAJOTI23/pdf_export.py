# pdf_export.py
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def export_to_pdf(locations, filename):
    pdf_file = f"{Path(filename).stem}.pdf"

    # Formatando os dados em formato de tabela
    headers = ["JID", "Localidade", "Cidade", "País", "Grupo", "Divisão"]
    data = [[loc["JID"], loc["Localidade"], loc["Cidade"], loc["País"], loc["Grupo"], loc["Divisão"]] for loc in locations]

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

    print(f"Localizações exportadas para '{pdf_file}'.")
