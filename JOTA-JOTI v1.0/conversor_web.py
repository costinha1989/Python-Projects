# conversor_web.py

import data_manager
from file_handler import delete_json


def realizar_acoes():
    log = []  # Usaremos uma lista para registrar o progresso do processamento

    try:
        # Limpar os dados
        log.append("Limpando dados antigos...")
        del_data()
        log.append("Dados eliminados com sucesso.")

        # Importar dados do Google Sheets
        log.append("Importando dados do Google Sheets...")
        import_google()
        log.append("Dados importados com sucesso.")

        # Exportar o mapa em HTML
        log.append("Exportando mapa em HTML...")
        save_path_html = 'static/map.html'
        export_map(save_path_html)
        log.append(f"Mapa guardado com sucesso em {save_path_html}.")

        # Processo finalizado
        log.append("Processo concluído com sucesso!")

    except Exception as e:
        log.append(f"Erro no processamento: {e}")

    # Retorna o log final para ser exibido na interface web
    return "\n".join(log)


def import_google():
    sheet_url = "https://docs.google.com/spreadsheets/d/1Nzk56Z3t17Gf1joCHnYGJ73ziU7abE7SeWK8hsyxW3I"
    try:
        data_manager.import_sheets(sheet_url)
    except Exception as e:
        raise Exception(f"Erro na importação: {e}")


def export_map(save_path):
    try:
        data_manager.show_on_map(save_path)
    except Exception as e:
        raise Exception(f"Erro na exportação HTML: {e}")


def del_data():
    try:
        delete_json()
    except Exception as e:
        raise Exception(f"Erro ao eliminar dados: {e}")
