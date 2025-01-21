        function atualizarPlacasModelos() {
            const motoristaSelecionado = document.getElementById('motorista').value;
            const placasSelect = document.getElementById('placa');

            // Limpa as opções anteriores
            placasSelect.innerHTML = '<option value="" disabled selected>Selecione a placa</option>';

            // Verifica se o motorista selecionado possui dados de placas
            if (motoristaSelecionado && dadosMotoristas[motoristaSelecionado]) {
                const placas = dadosMotoristas[motoristaSelecionado]['placas'];

                // Preenche as placas disponíveis
                placas.forEach(placa => {
                    const option = document.createElement('option');
                    option.value = placa;
                    option.textContent = placa;
                    placasSelect.appendChild(option);
                });

                // Se houver apenas uma placa, seleciona-a automaticamente
                if (placas.length === 1) {
                    placasSelect.value = placas[0];  // Seleciona a única opção de placa
                }
            }
        }