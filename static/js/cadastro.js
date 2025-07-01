

function fazerCadastro(event){
    event.preventDefault()

    let nomeCadastro = document.getElementById("nomeCadastro").value
    let emailCadastro = document.getElementById("emailCadastro").value
    let senhaCadastro = document.getElementById("senhaCadastro").value
    let confirmarSenha = document.getElementById("confirmarSenha").value
    let resultadoCadastro = document.getElementById("resultadoCadastro")

    fetch("/cadastro", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ nomeCadastro, emailCadastro, senhaCadastro, confirmarSenha })
    })
    .then(res => res.json())
    .then(data => {
        resultadoCadastro.innerHTML = data.mensagem

        if(data.mensagem === "Usuário cadastro com sucesso!"){
            resultadoCadastro.style.colo = "green"
            window.location.href = "/"
        }
        
        else{
            resultadoCadastro.style.color = "red"
        }
    })
    .catch(error => {
        resultadoCadastro.innerText = "Erro ao se conectar com o servidor"
        console.error(error)
    })
}

document.getElementById("btn-enviar").addEventListener("click", function(){
    let emailCadastro = document.getElementById("emailCadastro").value

    fetch("/enviar_email", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ emailCadastro })
    })
    .then(res => res.json())
    .then(data => {
        console.log("Email enviado", data)
    })

    .catch(error => {
        print("Erro ao enviar email", error)
    })
})