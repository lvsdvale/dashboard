import tkinter as tk
import tkinter.ttk as ttk
import json
import time
import threading

class TarefaProcesso:
    def __init__(self, pid, ppid, memoria, cpu, leitura, escrita):
        self.pid = pid
        self.ppid = ppid
        self.memoria = memoria
        self.cpu = cpu
        self.leitura = leitura
        self.escrita = escrita


class TarefaMemoria:
    def __init__(self, pid, total_memory, code_memory, heap_memory, stack_memory, total_pages, code_pages, heap_pages, stack_pages):
        self.pid = pid
        self.total_memory = total_memory
        self.code_memory = code_memory
        self.heap_memory = heap_memory
        self.stack_memory = stack_memory
        self.total_pages = total_pages
        self.code_pages = code_pages
        self.heap_pages = heap_pages
        self.stack_pages = stack_pages

class DadosGlobais:
    def __init__(self, pid, ppid, memoria, cpu, leitura, escrita):
        self.pid = pid
        self.ppid = ppid
        self.memoria = memoria
        self.cpu = cpu
        self.leitura = leitura
        self.escrita = escrita

class GerenciadorTarefas:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Gerenciador de Tarefas")

        # Criar tabela_processos de tarefas
        self.tabela_processos = ttk.Treeview(self.window, columns=("PID", "PPID", "Memória", "CPU", "Leitura", "Escrita"))
        self.tabela_processos.heading("PID", text="PID")
        self.tabela_processos.heading("PPID", text="PPID")
        self.tabela_processos.heading("Memória", text="Memória")
        self.tabela_processos.heading("CPU", text="CPU")
        self.tabela_processos.heading("Leitura", text="Leitura")
        self.tabela_processos.heading("Escrita", text="Escrita")
        self.tabela_processos.pack(expand=True, fill=tk.BOTH, side="top")
        
        self.tabela_memoria = ttk.Treeview(self.window, columns=("PID", "Memoria Total", "Memoria Codigo", "Memoria Heap", "Memoria Stack",
                                                                 "Total de Paginas", "Paginas Codigos", "Paginas Heap", "Paginas Stack"))
        self.tabela_memoria.heading("PID", text="PID")
        self.tabela_memoria.heading("Memoria Total", text="Memoria Total")
        self.tabela_memoria.heading("Memoria Codigo", text="code_memory")
        self.tabela_memoria.heading("Memoria Heap", text="heap_memory")
        self.tabela_memoria.heading("Memoria Stack", text="stack_memory")
        self.tabela_memoria.heading("Total de Paginas", text="total_pages")
        self.tabela_memoria.heading("Paginas Codigos", text="code_pages")
        self.tabela_memoria.heading("Paginas Heap", text="heap_pages")
        self.tabela_memoria.heading("Paginas Stack", text="stack_pages")
        self.tabela_memoria.pack(expand=True, fill=tk.BOTH, side="top")
        

        # Carregar tarefas iniciais
        self.carregar_tarefas_processos()
        self.carregar_tarefas_memoria()

        # Iniciar thread de atualização automática
        self.atualizar_thread = threading.Thread(target=self.atualizar_tarefas_automaticamente)
        self.atualizar_thread.start()

        # Executar loop principal da interface
        self.window.mainloop()

    def limpar_tabela_processos(self):
        self.tabela_processos.delete(*self.tabela_processos.get_children())
    
    def limpar_tabela_memoria(self):
        self.tabela_processos.delete(*self.tabela_memoria.get_children())

    def carregar_tarefas_processos(self):
        with open("api\processes.json", "r") as arquivo:
            dados = json.load(arquivo)

        tarefas_processos = []
        for tarefa in dados:
            pid = tarefa["pid"]
            ppid = tarefa["ppid"]
            memoria = str(tarefa["mem_usage_mb"]) + " Mb"
            cpu = str(tarefa["cpu_usage"]) + "%"
            leitura = str(tarefa["total_read_bytes"]) + " b"
            escrita = str(tarefa["total_write_bytes"]) + " b"

            nova_tarefa = TarefaProcesso(pid, ppid, memoria, cpu, leitura, escrita)
            tarefas_processos.append(nova_tarefa)
        
        self.limpar_tabela_processos()
        for tarefa in tarefas_processos:
                self.inserir_tarefa_processo(tarefa)
    
    def carregar_tarefas_memoria(self):
        with open("api\processes_memory.json", "r") as arquivo:
            dados = json.load(arquivo)
        tarefas_memoria = []
        for tarefa in dados:
            pid = tarefa["pid"]
            total_memory = tarefa["total_memory"]
            code_memory = tarefa["code_memory"]
            heap_memory = tarefa["heap_memory"]
            stack_memory = tarefa["stack_memory"]
            total_pages = tarefa["total_pages"]
            code_pages = tarefa["code_pages"]
            heap_pages = tarefa["heap_pages"]
            stack_pages = tarefa["stack_pages"]
            nova_tarefa = TarefaMemoria(pid, total_memory, code_memory, heap_memory, stack_memory, total_pages, code_pages, heap_pages, stack_pages)
            tarefas_memoria.append(nova_tarefa)


        self.limpar_tabela_memoria()
        for tarefa in tarefas_memoria:
            self.inserir_tarefa_memoria(tarefa)

    def inserir_tarefa_processo(self, tarefa):
        valores = (tarefa.pid, tarefa.ppid, tarefa.memoria, tarefa.cpu, tarefa.leitura, tarefa.escrita)
        self.tabela_processos.insert("", tk.END, values=valores)
    
    def inserir_tarefa_memoria(self, tarefa):
        valores = (tarefa.pid, tarefa.total_memory, tarefa.code_memory, tarefa.heap_memory, tarefa.total_pages, tarefa.code_pages, tarefa.heap_pages, tarefa.stack_pages)
        self.tabela_memoria.insert("", tk.END, values=valores)

    def atualizar_tarefas_processos(self):
        self.carregar_tarefas_processos()
        
    def atualizar_tarefas_memoria(self):
        self.carregar_tarefas_memoria()  

    def atualizar_tarefas_automaticamente(self):
        while True:
            self.atualizar_tarefas_processos()
            self.atualizar_tarefas_memoria()
            time.sleep(6)

if __name__ == "__main__":
    app = GerenciadorTarefas()