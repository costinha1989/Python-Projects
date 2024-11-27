import tkinter as tk

from tkinter import filedialog, messagebox, ttk
import data_manager
from file_handler import delete_json


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


def export_txt(save_path_txt):
    try:
        data_manager.save_as_text(save_path_txt)
    except Exception as e:
        raise Exception(f"Erro na exportação TXT: {e}")


def del_data():
    delete_json()


def export_log(log_content):
    save_path = filedialog.asksaveasfilename(
        title="Guardar log como",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if save_path:
        with open(save_path, "w") as log_file:
            log_file.write(log_content)


def realizar_acoes():
    progress_bar.pack(pady=10)  # Mostra a barra de progresso
    progress_bar.start()

    progress_window = tk.Toplevel(janela)
    progress_window.title("Processando")
    progress_window.geometry("400x300")
    progress_window.resizable(False, False)  # Janela não redimensionável

    # Label de progresso
    progress_label = tk.Label(progress_window, text="Processando... Por favor, aguarde.")
    progress_label.pack(pady=10)

    # Área de log
    log_text = tk.Text(progress_window, wrap="word", height=10, width=50)
    log_text.pack(pady=10)

    # Botões
    btn_export_log = tk.Button(progress_window, text="Exportar Log",
                               command=lambda: export_log(log_text.get("1.0", tk.END)), width=15)
    btn_export_log.pack(pady=5)

    btn_ok = tk.Button(progress_window, text="OK", command=progress_window.destroy, width=15)
    btn_ok.pack(pady=5)

    janela.update()  # Atualiza a interface principal
    janela.after(100, processar_acoes, log_text, progress_window)  # Inicia o processamento com atraso


def processar_acoes(log_text, progress_window):
    try:
        # Limpar os dados
        log_text.insert(tk.END, "Limpando dados antigos...\n")
        log_text.see(tk.END)  # Rolagem automática
        del_data()
        log_text.insert(tk.END, "Dados eliminados com sucesso.\n")
        log_text.see(tk.END)
        progress_window.update()

        # Importar dados do Google Sheets
        log_text.insert(tk.END, "Importando dados do Google Sheets...\n")
        log_text.see(tk.END)
        progress_window.update()
        import_google()
        log_text.insert(tk.END, "Dados importados com sucesso do Google Sheets.\n")
        log_text.see(tk.END)
        progress_window.update()

        # Exportar o mapa em HTML
        log_text.insert(tk.END, "Exportando mapa em HTML...\n")
        log_text.see(tk.END)
        progress_window.update()

        # Defina o caminho para salvar o HTML na pasta static
        save_path_html = 'static/map.html'  # Caminho correto
        export_map(save_path_html)
        log_text.insert(tk.END, f"Mapa guardado com sucesso em {save_path_html}.\n")
        log_text.see(tk.END)
        progress_window.update()

        # Finaliza o processo
        log_text.insert(tk.END, "Processo concluído com sucesso!\n")
        log_text.see(tk.END)
        progress_window.update()

    except Exception as e:
        log_text.insert(tk.END, f"Erro no processamento: {e}\n")
        log_text.see(tk.END)
        progress_window.update()

    finally:
        progress_bar.stop()  # Para a barra de loading
        progress_bar.pack_forget()  # Oculta a barra de progresso
        messagebox.showinfo("Concluído", "Processamento concluído!", icon=messagebox.INFO)


def terminate():
    resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja sair?", icon=messagebox.WARNING)
    if resposta:
        janela.quit()


janela = tk.Tk()
janela.title("Conversor")
janela.geometry("400x300")
janela.resizable(False, False)

label = tk.Label(janela, text="Conversor para OpenStreet Maps", font=("Arial", 14))
label.pack(pady=20)

btn_todas_acoes = tk.Button(janela, text="Executar processos", command=realizar_acoes, width=40)
btn_todas_acoes.pack(pady=10)

progress_bar = ttk.Progressbar(janela, mode='indeterminate', length=300)
progress_bar.pack_forget()

btn_sair = tk.Button(janela, text="Sair", command=terminate, width=40)
btn_sair.pack(pady=20)

dev_label = tk.Label(janela, text="Desenvolvido por: Luís Costa", font=("Arial", 10))
dev_label.pack(pady=10)

janela.mainloop()
