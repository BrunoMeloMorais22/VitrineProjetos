
let projetoSelecionado = null
function denuncia(id) {
    projetoSelecionado = id
    document.getElementById('modalDenuncia').style.display = 'flex';
}

function fecharModal() {
    document.getElementById('modalDenuncia').style.display = 'none';
    document.body.classList.remove('fundo-desfocado');
}

function confirmarDenuncia() {
    const motivo = document.getElementById("motivoDenuncia").value

    if(!motivo){
        alert("Por favor, escreva o motivo da denúncia")
        return
    }

    fetch(`/denunciar/${projetoSelecionado}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ motivo })
    })
    .then(res =>{
        if(res.ok){
            alert("Denúncia enviada com sucesso")
        }
        else{
            alert("Erro ao enviar denúncia")
        }

        fecharModal()
    })
    .catch(err=>{
        console.error("Erro:", err)
        alert("Erro ao enviar denuncia")
        fecharModal()
    })
}

document.querySelectorAll(".fa-heart").forEach(coracao => {
    coracao.addEventListener("click", function () {
        const donoId = coracao.getAttribute("data-dono-id");

        coracao.classList.toggle("curtido");

        fetch(`/projeto_curtido/${donoId}`, {
            method: "POST"
        })
        .then(res => res.json())
        .then(data => {
            alert(data.mensagem);
        })
        .catch(err => {
            console.error("Erro ao curtir projeto", err);
            alert("Erro ao curtir o projeto");
        });
    });
});
