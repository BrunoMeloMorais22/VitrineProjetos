
function denuncia() {
    document.getElementById('modalDenuncia').style.display = 'flex';
    document.body.classList.add('fundo-desfocado');
}

function fecharModal() {
    document.getElementById('modalDenuncia').style.display = 'none';
    document.body.classList.remove('fundo-desfocado');
}

function confirmarDenuncia() {
    alert("Projeto denunciado com sucesso!");
    fecharModal();
}