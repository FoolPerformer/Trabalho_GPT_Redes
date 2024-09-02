import socket, sys, os


HOST = '127.0.0.1'  # endereço IP
PORT = 20000        # Porta utilizada pelo servidor
BUFFER_SIZE = 1024  # tamanho do buffer para recepção dos dados


def main(argv): 
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print("Servidor executando!")
            somaResultado = 0
            total = 0
            porcentagem = 0
            nome = input("Informe seu nome: ")
            s.send(nome.encode())
            while(True):       
                
                texto = input("Digite sua duvida (caso queira finalizar a conexao escreva tchau):\n")
                s.send(texto.encode()) #texto.encode - converte a string para bytes
                data = s.recv(BUFFER_SIZE)
                #texto_recebido = repr(data) #converte de bytes para um formato "printável"
                #print('Recebido', texto_recebido) testar no final o gpt, se os acentos ficarem apagar essa a linha comentada acima
                texto_string = data.decode('utf-8') #converte os bytes em string
                print('Recebido', texto_string)
                if (texto == 'tchau'):
                    print('\nEncerrando comunicação com o servidor, aperte qualquer tecla para finalizar!')
                    print("\nVoce acertou :" + str(somaResultado) + " / " + str(total))
                    porcentagem = round(float(somaResultado / total * 100), 2)
                    print("\nPorcentagem de acertos: " + str(porcentagem) + "% ")
                    os.system("pause")
                    s.close()
                    break
                chute = input("Quem escreveu a resposta? \n1 para chatGPT \n2 para Humano:\n")
                chute = str(chute)
                s.send(chute.encode()) #texto.encode - converte a string para byte
                numero = s.recv(BUFFER_SIZE)
                resultado = int(numero.decode('utf-8'))
                somaResultado = somaResultado + resultado
                total += 1
    except Exception as error:
        print("Exceção - Programa será encerrado!")
        print(error)
        return


if __name__ == "__main__":   
    main(sys.argv[1:])
