import tkinter as tk
import tkinter.ttk as ttk
import json
import threading
import time

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

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        self.tab_processos = ttk.Frame(self.notebook)
        self.tab_memoria = ttk.Frame(self.notebook)
        self.tab_global = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_processos, text="Processos")
        self.notebook.add(self.tab_memoria, text="Memória")
        self.notebook.add(self.tab_global, text="Global")

        self.tabela_processos = ttk.Treeview(self.tab_processos, columns=("PID", "PPID", "Memória", "CPU", "Leitura", "Escrita"))
        self.tabela_processos.heading("#0", text="Nome")
        self.tabela_processos.heading("#1", text="PID")
        self.tabela_processos.heading("#2", text="PPID")
        self.tabela_processos.heading("#3", text="Memória")
        self.tabela_processos.heading("#4", text="CPU")
        self.tabela_processos.heading("#5", text="Leitura")
        self.tabela_processos.heading("#6", text="Escrita")
        self.tabela_processos.pack(expand=True, fill=tk.BOTH, side="top")
        
        self.tabela_memoria = ttk.Treeview(self.tab_memoria, columns=("PID", "Memoria Total", "Memoria Codigo", "Memoria Heap", "Memoria Stack",
                                                                 "Total de Paginas", "Paginas Codigos", "Paginas Heap", "Paginas Stack"))
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
        self.tabela_memoria.pack(expand=True, fill=tk.BOTH, side="top")
        
        self.tabela_global = ttk.Treeview(self.tab_global, columns=("RAM Livre", "Porcentagem de RAM utilizada", "Swap Total", 
                                                                "Swap Livre", "Porcentagem de Swap utilizado"))
        self.tabela_global.heading("#0", text="RAM Total")
        self.tabela_global.heading("#1", text="RAM Livre")
        self.tabela_global.heading("#2", text="Porcentagem de RAM utilizada")
        self.tabela_global.heading("#3", text="Swap Total")
        self.tabela_global.heading("#4", text="Swap Livre")
        self.tabela_global.heading("#5", text="Porcentagem de Swap utilizado")
        self.tabela_global.pack(expand=True, fill=tk.BOTH, side="top")

        self.atualizar_dados_thread = threading.Thread(target=self.atualizar_dados)
        self.atualizar_dados_thread.daemon = True
        self.atualizar_dados_thread.start()

        self.window.mainloop()

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
            cpu = str(tarefa["cpu_usage"]) + "%"
            leitura = str(tarefa["total_read_bytes"]) + " b"
            escrita = str(tarefa["total_write_bytes"]) + " b"

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
            total_memory = tarefa["total_memory"]
            code_memory = tarefa["code_memory"]
            heap_memory = tarefa["heap_memory"]
            stack_memory = tarefa["stack_memory"]
            total_pages = tarefa["total_pages"]
            code_pages = tarefa["code_pages"]
            heap_pages = tarefa["heap_pages"]
            stack_pages = tarefa["stack_pages"]
            nova_tarefa = TarefaMemoria(nome, pid, total_memory, code_memory, heap_memory, stack_memory, total_pages, code_pages, heap_pages, stack_pages)
            tarefas_memoria.append(nova_tarefa)

        self.limpar_tabela_memoria()
        for tarefa in tarefas_memoria:
            self.inserir_tarefa_memoria(tarefa)

    def atualizar_tarefas_global(self):
        with open("global_data.json", "r") as arquivo:
            dados = json.load(arquivo)

        tarefas_global = []
        total_ram = str(dados["total_ram"]) + " Mb"
        free_ram = str(dados["free_ram"]) + " Mb"
        ram_usage_percentage = str(dados["ram_usage_percentage"]) + " %"
        total_swap = str(dados["total_swap"]) + " Mb"
        free_swap = str(dados["free_swap"]) + " Mb"
        swap_usage_percentage = str(dados["swap_usage_percentage"]) + " %"
        nova_tarefa = TarefaGlobal(total_ram, free_ram, ram_usage_percentage, total_swap, free_swap, swap_usage_percentage)
        tarefas_global.append(nova_tarefa)
        
        self.limpar_tabela_global()
        for tarefa in tarefas_global:
            self.inserir_tarefa_global(tarefa)

if __name__ == "__main__":
    app = GerenciadorTarefas()
