// Variáveis globais para dados do backend  
const listaMotoristas = {{ lista_motoristas | tojson | safe }};
const listaSetores = {{ lista_setores | tojson | safe }};
const listaViaturas = {{ lista_viaturas | tojson | safe }};

// Função para atualizar a seleção de motoristas
function atualizarMotoristas() {
    const motoristasSelect = document.getElementById('motorista');
    motoristasSelect.innerHTML = '<option value="" disabled selected>Selecione o motorista</option>';
    listaMotoristas.forEach(motorista => {
        const option = document.createElement('option');
        option.value = motorista;
        option.textContent = motorista;
        motoristasSelect.appendChild(option);
    });
}

// Função para atualizar a lista de setores
function atualizarSetores() {
    const setoresSelect = document.getElementById('setor');
    setoresSelect.innerHTML = '<option value="" disabled selected>Selecione o setor</option>';
    listaSetores.forEach(setor => {
        const option = document.createElement('option');
        option.value = setor;
        option.textContent = setor;
        setoresSelect.appendChild(option);
    });
}

// Função para atualizar a seleção de viaturas
function atualizarViaturas() {
    const veiculosSelect = document.getElementById('veiculo');
    veiculosSelect.innerHTML = '<option value="" disabled selected>Selecione a placa e modelo</option>';
    listaViaturas.forEach(viatura => {
        const option = document.createElement('option');
        option.value = viatura.placa;
        option.textContent = `${viatura.placa} - ${viatura.modelo}`;
        veiculosSelect.appendChild(option);
    });
}

// Chama as funções ao carregar a página
document.addEventListener("DOMContentLoaded", () => {
    atualizarMotoristas();
    atualizarSetores();
    atualizarViaturas();
});
