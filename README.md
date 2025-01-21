# Projeto Estacionamento

Este projeto é um sistema de gerenciamento de estacionamento com interface web. Ele utiliza Flask como framework principal, MongoDB para armazenamento de dados, e implementa diversas funcionalidades para gerenciar veículos, motoristas e relatórios.

## Funcionalidades
- Registro de entrada e saída de veículos.
- Gerenciamento de motoristas e viaturas.
- Relatórios de movimentação e pedidos de viaturas.
- Área restrita para administradores e usuários.

## Requisitos
- Python 3.8 ou superior
- MongoDB

## Configuração do Ambiente
1. Clone o repositório:
   ```bash
   git clone https://github.com/usuario/projeto_estacionamento.git
   cd projeto_estacionamento
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/MacOS
   .\venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

3. Certifique-se de que o MongoDB está em execução.

4. Inicie o servidor Flask:
   ```bash
   python app.py
   ```

## Estrutura do Projeto
```
projeto_estacionamento/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── models/
│   ├── estacionamento.py
│   └── veiculo.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── relatorios.csv
```

## Como Contribuir

1. Faça um fork deste repositório.
2. Crie uma branch para sua feature ou correção:
   ```bash
   git checkout -b minha-feature
   ```
3. Commit suas alterações:
   ```bash
   git commit -m "Adiciona minha nova feature"
   ```
4. Faça o push para sua branch:
   ```bash
   git push origin minha-feature
   ```
5. Abra um Pull Request.

## Licença
Este projeto está licenciado sob a [MIT License](LICENSE).


Se tiver dúvidas ou problemas, sinta-se à vontade para abrir uma issue no repositório.

