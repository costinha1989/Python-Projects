import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from lxml import etree
import os

def load_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Ficheiros XML", "*.xml")],
        title="Selecione o ficheiro de inventário em formato XML"
    )
    if file_path:
        process_xml(file_path)

def process_xml(file_path):
    try:
        tree = etree.parse(file_path)
        root = tree.getroot()

        problematic_data = []

        for elem in root.iter():
            # Eliminar linhas ClosingStockValue
            if elem.tag.endswith('ClosingStockValue'):
                parent = elem.getparent()
                if parent is not None:
                    parent.remove(elem)

            # Validar e corrigir ClosingStockQuantity
            if elem.tag.endswith('ClosingStockQuantity'):
                if elem.text:
                    # Substituir vírgulas por pontos
                    elem.text = elem.text.replace(",", ".").strip()

                original_value = elem.text
                try:
                    value = float(original_value)

                    # Verificar casas decimais
                    if len(str(value).split(".")[1]) > 2:
                        # Adicionar à lista de problemas
                        product_code, product_description = find_product_details(elem)
                        problematic_data.append({
                            'product_code': product_code,
                            'product_description': product_description,
                            'original': original_value,
                            'element': elem
                        })
                except ValueError:
                    product_code, product_description = find_product_details(elem)
                    problematic_data.append({
                        'product_code': product_code,
                        'product_description': product_description,
                        'original': original_value,
                        'element': elem
                    })

        if problematic_data:
            show_table(problematic_data, tree, file_path)
        else:
            save_corrected_file(tree, file_path)
            messagebox.showinfo(
                "Sucesso", "Todos os valores corretos. Não necessita correção."
            )

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

def find_product_details(elem):
    """
    Procura pelo ProductCode e ProductDescription no mesmo nível do ClosingStockQuantity.
    """
    product_code = "N/A"
    product_description = "N/A"

    # Obtém o nó pai do ClosingStockQuantity
    parent = elem.getparent()

    # Verifica se o nó pai é válido e contém os campos necessários
    if parent is not None:
        for child in parent:
            tag = etree.QName(child.tag).localname  # Ignorar namespace
            if tag == "ProductCode" and child.text:
                product_code = child.text.strip()
            if tag == "ProductDescription" and child.text:
                product_description = child.text.strip()

    return product_code, product_description

def show_table(data, tree, file_path):
    def edit_value(event):
        selected_item = treeview.focus()
        if not selected_item:
            return

        column = treeview.identify_column(event.x)
        column_index = int(column[1:]) - 1  # Convert column name to index
        if column_index != 3:  # Allow edits only in "Valor Corrigido"
            return

        entry = tk.Entry(table_window)
        entry.place(x=event.x, y=event.y)
        entry.focus_set()

        def save_edit():
            new_value = entry.get()
            try:
                corrected_value = f"{float(new_value):.2f}"
                treeview.item(selected_item, values=(
                    *treeview.item(selected_item, "values")[:3],
                    corrected_value
                ))
                entry.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido.")

        entry.bind("<Return>", lambda e: save_edit())
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    def save_edits():
        invalid_data = []  # Lista de dados que ainda têm problemas
        for idx, item in enumerate(treeview.get_children()):
            corrected_value = treeview.item(item, "values")[3]  # Obtém o valor corrigido
            try:
                # Validar o número corrigido
                corrected_float = float(corrected_value)
                corrected_formatted = f"{corrected_float:.2f}"  # Formata para 2 casas decimais

                # Verificar se há mais de 2 casas decimais no valor corrigido
                if len(str(corrected_float).split(".")[1]) > 2:
                    raise ValueError("Mais de 2 casas decimais")

                # Atualizar o elemento XML com o valor corrigido formatado
                data[idx]['element'].text = corrected_formatted
            except (ValueError, IndexError):
                # Adicionar à lista de dados inválidos se houver problema
                invalid_data.append(data[idx])

        if invalid_data:
            # Exibir mensagem de erro se ainda houver valores inválidos
            messagebox.showwarning(
                "Erro",
                "Corrija os valores incorretos."
            )
            return

        # Guardar o ficheiro corrigido se todos os valores forem válidos
        save_corrected_file(tree, file_path)
        messagebox.showinfo(
            "Sucesso", "Ficheiro validado e guardado."
        )
        table_window.destroy()

    table_window = tk.Toplevel()
    table_window.title("Corrigir")
    table_window.geometry("800x400")

    frame = ttk.Frame(table_window)
    frame.pack(fill=tk.BOTH, expand=True)

    treeview = ttk.Treeview(frame, columns=(
        "product_code", "product_description", "original", "corrected"), show="headings")
    treeview.heading("product_code", text="Código")
    treeview.heading("product_description", text="Descrição")
    treeview.heading("original", text="Valor Original")
    treeview.heading("corrected", text="Valor a corrigir")

    for entry in data:
        treeview.insert("", tk.END, values=(
            entry['product_code'], entry['product_description'],
            entry['original'], entry['original']
        ))

    treeview.bind("<Double-1>", edit_value)
    treeview.pack(fill=tk.BOTH, expand=True)

    save_button = tk.Button(table_window, text="Guardar", command=save_edits)
    save_button.pack(pady=10)

def save_corrected_file(tree, file_path):
    new_file = os.path.splitext(file_path)[0] + "_corrigido.xml"
    tree.write(new_file, encoding="utf-8", pretty_print=True, xml_declaration=True)
    messagebox.showinfo("Ficheiro guardado", f"Ficheiro guardado em {new_file}")

# Interface Gráfica
window = tk.Tk()
window.title("Correção de inventários não valorizados")
window.geometry("300x200")

label = tk.Label(window, text="Localização do ficheiro:")
label.pack(pady=20)

load_button = tk.Button(window, text="Carregar Ficheiro", command=load_file)
load_button.pack(pady=12)

window.mainloop()
