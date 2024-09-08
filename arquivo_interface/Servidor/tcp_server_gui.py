import socket
import sys
from threading import Thread
from tkinter import *
from tkinter import messagebox, scrolledtext

HOST = '127.0.0.1'
PORT = 20000
BUFFER_SIZE = 1024

# Cores
BUTTON_COLOR = "#9D2F3B"
POPUP_COLOR = "#A9AEB2"
BACKGROUND_COLOR = "#FFFFFF"

class ServidorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Servidor de Perguntas")
        self.master.configure(bg=BACKGROUND_COLOR)
        self.s = None  # socket do servidor
        self.clientsocket = None
        self.addr = None

        # Configurações da interface
        self.lbl_status = Label(master, text="Servidor Desconectado", bg=BACKGROUND_COLOR)
        self.lbl_status.pack(pady=(10, 0))

        self.btn_iniciar = Button(master, text="Iniciar Servidor", command=self.iniciar_servidor, bg=BUTTON_COLOR, fg="white")
        self.btn_iniciar.pack(pady=(10, 10), ipadx=10)

        self.lbl_pergunta = Label(master, text="Pergunta Recebida:", bg=BACKGROUND_COLOR)
        self.lbl_pergunta.pack()

        self.text_pergunta = Text(master, height=5, width=50)
        self.text_pergunta.pack(pady=(0, 10), padx=20)

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

    def iniciar_servidor(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((HOST, PORT))
            self.s.listen()
            self.log("Servidor iniciado e ouvindo em {}:{}".format(HOST, PORT))
            self.lbl_status.config(text="Servidor Conectado")
            Thread(target=self.aceitar_clientes).start()
        except Exception as error:
            self.custom_messagebox("Erro", f"Erro ao iniciar o servidor: {error}")
            self.log(f"Erro ao iniciar o servidor: {error}")

    def aceitar_clientes(self):
        while True:
            try:
                self.clientsocket, self.addr = self.s.accept()
                self.log(f"Conectado ao cliente no endereço: {self.addr}")
                Thread(target=self.gerenciar_cliente).start()
            except Exception as e:
                self.log(f"Erro ao aceitar cliente: {e}")
                break

    def gerenciar_cliente(self):
        try:
            while True:
                data = self.clientsocket.recv(BUFFER_SIZE)
                if not data:
                    break
                mensagem = data.decode('utf-8')
                if "?" in mensagem:  # Verifica se é uma pergunta válida
                    self.text_pergunta.delete(1.0, END)
                    self.text_pergunta.insert(END, mensagem)
                    self.log(f"Pergunta recebida do cliente {self.addr}: {mensagem}")
                    self.popup_responder_pergunta()
                else:
                    self.log(f"Conectado ao cliente: {mensagem}")
        except Exception as e:
            self.log(f"Erro na conexão com o cliente: {e}")

    def popup_responder_pergunta(self):
        popup = Toplevel(self.master)
        popup.title("Responder Pergunta")
        popup.configure(bg=POPUP_COLOR)
        Label(popup, text="Escolha quem vai responder:", bg=POPUP_COLOR, fg="black").pack(pady=10, padx=10)
        Button(popup, text="Responder com ChatGPT", command=lambda: [self.responder_gpt(), popup.destroy()], bg=BUTTON_COLOR, fg="white").pack(pady=5)
        Button(popup, text="Responder Manualmente", command=lambda: [self.responder_humano(popup)], bg=BUTTON_COLOR, fg="white").pack(pady=5)

    def responder_gpt(self):
        resposta = "Resposta simulada pelo ChatGPT."
        self.enviar_resposta_texto(resposta)

    def responder_humano(self, popup):
        popup.destroy()
        self.abrir_popup_resposta_manual()

    def abrir_popup_resposta_manual(self):
        popup = Toplevel(self.master)
        popup.title("Resposta Manual")
        popup.configure(bg=POPUP_COLOR)
        Label(popup, text="Digite a resposta manual:", bg=POPUP_COLOR, fg="black").pack(pady=10, padx=10)
        entry_resposta = Entry(popup)
        entry_resposta.pack(pady=(0, 10), padx=20, ipadx=10)
        Button(popup, text="Enviar", command=lambda: [self.enviar_resposta(entry_resposta.get()), popup.destroy()], bg=BUTTON_COLOR, fg="white").pack(pady=10)

    def enviar_resposta(self, resposta):
        if resposta:
            self.enviar_resposta_texto(resposta)
        else:
            self.custom_messagebox("Aviso", "Por favor, insira uma resposta.")

    def enviar_resposta_texto(self, resposta):
        try:
            self.clientsocket.send(resposta.encode())
            self.log(f"Resposta enviada: {resposta}")
            self.popup_resposta_enviada(resposta)
        except Exception as e:
            self.custom_messagebox("Erro", f"Erro ao enviar resposta: {e}")
            self.log(f"Erro ao enviar resposta: {e}")

    def popup_resposta_enviada(self, resposta):
        popup = Toplevel(self.master)
        popup.title("Resposta Enviada")
        popup.configure(bg=POPUP_COLOR)
        Label(popup, text=f"Resposta enviada: {resposta}", bg=POPUP_COLOR, fg="black").pack(pady=10, padx=10)
        Button(popup, text="OK", command=popup.destroy, bg=BUTTON_COLOR, fg="white").pack(pady=10)

    def custom_messagebox(self, title, message):
        popup = Toplevel(self.master)
        popup.title(title)
        popup.configure(bg=POPUP_COLOR)
        Label(popup, text=message, bg=POPUP_COLOR, fg="black").pack(pady=10, padx=10)
        Button(popup, text="OK", command=popup.destroy, bg=BUTTON_COLOR, fg="white").pack(pady=10)

def main():
    root = Tk()
    app = ServidorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()


