# main.py -- put your code here!
import machine
import time

# Configuração do pino de entrada digital
pin_entrada = machine.Pin(14, machine.Pin.IN)  # Substitua o número do pino pelo pino que você está utilizando

while True:
    valor = pin_entrada.value()  # Lê o valor do pino de entrada
    print("Valor da entrada digital:", valor)  # Exibe o valor lido no console
    time.sleep(0.5)  # Aguarda meio segundo antes de ler novamente
