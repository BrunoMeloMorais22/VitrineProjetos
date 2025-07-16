

function fazerLogin(event){
    event.preventDefault()

    let emailLogin = document.getElementById("emailLogin").value
    let senhaLogin = document.getElementById("senhaLogin").value
    let resultadoLogin = document.getElementById("resultadoLogin")

    fetch("/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ emailLogin, senhaLogin }),
        credentials: "include"
    })
    .then(res => res.json())
    .then(data => {
        resultadoLogin.innerHTML = data.mensagem

        if(data.mensagem === "Login efetuado com sucesso"){
            resultadoLogin.style.color = "green"
            resultadoLogin.style.fontWeight = "bold"
            
            setTimeout(() => {
                if(data.admin === "ajuda"){
                    window.location.href = "/admin/ajuda"
                }

                else if(data.admin === "denuncia"){
                    window.location.href = "/painel_admin"
                }

                else{
                    window.location.href = "/"
                }
            }, 2000)
        }
        
        else{
            resultadoLogin.style.color = "red"
        }
    })
    .catch(error => {
        resultadoLogin.innerText = "Erro ao se conectar com o servidor"
        console.error(error)
    })
}