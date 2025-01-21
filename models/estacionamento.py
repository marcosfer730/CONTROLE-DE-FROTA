import os
from datetime import datetime
from models.veiculo import Veiculo

class Estacionamento:
    def __init__(self):
        self.veiculos = []
        self.log_file = 'relatorios.txt'
        self._criar_arquivo_log()  # Cria o arquivo no início, se não existir

    def _criar_arquivo_log(self):
        # Cria o arquivo se não existir
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("Placa,Motorista,Modelo,Hodômetro Entrada,Hodômetro Saída,Hora de Entrada,Hora de Saída\n")  # Cabeçalho

    def registrar_veiculo(self, veiculo: Veiculo):
        veiculo.hora_entrada = datetime.now()
        self.veiculos.append(veiculo)  # Adiciona o veículo após definir a hora de entrada
        self.registrar_saida_formatada(veiculo, entrada=True)
        print('Veículo registrado com sucesso!')

    def listar_veiculos(self):
        for veiculo in self.veiculos:
            print(f'Placa: {veiculo.placa}, Modelo: {veiculo.modelo}, Motorista: {veiculo.motorista}, Hora de Entrada: {veiculo.hora_entrada}')

    def exibir_relatorios(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                print("Relatórios de veículos registrados:")
                for linha in f:
                    print(linha.strip())
        else:
            print("Nenhum relatório encontrado.")

    def registrar_saida(self, placa, hodometro_saida):
        placa = placa.upper()  # Normaliza a placa para maiúsculas
        veiculo_encontrado = None
        
        # Busca o veículo pela placa
        for veiculo in self.veiculos:
            if veiculo.placa == placa:
                veiculo_encontrado = veiculo
                break

        # Verifica se o veículo foi encontrado
        if veiculo_encontrado is None:
            print('Veículo não encontrado pela placa: ' + placa)
            return None  # Retorna None se não encontrar o veículo

        # Atualiza a hora de saída e o hodômetro de saída
        veiculo_encontrado.hora_saida = datetime.now()
        veiculo_encontrado.hodometro_saida = hodometro_saida

        # Registra a saída de forma formatada
        self.registrar_saida_formatada(veiculo_encontrado, entrada=False)

        # Remove o veículo da lista de estacionados
        self.veiculos.remove(veiculo_encontrado)
        print('Saída do veículo registrada com sucesso!')

        return veiculo_encontrado  # Retorna o veículo que saiu

    def registrar_saida_formatada(self, veiculo, entrada=True):
        # Registra a entrada ou saída formatada no arquivo de log
        with open(self.log_file, 'a') as f:
            if entrada:
                # Registro de entrada
                f.write(f"{veiculo.placa},{veiculo.motorista},{veiculo.modelo},{veiculo.hodometro},-,{veiculo.hora_entrada.strftime('%d/%m/%Y %H:%M:%S')},-\n")
            else:
                # Atualiza a linha de saída
                f.write(f"{veiculo.placa},{veiculo.motorista},{veiculo.modelo},{veiculo.hodometro},{veiculo.hodometro_saida},{veiculo.hora_entrada.strftime('%d/%m/%Y %H:%M:%S')},{veiculo.hora_saida.strftime('%d/%m/%Y %H:%M:%S')}\n")
