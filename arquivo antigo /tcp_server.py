import socket, sys
from threading import Thread
from random import randint
import requests
import time
import os

HOST = '127.0.0.1'  # endereço IP
PORT = 20000        # Porta utilizada pelo servidor
BUFFER_SIZE = 1024  # tamanho do buffer para recepção dos dados

def on_new_client(clientsocket,addr):
    
    nome_cod = clientsocket.recv(BUFFER_SIZE)
    if not nome_cod:
        nome_cliente = "Nome nao informado"
    nome_cliente = nome_cod.decode('utf-8')
    arquivo = open(r"C:\Users\paulo\Documents\Trabalho Redes 1\datateste.txt","a+")
    arquivo.write("\nNome: " + nome_cliente )
    contador = 0
    resultadoTotal = 0
    porcentagem = 0
    
    
    while True:
        try:
            
            data = clientsocket.recv(BUFFER_SIZE)
            if not data:
                break
            texto_recebido = data.decode('utf-8') # converte os bytes em string
            if (texto_recebido == 'tchau'):
                print('vai encerrar o socket do cliente {} !'.format(addr[0]))
                arquivo.write("\nO usuario "+ nome_cliente + " acertou :" + str(resultadoTotal) + " / " + str(contador))
                porcentagem = round(float(resultadoTotal / contador * 100), 2)
                arquivo.write("\nPorcentagem de acertos: " + str(porcentagem) + "% ")
                arquivo.close()
                clientsocket.close() 
                return
            arquivo.write("\n" + texto_recebido + " ")
            texto_recebido = "Escreva em, no máximo, uma frase " + texto_recebido + " sem a utilizacao de acentos nas palavras"
            print('recebido do cliente {} na porta {}: {}'.format(addr[0], addr[1],texto_recebido))

            num = randint(0,9)

            if num % 2 == 0: #gpt

                url = "https://chatgpt-42.p.rapidapi.com/conversationgpt4-2"

                payload = {
                    "messages": [
		                {
			                "role": "user",
			                "content": texto_recebido
		                }
	                ],
	                "system_prompt": "",
	                "max_tokens": 90,
                }
                headers = {
	                #"x-rapidapi-key": "NEM FUDENDO QUE VCS VAO USAR MINHA CHAVE RYAN QUER ME FALIR SOCORRO",
	                "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
	                "Content-Type": "application/json"
                }

                response = requests.post(url, json=payload, headers=headers)
                response = str(response.json())
                print(response)
                semi_resposta = response.split(": '")
                resposta = semi_resposta[1].split("', '")
                resposta = resposta[0]
                print(resposta)
            
               

            else: #pessoa

                resposta = input("Escreva a resposta: ")
                numChute = 2

            clientsocket.send(resposta.encode())
            
            data2 = clientsocket.recv(BUFFER_SIZE)
            
            if not data2:
                break
            num_recebido = data2.decode('utf-8') # converte os bytes em string
            num_recebido = int(num_recebido)
            
            if num_recebido == numChute:
                resultado = 1
            else:
                resultado = 0
            
            resultado = str(resultado)
            
            clientsocket.send(resultado.encode())
            contador += 1
            resultadoTotal += int(resultado)
            arquivo.write(resposta)
            
            
        except Exception as error:
            print("Erro na conexão com o cliente!!")
            arquivo.close()
            return


def main(argv):
    try:
        # AF_INET: indica o protocolo IPv4. SOCK_STREAM: tipo de socket para TCP,
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            while True:
                server_socket.listen()
                clientsocket, addr = server_socket.accept()
                print('Conectado ao cliente no endereço:', addr)
                t = Thread(target=on_new_client, args=(clientsocket,addr))
                t.start()   
    except Exception as error:
        print("Erro na execução do servidor!!")
        print(error)        
        return             



if __name__ == "__main__":   
    main(sys.argv[1:])
