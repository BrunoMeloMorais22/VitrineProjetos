document.addEventListener("DOMContentLoaded", function () {
    let projetoSelecionado = null;

    window.denuncia = function (id) {
        projetoSelecionado = id;
        document.getElementById('modelExcluir').classList.add('show');
    };

    window.fecharModal = function () {
        document.getElementById('modelExcluir').classList.remove('show');
    };

    window.confirmarDenuncia = function () {
        fetch(`/excluir/${projetoSelecionado}`, {
            method: "POST"
        })
        .then(res => {
            if (res.ok) {
                alert("Projeto excluído com sucesso");
                location.reload();
            } else {
                alert("Erro ao excluir projeto");
            }
        })
        .catch(err => {
            console.error("Erro:", err);
            alert("Erro ao excluir projeto");
        });

        fecharModal();
    };
});
