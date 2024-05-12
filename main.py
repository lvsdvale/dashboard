import tkinter as tk
import tkinter.ttk as ttk
import json
import time
import threading

class Tarefa:
    def __init__(self, pid, ppid, memoria, cpu, leitura, escrita):
        self.pid = pid
        self.ppid = ppid
        self.memoria = memoria
        self.cpu = cpu
        self.leitura = leitura
        self.escrita = escrita

    def __str__(self):
        return f"{self.pid:<10} {self.ppid:<10} {self.memoria:<10} {self.cpu:<10} {self.leitura:<10} {self.escrita:<10}"

class GerenciadorTarefas:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Gerenciador de Tarefas")

        # Criar tabela de tarefas
        self.tabela = ttk.Treeview(self.window, columns=("PID", "PPID", "Memória", "CPU", "Leitura", "Escrita"))
        self.tabela.heading("PID", text="PID")
        self.tabela.heading("PPID", text="PPID")
        self.tabela.heading("Memória", text="Memória")
        self.tabela.heading("CPU", text="CPU")
        self.tabela.heading("Leitura", text="Leitura")
        self.tabela.heading("Escrita", text="Escrita")
        self.tabela.pack(expand=True, fill=tk.BOTH, side="top")

        # Carregar tarefas iniciais
        self.carregar_tarefas()

        # Iniciar thread de atualização automática
        self.atualizar_thread = threading.Thread(target=self.atualizar_tarefas_automaticamente)
        self.atualizar_thread.start()

        # Executar loop principal da interface
        self.window.mainloop()

    def limpar_tabela(self):
        self.tabela.delete(*self.tabela.get_children())

    def carregar_tarefas(self):
        with open("tarefas.json", "r") as arquivo:
            dados = json.load(arquivo)

        tarefas = []
        for tarefa in dados:
            pid = tarefa["pid"]
            ppid = tarefa["ppid"]
            memoria = tarefa["memoria"]
            cpu = tarefa["cpu"]
            leitura = tarefa["leitura"]
            escrita = tarefa["escrita"]

            nova_tarefa = Tarefa(pid, ppid, memoria, cpu, leitura, escrita)
            tarefas.append(nova_tarefa)
    
    
        self.limpar_tabela()
        for tarefa in tarefas:
            self.inserir_tarefa(tarefa)

    def inserir_tarefa(self, tarefa):
        valores = (tarefa.pid, tarefa.ppid, tarefa.memoria, tarefa.cpu, tarefa.leitura, tarefa.escrita)
        self.tabela.insert("", tk.END, values=valores)

    def filtrar_tarefas(self, event):
        termo_filtro = self.filtro_entry.get()
        tarefas_filtradas = []

        for tarefa in self.tarefas:
            if termo_filtro.lower() in str(tarefa).lower():
                tarefas_filtradas.append(tarefa)

        self.limpar_tabela()
        for tarefa in tarefas_filtradas:
            self.inserir_tarefa(tarefa)

    def atualizar_tarefas(self):
        self.carregar_tarefas()

    def atualizar_tarefas_automaticamente(self):
        while True:
            self.atualizar_tarefas()
            time.sleep(6)

if __name__ == "__main__":
    app = GerenciadorTarefas()
    app.executar()