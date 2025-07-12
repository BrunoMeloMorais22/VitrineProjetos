
document.getElementById("formAjuda").addEventListener("submit", async function(e){
    e.preventDefault()

    const mensagem = document.getElementById("mensagemAjuda").value

    const resposta = await fetch("/enviar_ajuda", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ mensagem })
    })

    const resultado = await resposta.json()
    document.getElementById("respostaStatus").textContent = resultado.mensagem
    document.getElementById("formAjuda").reset()
})