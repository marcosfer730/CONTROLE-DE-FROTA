function adicionarMissao() { 
    document.getElementById('missao-coluna').classList.remove('d-none');
    let missoes = document.querySelectorAll('.missao-celula');
    missoes.forEach(function(celula) {
        celula.classList.remove('d-none');
    });
    document.querySelector('.assinaturas').classList.remove('d-none');
    window.print();
    document.querySelector('.assinaturas').classList.add('d-none');
}
