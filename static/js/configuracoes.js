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