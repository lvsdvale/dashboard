import tkinter as tk
from tkinter import ttk,messagebox
from ttkthemes import ThemedStyle  # Importa o estilo temático
import json
import threading
import time 
import subprocess

class TarefaProcesso:
    def __init__(self, nome, pid, ppid, memoria, cpu, leitura, escrita):
        self.nome = nome
        self.pid = pid
        self.ppid = ppid
        self.memoria = memoria
        self.cpu = cpu
        self.leitura = leitura
        self.escrita = escrita

class TarefaMemoria:
    def __init__(self, nome, pid, total_memory, code_memory, heap_memory, stack_memory, total_pages, code_pages, heap_pages, stack_pages):
        self.nome = nome
        self.pid = pid
        self.total_memory = total_memory
        self.code_memory = code_memory
        self.heap_memory = heap_memory
        self.stack_memory = stack_memory
        self.total_pages = total_pages
        self.code_pages = code_pages
        self.heap_pages = heap_pages
        self.stack_pages = stack_pages

class TarefaGlobal:
    def __init__(self, total_ram, free_ram, ram_usage_percentage, total_swap, free_swap, swap_usage_percentage):
        self.total_ram = total_ram
        self.free_ram = free_ram
        self.ram_usage_percentage = ram_usage_percentage
        self.total_swap = total_swap
        self.free_swap = free_swap
        self.swap_usage_percentage = swap_usage_percentage

class GerenciadorTarefas:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Gerenciador de Tarefas")
        
        # Aplica um estilo temático para uma aparência mais moderna
        self.style = ThemedStyle(self.window)
        self.style.set_theme("arc")  # Escolhe o tema "arc" (você pode escolher outros temas disponíveis)

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        self.tab_processos = ttk.Frame(self.notebook)
        self.tab_memoria = ttk.Frame(self.notebook)
        self.tab_global = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_processos, text="Processos")
        self.notebook.add(self.tab_memoria, text="Memória")
        self.notebook.add(self.tab_global, text="Global")

        self.explorador_button = ttk.Button(self.window, text="Explorador de Arquivos", command=self.abrir_explorador_de_arquivos)
        self.explorador_button.pack(pady=10)

        self.configurar_tabela_processos()
        self.configurar_tabela_memoria()
        self.configurar_tabela_global()

        self.tabela_processos.heading("#0", text="Nome", command=lambda: self.ordenar_tabela_processos(self.tabela_processos, 0))
        self.tabela_processos.heading("#1", text="PID", command=lambda: self.ordenar_tabela_processos(self.tabela_processos, 1))
        self.tabela_processos.heading("#2", text="PPID", command=lambda: self.ordenar_tabela_processos(self.tabela_processos, 2))
        self.tabela_processos.heading("#3", text="Memória", command=lambda: self.ordenar_tabela_processos(self.tabela_processos, 3))
        self.tabela_processos.heading("#4", text="CPU", command=lambda: self.ordenar_tabela_processos(self.tabela_processos, 4))
        self.tabela_processos.heading("#5", text="Leitura", command=lambda: self.ordenar_tabela_processos(self.tabela_processos, 5))
        self.tabela_processos.heading("#6", text="Escrita", command=lambda: self.ordenar_tabela_processos(self.tabela_processos, 6))

        self.tabela_memoria.heading("#0", text="Nome", command=lambda: self.ordenar_tabela_memoria(self.tabela_memoria, 0, self.ordenacao_memoria))
        self.tabela_memoria.heading("#1", text="PID", command=lambda: self.ordenar_tabela_memoria(self.tabela_memoria, 1, self.ordenacao_memoria))
        self.tabela_memoria.heading("#2", text="Memoria Total", command=lambda: self.ordenar_tabela_memoria(self.tabela_memoria, 2, self.ordenacao_memoria))
        self.tabela_memoria.heading("#3", text="Memoria Codigo", command=lambda: self.ordenar_tabela_memoria(self.tabela_memoria, 3, self.ordenacao_memoria))
        self.tabela_memoria.heading("#4", text="Memoria Heap", command=lambda: self.ordenar_tabela_memoria(self.tabela_memoria, 4, self.ordenacao_memoria))
        self.tabela_memoria.heading("#5", text="Memoria Stack", command=lambda: self.ordenar_tabela_memoria(self.tabela_memoria, 5, self.ordenacao_memoria))
        self.tabela_memoria.heading("#6", text="Total de Paginas", command=lambda: self.ordenar_tabela_memoria(self.tabela_memoria, 6, self.ordenacao_memoria))
        self.tabela_memoria.heading("#7", text="Paginas Codigos", command=lambda: self.ordenar_tabela_memoria(self.tabela_memoria, 7, self.ordenacao_memoria))
        self.tabela_memoria.heading("#8", text="Paginas Heap", command=lambda: self.ordenar_tabela_memoria(self.tabela_memoria, 8, self.ordenacao_memoria))
        self.tabela_memoria.heading("#9", text="Paginas Stack", command=lambda: self.ordenar_tabela_memoria(self.tabela_memoria, 9, self.ordenacao_memoria))


        self.tabela_global.heading("#0", text="RAM Total", command=lambda: self.ordenar_tabela(self.tabela_global, 0, self.ordenacao_global))
        self.tabela_global.heading("#1", text="RAM Livre", command=lambda: self.ordenar_tabela(self.tabela_global, 1, self.ordenacao_global))
        self.tabela_global.heading("#2", text="Porcentagem de RAM utilizada", command=lambda: self.ordenar_tabela(self.tabela_global, 2, self.ordenacao_global))
        self.tabela_global.heading("#3", text="Swap Total", command=lambda: self.ordenar_tabela(self.tabela_global, 3, self.ordenacao_global))
        self.tabela_global.heading("#4", text="Swap Livre", command=lambda: self.ordenar_tabela(self.tabela_global, 4, self.ordenacao_global))
        self.tabela_global.heading("#5", text="Porcentagem de Swap utilizado", command=lambda: self.ordenar_tabela(self.tabela_global, 5, self.ordenacao_global))

        # Adiciona eventos de clique nas tabelas de processos e memória
        self.tabela_processos.bind("<Double-1>", self.exibir_detalhes_processo)
        self.tabela_memoria.bind("<Double-1>", self.exibir_detalhes_memoria)

        self.atualizar_dados_thread = threading.Thread(target=self.atualizar_dados)
        self.atualizar_dados_thread.daemon = True
        self.atualizar_dados_thread.start()

        self.window.mainloop()

    def configurar_tabela_processos(self):
        self.frame_tabela_processos = ttk.Frame(self.tab_processos)
        self.frame_tabela_processos.pack(expand=True, fill=tk.BOTH)

        
        self.scrollbar_processos = ttk.Scrollbar(self.frame_tabela_processos, orient="vertical")
        self.scrollbar_processos.pack(side="right", fill="y")

        # Cria a tabela de processos
        self.tabela_processos = ttk.Treeview(self.frame_tabela_processos, columns=("PID", "PPID", "Memória", "CPU", "Leitura", "Escrita"), yscrollcommand=self.scrollbar_processos.set)
        self.tabela_processos.heading("#0", text="Nome")
        self.tabela_processos.heading("#1", text="PID")
        self.tabela_processos.heading("#2", text="PPID")
        self.tabela_processos.heading("#3", text="Memória")
        self.tabela_processos.heading("#4", text="CPU")
        self.tabela_processos.heading("#5", text="Leitura")
        self.tabela_processos.heading("#6", text="Escrita")
        self.tabela_processos.pack(expand=True, fill=tk.BOTH, side="left")

        # Configura a barra de rolagem para a tabela
        self.scrollbar_processos.config(command=self.tabela_processos.yview)

        # Configuração da ordenação
        self.ordenacao_processos = {'column': None, 'reverse': False}
        for col in ("#1", "#2", "#3", "#4", "#5", "#6"):
            self.tabela_processos.heading(col, text=col, command=lambda _col=col: self.ordenar_tabela_processos(self.tabela_processos, _col))

    
    def configurar_tabela_memoria(self):
        self.frame_tabela_memoria = ttk.Frame(self.tab_memoria)
        self.frame_tabela_memoria.pack(expand=True, fill=tk.BOTH)

        self.scrollbar_memoria_vertical = ttk.Scrollbar(self.frame_tabela_memoria, orient="vertical")
        self.scrollbar_memoria_vertical.pack(side="right", fill="y")
        self.scrollbar_memoria_horizontal = ttk.Scrollbar(self.frame_tabela_memoria, orient="horizontal")
        self.scrollbar_memoria_horizontal.pack(side="bottom", fill="x")

        self.tabela_memoria = ttk.Treeview(self.frame_tabela_memoria, columns=("PID", "Memoria Total", "Memoria Codigo", "Memoria Heap", "Memoria Stack",
                                                                          "Total de Paginas", "Paginas Codigos", "Paginas Heap", "Paginas Stack"),yscrollcommand=self.scrollbar_memoria_vertical.set, xscrollcommand=self.scrollbar_memoria_horizontal)
        self.tabela_memoria.heading("#0", text="Nome")
        self.tabela_memoria.heading("#1", text="PID")
        self.tabela_memoria.heading("#2", text="Memoria Total")
        self.tabela_memoria.heading("#3", text="Memoria Codigo")
        self.tabela_memoria.heading("#4", text="Memoria Heap")
        self.tabela_memoria.heading("#5", text="Memoria Stack")
        self.tabela_memoria.heading("#6", text="Total de Paginas")
        self.tabela_memoria.heading("#7", text="Paginas Codigos")
        self.tabela_memoria.heading("#8", text="Paginas Heap")
        self.tabela_memoria.heading("#9", text="Paginas Stack")
        self.tabela_memoria.pack(expand=True, fill=tk.BOTH, side="left")

        self.scrollbar_memoria_vertical.config(command=self.tabela_memoria.yview)
        self.scrollbar_memoria_horizontal.config(command=self.tabela_memoria.xview)

        # Configuração da ordenação
        self.ordenacao_memoria = {'column': None, 'reverse': False}
        for col in ("#1", "#2", "#3", "#4", "#5", "#6", "#7", "#8", "#9"):
            self.tabela_memoria.heading(col, text=col, command=lambda _col=col: self.ordenar_tabela_memoria(self.tabela_memoria, _col))

    def configurar_tabela_global(self):
        frame_tabela_global = ttk.Frame(self.tab_global)
        frame_tabela_global.pack(expand=True, fill=tk.BOTH)

        self.tabela_global = ttk.Treeview(frame_tabela_global, columns=("RAM Livre", "Porcentagem de RAM utilizada", "Swap Total", 
                                                                        "Swap Livre", "Porcentagem de Swap utilizado"))
        self.tabela_global.heading("#0", text="RAM Total")
        self.tabela_global.heading("#1", text="RAM Livre")
        self.tabela_global.heading("#2", text="Porcentagem de RAM utilizada")
        self.tabela_global.heading("#3", text="Swap Total")
        self.tabela_global.heading("#4", text="Swap Livre")
        self.tabela_global.heading("#5", text="Porcentagem de Swap utilizado")
        self.tabela_global.pack(expand=True, fill=tk.BOTH, side="left")

        scrollbar_global = ttk.Scrollbar(frame_tabela_global, orient="vertical", command=self.tabela_global.yview)
        self.tabela_global.configure(yscroll=scrollbar_global.set)
        scrollbar_global.pack(side="right", fill="y")


    def atualizar_tarefas_global(self):
        with open("global_data.json", "r") as arquivo:
            dados = json.load(arquivo)

        tarefas_global = []
        total_ram = dados["total_ram"]
        free_ram = str(dados["free_ram"]) + " Mb"
        ram_usage_percentage = str(round(dados["ram_usage_percentage"],1)) + " %"
        total_swap = str(dados["total_swap"]) + " Mb"
        free_swap = str(dados["free_swap"]) + " Mb"
        swap_usage_percentage = str(round(dados["swap_usage_percentage"],1)) + " %"
        nova_tarefa = TarefaGlobal(total_ram, free_ram, ram_usage_percentage, total_swap, free_swap, swap_usage_percentage)
        tarefas_global.append(nova_tarefa)
        
        self.limpar_tabela_global()
        for tarefa in tarefas_global:
            self.inserir_tarefa_global(tarefa)

    def limpar_tabela_processos(self):
        self.tabela_processos.delete(*self.tabela_processos.get_children())
    
    def limpar_tabela_memoria(self):
        self.tabela_memoria.delete(*self.tabela_memoria.get_children())

    def limpar_tabela_global(self):
        self.tabela_global.delete(*self.tabela_global.get_children())

    def inserir_tarefa_processo(self, tarefa):
        valores = (tarefa.pid, tarefa.ppid, tarefa.memoria, tarefa.cpu, tarefa.leitura, tarefa.escrita)
        self.tabela_processos.insert("", tk.END, text=tarefa.nome, values=valores)
    
    def inserir_tarefa_memoria(self, tarefa):
        valores = (tarefa.pid, tarefa.total_memory, tarefa.code_memory, tarefa.heap_memory, tarefa.stack_memory, tarefa.total_pages, tarefa.code_pages, tarefa.heap_pages, tarefa.stack_pages)
        self.tabela_memoria.insert("", tk.END, text=tarefa.nome, values=valores)

    def inserir_tarefa_global(self, tarefa):
        valores = (tarefa.free_ram, tarefa.ram_usage_percentage, tarefa.total_swap, tarefa.free_swap, tarefa.swap_usage_percentage)
        self.tabela_global.insert("", tk.END, values=valores)

    def atualizar_dados(self):
        while True:
            self.atualizar_tarefas_processos()
            self.atualizar_tarefas_memoria()
            self.atualizar_tarefas_global()
            time.sleep(3)

    def atualizar_tarefas_processos(self):
        with open("processes.json", "r") as arquivo:
            dados = json.load(arquivo)

        tarefas_processos = []
        for tarefa in dados:
            nome = tarefa["name"]
            pid = tarefa["pid"]
            ppid = tarefa["ppid"]
            memoria = str(tarefa["mem_usage_mb"]) + " Mb"
            cpu = str(round(tarefa["cpu_usage"]/1024,1)) + "%"
            leitura = str(round(tarefa["total_read_bytes"]/1024,1)) + " Mb"
            escrita = str(round(tarefa["total_write_bytes"]/1024,1)) + " Mb"

            nova_tarefa = TarefaProcesso(nome, pid, ppid, memoria, cpu, leitura, escrita)
            tarefas_processos.append(nova_tarefa)
        
        self.limpar_tabela_processos()
        for tarefa in tarefas_processos:
            self.inserir_tarefa_processo(tarefa)
    
    def atualizar_tarefas_memoria(self):
        with open("processes_memory.json", "r") as arquivo:
            dados = json.load(arquivo)

        tarefas_memoria = []
        for tarefa in dados:
            nome = tarefa["name"]
            pid = tarefa["pid"]
            total_memory = str(round(tarefa["total_memory"]/1024, 1)) + " Mb"
            code_memory = str(round(tarefa["code_memory"]/1024,1)) + " Mb"
            heap_memory = str(round(tarefa["heap_memory"]/1024,1)) + " Mb"
            stack_memory = str(round(tarefa["stack_memory"]/1024,1)) + " Mb"
            total_pages = tarefa["total_pages"]
            code_pages = tarefa["code_pages"]
            heap_pages = tarefa["heap_pages"]
            stack_pages = tarefa["stack_pages"]

            nova_tarefa = TarefaMemoria(nome, pid, total_memory, code_memory, heap_memory, stack_memory, total_pages, code_pages, heap_pages, stack_pages)
            tarefas_memoria.append(nova_tarefa)
        
        self.limpar_tabela_memoria()
        for tarefa in tarefas_memoria:
            self.inserir_tarefa_memoria(tarefa)

    def ordenar_tabela_processos(self, tabela, col):
        # Limpa a ordenação anterior (se houver) nas outras colunas
        for key in self.ordenacao_processos.keys():
            if key != 'column':
                self.ordenacao_processos[key] = False

        # Verifica se a coluna clicada é a mesma que a última
        if self.ordenacao_processos['column'] == col:
            # Alternar a direção da ordenação
            self.ordenacao_processos['reverse'] = not self.ordenacao_processos['reverse']
        else:
            # Primeira vez clicando na coluna: ordenação ascendente
            self.ordenacao_processos['reverse'] = False

        # Obtém os dados atuais da tabela
        data = [(self.get_valor_ordenacao_processo(tabela, item, col), item) for item in tabela.get_children('')]

        # Ordena os dados de acordo com a coluna clicada e a direção
        data.sort(key=lambda x: x[0], reverse=self.ordenacao_processos['reverse'])

        # Rearranja os itens na tabela na nova ordem
        for index, (val, item) in enumerate(data):
            tabela.move(item, '', index)

        # Define a coluna atual para a próxima ordenação
        self.ordenacao_processos['column'] = col

    def get_valor_ordenacao_processo(self, tabela, item, col):
        valor = tabela.set(item, col)
        try:
            # Tentar converter para float se for numérico
            return float(valor)
        except ValueError:
            # Se não for possível converter para float, manter como string
            return valor.lower() if isinstance(valor, str) else valor

    def ordenar_tabela_memoria(self, tabela, col):
        # Limpa a ordenação anterior (se houver) nas outras colunas
        for key in self.ordenacao_memoria.keys():
            if key != 'column':
                self.ordenacao_memoria[key] = False

        # Verifica se a coluna clicada é a mesma que a última
        if self.ordenacao_memoria['column'] == col:
            # Alternar a direção da ordenação
            if self.ordenacao_memoria['estado'] == "original":
                self.ordenacao_memoria['reverse'] = True
                self.ordenacao_memoria['estado'] = "decrescente"
            elif self.ordenacao_memoria['estado'] == "crescente":
                self.ordenacao_memoria['reverse'] = True
                self.ordenacao_memoria['estado'] = "decrescente"
            elif self.ordenacao_memoria['estado'] == "decrescente":
                self.ordenacao_memoria['reverse'] = False
                self.ordenacao_memoria['estado'] = "original"
        else:
            # Primeira vez clicando na coluna: ordenação ascendente
            self.ordenacao_memoria['reverse'] = False
            self.ordenacao_memoria['estado'] = "crescente"

        # Obtém os dados atuais da tabela
        data = [(self.get_valor_ordenacao_memoria(tabela, item, col), item) for item in tabela.get_children('')]

        # Ordena os dados de acordo com a coluna clicada e a direção
        data.sort(key=lambda x: x[0], reverse=self.ordenacao_memoria['reverse'])

        # Rearranja os itens na tabela na nova ordem
        for index, (val, item) in enumerate(data):
            tabela.move(item, '', index)

        # Define a coluna atual para a próxima ordenação
        self.ordenacao_memoria['column'] = col

    def get_valor_ordenacao_memoria(self, tabela, item, col):
        valor = tabela.set(item, col)
        try:
            # Tentar converter para float se for numérico
            return float(valor)
        except ValueError:
            # Se não for possível converter para float, manter como string
            return valor.lower() if isinstance(valor, str) else valor

    def resetar_ordenacao(self):
        self.ordenacao_memoria['estado'] = "original"
        self.ordenacao_memoria['reverse'] = False
        self.ordenar_tabela_memoria(self.tabela, self.coluna_padrao)  # Redefina a ordenação com base na coluna padrão

    def exibir_detalhes_processo(self, event):
        item = self.tabela_processos.selection()[0]
        nome_processo = self.tabela_processos.item(item, "text")
        valores = self.tabela_processos.item(item, "values")
        detalhes_window = tk.Toplevel(self.window)
        detalhes_window.title(f"Detalhes do Processo: {nome_processo}")
        # Cria e posiciona os widgets na nova janela
        nome_label = ttk.Label(detalhes_window, text=f"Processo: {nome_processo}")
        nome_label.pack(pady=10)
        detalhes_frame = ttk.Frame(detalhes_window)
        detalhes_frame.pack(padx=20, pady=10)
        # Adiciona as informações do processo no frame
        labels = ["PID", "PPID", "Memória", "CPU", "Leitura", "Escrita"]
        for i in range(len(labels)):
            ttk.Label(detalhes_frame, text=labels[i]).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            ttk.Label(detalhes_frame, text=valores[i]).grid(row=i, column=1, padx=5, pady=5, sticky="w")
    def exibir_detalhes_memoria(self, event):
        item = self.tabela_memoria.selection()[0]
        nome_processo = self.tabela_memoria.item(item, "text")
        valores = self.tabela_memoria.item(item, "values")
        detalhes_window = tk.Toplevel(self.window)
        detalhes_window.title(f"Detalhes do Processo: {nome_processo}")
        # Cria e posiciona os widgets na nova janela
        nome_label = ttk.Label(detalhes_window, text=f"Processo: {nome_processo}")
        nome_label.pack(pady=10)
        detalhes_frame = ttk.Frame(detalhes_window)
        detalhes_frame.pack(padx=20, pady=10)
        # Adiciona as informações do processo no frame
        labels = ["PID", "Memória Total", "Memória Código", "Memória Heap", "Memória Stack", "Total de Paginas", "Paginas Codigo", "Paginas Heap", "Paginas Stack" ]
        for i in range(len(labels)):
            ttk.Label(detalhes_frame, text=labels[i]).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            ttk.Label(detalhes_frame, text=valores[i]).grid(row=i, column=1, padx=5, pady=5, sticky="w")

    def abrir_explorador_de_arquivos(self):
        self.current_path = ""
        self.history = []
        self.exibir_diretorio("navigation.json")

    def exibir_diretorio(self, json_path):
        try:
            with open(json_path, "r") as arquivo:
                dados = json.load(arquivo)

            path = dados.get("path", "Explorador de Arquivos")
            children = dados.get("children", [])
       
            nova_janela = tk.Toplevel(self.window)
            nova_janela.title(path)
            nova_janela.geometry("600x400")

            frame = ttk.Frame(nova_janela)
            frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

            tree = ttk.Treeview(frame, columns=("Nome", "Tamanho", "Tipo"), show='headings')
            tree.heading("#1", text="Nome")
            tree.heading("#2", text="Tamanho")
            tree.heading("#3", text="Tipo")
            tree.column("#1", anchor=tk.W)
            tree.column("#2", anchor=tk.W)
            tree.column("#3", anchor=tk.W)
            tree.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

            for child in children:
                name = child.get("name", "Desconhecido")
                size = child.get("size", "Desconhecido")
                tipo = child.get("type", "Desconhecido")
                tree.insert("", tk.END, values=(name, size, tipo))

            scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL)
            scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
            scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
            scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

            tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
            scroll_y.config(command=tree.yview)
            scroll_x.config(command=tree.xview)
            def on_item_click(event, path=path):
                item = tree.selection()[0]
                item_text = tree.item(item, "values")
                if item_text[2] == "directory":
                    path = path.replace('\\', '')
                    novo_caminho = f"{path}{item_text[0]}/"
                    print(novo_caminho)
                    self.history.append(path)
                    self.current_path = novo_caminho
                    self.chamar_get_dir_tree(novo_caminho)

            tree.bind("<Double-1>", on_item_click)

            def voltar():
                if self.history:
                    caminho_anterior = self.history.pop()
                    self.exibir_diretorio(caminho_anterior)

            voltar_button = ttk.Button(nova_janela, text="Voltar", command=voltar)
            voltar_button.pack(pady=10)

        except FileNotFoundError:
            messagebox.showerror("Erro", "O arquivo JSON não foi encontrado.")
        except json.JSONDecodeError:
            messagebox.showerror("Erro", "Erro ao decodificar o arquivo JSON.")

    def chamar_get_dir_tree(self, caminho):
        try:
            resultado = subprocess.run(["sudo","./api/get_dir_tree", caminho])
            if resultado.returncode == -6:
                self.exibir_diretorio("navigation.json")
            else:
                messagebox.showerror("Erro", "Erro ao executar o programa get_dir_tree.")
        except FileNotFoundError:
            messagebox.showerror("Erro", "O programa get_dir_tree não foi encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar o programa get_dir_tree: {str(e)}")



if __name__ == "__main__":
    GerenciadorTarefas()

