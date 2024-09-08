import socket
import sys
from tkinter import *
from tkinter import messagebox, scrolledtext

HOST = '127.0.0.1'
PORT = 20000
BUFFER_SIZE = 1024

# Cores
BUTTON_COLOR = "#9D2F3B"
POPUP_COLOR = "#A9AEB2"
BACKGROUND_COLOR = "#FFFFFF"

class ClienteApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Cliente de Perguntas")
        self.master.configure(bg=BACKGROUND_COLOR)
        self.s = None  # socket de conexão
        self.somaResultado = 0
        self.total = 0

        # Configurações da interface
        self.lbl_nome = Label(master, text="Informe seu nome:", bg=BACKGROUND_COLOR)
        self.lbl_nome.pack(pady=(10, 0))

        self.entry_nome = Entry(master)
        self.entry_nome.pack(pady=(0, 10), padx=20, ipadx=10)

        self.btn_conectar = Button(master, text="Conectar ao Servidor", command=self.conectar, bg=BUTTON_COLOR, fg="white")
        self.btn_conectar.pack(pady=(0, 10), ipadx=10)

        self.lbl_pergunta = Label(master, text="Digite sua dúvida:", bg=BACKGROUND_COLOR)
        self.lbl_pergunta.pack()

        self.entry_pergunta = Entry(master)
        self.entry_pergunta.pack(pady=(0, 10), padx=20, ipadx=10)

        self.btn_enviar = Button(master, text="Enviar Pergunta", command=self.enviar_pergunta, bg=BUTTON_COLOR, fg="white")
        self.btn_enviar.pack(pady=(0, 10), ipadx=10)

        self.lbl_resposta = Label(master, text="Resposta:", bg=BACKGROUND_COLOR)
        self.lbl_resposta.pack()

        self.text_resposta = Text(master, height=10, width=50)
        self.text_resposta.pack(pady=(0, 10), padx=20)

        # Área de logs
        self.lbl_logs = Label(master, text="Logs:", bg=BACKGROUND_COLOR)
        self.lbl_logs.pack()

        self.text_logs = scrolledtext.ScrolledText(master, height=10, width=50, state='disabled')
        self.text_logs.pack(pady=(0, 10), padx=20)

    def log(self, message):
        self.text_logs.config(state='normal')
        self.text_logs.insert(END, message + "\n")
        self.text_logs.config(state='disabled')
        self.text_logs.see(END)

    def conectar(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((HOST, PORT))
            nome = self.entry_nome.get()
            if nome:
                self.s.send(nome.encode())
                self.custom_messagebox("Conexão", "Conectado ao servidor!")
                self.log(f"Conectado ao servidor com o nome: {nome}")
            else:
                self.custom_messagebox("Aviso", "Por favor, insira um nome.")
                self.log("Tentativa de conexão sem nome.")
        except Exception as error:
            self.custom_messagebox("Erro", f"Erro ao conectar ao servidor: {error}")
            self.log(f"Erro ao conectar ao servidor: {error}")

    def enviar_pergunta(self):
        pergunta = self.entry_pergunta.get()
        if pergunta:
            try:
                self.s.send(pergunta.encode())
                resposta = self.s.recv(BUFFER_SIZE).decode('utf-8')
                self.text_resposta.delete(1.0, END)
                self.text_resposta.insert(END, resposta)
                self.log(f"Pergunta enviada: {pergunta}")
                self.log(f"Resposta recebida: {resposta}")
                self.popup_resposta_recebida(resposta)  # Chamar o pop-up "Resposta Recebida"
            except Exception as error:
                self.custom_messagebox("Erro", f"Erro ao enviar pergunta: {error}")
                self.log(f"Erro ao enviar pergunta: {error}")
        else:
            self.custom_messagebox("Aviso", "Por favor, insira uma pergunta.")
            self.log("Tentativa de envio sem pergunta.")

    def popup_resposta_recebida(self, resposta):
        popup = Toplevel(self.master)
        popup.title("Resposta Recebida")
        popup.configure(bg=POPUP_COLOR)
        Label(popup, text=f"Resposta recebida: {resposta}", bg=POPUP_COLOR, fg="black").pack(pady=10, padx=10)
        Button(popup, text="OK", command=lambda: [self.popup_votacao_resposta(), popup.destroy()], bg=BUTTON_COLOR, fg="white").pack(pady=10)

    def popup_votacao_resposta(self):
        popup = Toplevel(self.master)
        popup.title("Votação")
        popup.configure(bg=POPUP_COLOR)
        Label(popup, text="Quem respondeu a pergunta?", bg=POPUP_COLOR, fg="black").pack(pady=10, padx=10)
        Button(popup, text="ChatGPT", command=lambda: [self.enviar_chute(1), popup.destroy()], bg=BUTTON_COLOR, fg="white").pack(pady=5)
        Button(popup, text="Humano", command=lambda: [self.enviar_chute(2), popup.destroy()], bg=BUTTON_COLOR, fg="white").pack(pady=5)

    def enviar_chute(self, chute):
        try:
            self.s.send(str(chute).encode())
            resultado = int(self.s.recv(BUFFER_SIZE).decode('utf-8'))
            self.somaResultado += resultado
            self.total += 1
            self.popup_resultado_votacao(resultado)
        except Exception as error:
            self.custom_messagebox("Erro", f"Erro ao enviar chute: {error}")
            self.log(f"Erro ao enviar chute: {error}")

    def popup_resultado_votacao(self, resultado):
        popup = Toplevel(self.master)
        popup.title("Resultado da Votação")
        popup.configure(bg=POPUP_COLOR)
        Label(popup, text=f"Resultado da Votação: {'Correto' if resultado == 1 else 'Incorreto'}", bg=POPUP_COLOR, fg="black").pack(pady=10, padx=10)
        Label(popup, text=f"Pontos: {resultado}", bg=POPUP_COLOR, fg="black").pack(pady=10, padx=10)
        self.log(f"Votação realizada: {'Correto' if resultado == 1 else 'Incorreto'}, Pontos: {resultado}.")
        Button(popup, text="Continuar", command=lambda: [popup.destroy(), self.popup_continuar_ou_finalizar()], bg=BUTTON_COLOR, fg="white").pack(side=LEFT, padx=20, pady=10)
        Button(popup, text="Encerrar", command=self.encerrar, bg=BUTTON_COLOR, fg="white").pack(side=RIGHT, padx=20, pady=10)

    def popup_continuar_ou_finalizar(self):
        popup = Toplevel(self.master)
        popup.title("Continuar ou Encerrar")
        popup.configure(bg=POPUP_COLOR)
        Label(popup, text="Deseja continuar ou encerrar?", bg=POPUP_COLOR, fg="black").pack(pady=10, padx=10)
        Button(popup, text="Continuar", command=popup.destroy, bg=BUTTON_COLOR, fg="white").pack(side=LEFT, padx=20, pady=10)
        Button(popup, text="Encerrar", command=self.encerrar, bg=BUTTON_COLOR, fg="white").pack(side=RIGHT, padx=20, pady=10)

    def encerrar(self):
        if self.s:
            self.s.close()
        self.custom_messagebox("Encerrado", "Conexão encerrada.")
        self.log("Conexão encerrada.")
        self.master.quit()

    def custom_messagebox(self, title, message):
        popup = Toplevel(self.master)
        popup.title(title)
        popup.configure(bg=POPUP_COLOR)
        Label(popup, text=message, bg=POPUP_COLOR, fg="black").pack(pady=10, padx=10)
        Button(popup, text="OK", command=popup.destroy, bg=BUTTON_COLOR, fg="white").pack(pady=10)

def main():
    root = Tk()
    app = ClienteApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
