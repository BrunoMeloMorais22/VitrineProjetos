const abas = document.querySelectorAll(".abas a");
    const conteudos = document.querySelectorAll(".conteudo");

    abas.forEach(aba => {
      aba.addEventListener("click", function(e) {
        e.preventDefault();

        abas.forEach(a => a.classList.remove("ativa"));
        this.classList.add("ativa");

        conteudos.forEach(c => c.classList.remove("ativo"));

        const id = this.getAttribute("data-aba");
        document.getElementById(id).classList.add("ativo");
    });
});


document.getElementById("formSeguranca").addEventListener("submit", function(e){
    e.preventDefault()

    const senhaAtual = document.getElementById("senhaAtual").value
    const novaSenha = document.getElementById("novaSenha").value
    const confirmarSenha = document.getElementById("confirmarSenha").value

    fetch("/seguranca", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ senhaAtual, novaSenha, confirmarSenha }),
        credentials: "include"
    })
    .then(res => res.json())
    .then(data => {
      document.getElementById("resultadoSenha").innerText = data.mensagem

      if(data.mensagem === "Senha atualizada com sucesso"){
        document.getElementById("resultadoSenha").style.color = "green"

        setTimeout(() => {
          window.location.href = "/login"
        })
      }
      else{
        document.getElementById("resultadoSenha").innerText = "Senha atual incorreta"
        document.getElementById("resultadoSenha").style.color = "red"
      }
    })
    .catch(error => {
        alert("Erro ao atualizar senha", error)
    })
})

document.addEventListener("DOMContentLoaded", () => {
  const formNotificacoes = document.getElementById("formNotificacoes");


  fetch("/configuracoes/notificacoes")
    .then(res => res.json())
    .then(data => {
      if (data) {
        formNotificacoes.email_newsletter.checked = data.email_newsletter;
        formNotificacoes.email_alertas.checked = data.email_alertas;
        formNotificacoes.notificacao_projetos.checked = data.notificacao_projetos;
        formNotificacoes.notificacao_sistema.checked = data.notificacao_sistema;
        formNotificacoes.notificacao_suporte.checked = data.notificacao_suporte;
      }
    });

  // Salvar ao enviar
  formNotificacoes.addEventListener("submit", function (e) {
    e.preventDefault();
    const prefs = {
      email_newsletter: formNotificacoes.email_newsletter.checked,
      email_alertas: formNotificacoes.email_alertas.checked,
      notificacao_projetos: formNotificacoes.notificacao_projetos.checked,
      notificacao_sistema: formNotificacoes.notificacao_sistema.checked,
      notificacao_suporte: formNotificacoes.notificacao_suporte.checked
    };

    fetch("/configuracoes/notificacoes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(prefs)
    })
    .then(res => res.json())
    .then(data => {
      alert(data.mensagem);
    });
  });
});
