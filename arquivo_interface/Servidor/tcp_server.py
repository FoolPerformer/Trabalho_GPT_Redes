import socket
import sys
from threading import Thread
import requests
import os

HOST = '127.0.0.1'
PORT = 20000
BUFFER_SIZE = 1024

# Função para ordenar o ranking
def my_sort(line):
    line_fields = line.strip().replace("%", "").split(':')
    amount = float(line_fields[1])
    return amount

def on_new_client(clientsocket, addr):
    nome_cod = clientsocket.recv(BUFFER_SIZE)
    nome_cliente = nome_cod.decode('utf-8') if nome_cod else "Nome nao informado"

    # Caminhos para os arquivos ajustados para a estrutura mostrada
    caminho_diretorio = os.path.join(os.path.dirname(__file__), "Data")
    arquivo_path = os.path.join(caminho_diretorio, "datateste.txt")
    ranking_path = os.path.join(caminho_diretorio, "ranking.txt")

    # Criação dos arquivos se não existirem
    os.makedirs(caminho_diretorio, exist_ok=True)

    # Manipulação dos arquivos de forma mais robusta
    with open(arquivo_path, "a+") as arquivo, open(ranking_path, "a+") as ranking:
        arquivo.write("\nNome: " + nome_cliente)
        contador = 0
        resultadoTotal = 0
        cont = 0

        while True:
            try:
                data = clientsocket.recv(BUFFER_SIZE)
                if not data:
                    break
                texto_recebido = data.decode('utf-8')
                if texto_recebido == 'tchau':
                    print(f'Encerrando o socket do cliente {addr[0]}!')
                    arquivo.write(f"\nO usuario {nome_cliente} acertou: {resultadoTotal} / {contador}")
                    if contador >= 5:
                        # Atualiza o ranking
                        porcentagem = round((resultadoTotal / contador) * 100, 2)
                        ranking.write(f"{nome_cliente}: {porcentagem}%\n")

                        # Reorganiza o ranking
                        ranking.close()
                        with open(ranking_path, "r") as ranking_read:
                            ordenado = ranking_read.readlines()
                        ordenado.sort(key=my_sort, reverse=True)
                        with open(ranking_path, "w") as ranking_write:
                            ranking_write.writelines(ordenado)

                    clientsocket.send(str(cont).encode())
                    clientsocket.close()
                    return

                # Processa a resposta
                arquivo.write("\nPergunta: " + texto_recebido + " | Resposta: ")
                print(f'Recebido do cliente {addr[0]} na porta {addr[1]}: {texto_recebido}')

                escolha = input("Quem vai responder? \n1 para chatGPT \n2 para Humano\n")

                if int(escolha) == 1:  # Resposta via ChatGPT
                    url = "https://chatgpt-42.p.rapidapi.com/conversationgpt4-2"
                    payload = {
                        "messages": [{"role": "user", "content": texto_recebido}],
                        "system_prompt": "",
                        "max_tokens": 90,
                    }
                    headers = {
                        "x-rapidapi-key": "sua chave aqui",
                        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
                        "Content-Type": "application/json"
                    }
                    response = requests.post(url, json=payload, headers=headers)
                    response_json = response.json()

                    # Verifica a resposta da API
                    if response_json.get("error") == "server is busy":
                        resposta = "Servidor ocupado. Tente novamente mais tarde."
                    else:
                        semi_resposta = response_json.get('choices', [{}])[0].get('message', {}).get('content', '')
                        resposta = semi_resposta.strip() if semi_resposta else "Erro ao obter resposta da API."

                    numChute = 1
                else:  # Resposta manual
                    resposta = input("Escreva a resposta: ")
                    numChute = 2

                # Envia a resposta ao cliente
                clientsocket.send(resposta.encode())

                # Recebe a resposta do cliente
                data2 = clientsocket.recv(BUFFER_SIZE)
                if not data2:
                    break
                num_recebido = int(data2.decode('utf-8'))

                # Verifica se a resposta foi correta
                resultado = 1 if num_recebido == numChute else 0
                resultado_texto = "acertou o chute" if resultado == 1 else "errou o chute"
                arquivo.write(resposta + " | " + resultado_texto)
                clientsocket.send(str(resultado).encode())

                # Atualiza contadores
                contador += 1
                resultadoTotal += resultado

            except Exception as error:
                print("Erro na conexão com o cliente!!", error)
                arquivo.close()
                return

def main(argv):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            while True:
                server_socket.listen()
                clientsocket, addr = server_socket.accept()
                print('Conectado ao cliente no endereço:', addr)
                t = Thread(target=on_new_client, args=(clientsocket, addr))
                t.start()
    except Exception as error:
        print("Erro na execução do servidor!!", error)

if __name__ == "__main__":
    main(sys.argv[1:])
