class Veiculo:
    def __init__(self, placa, motorista, modelo):
        self.placa = placa
        self.motorista = motorista
        self.modelo = modelo
        self.hodometro = None  # Inicializa o hodômetro como None
        self.hodometro_saida = None
        self.hora_entrada = None
        self.hora_saida = None

    
