function fazerCadastro(event) {
    event.preventDefault();

    let nomeCadastro = document.getElementById("nomeCadastro").value;
    let emailCadastro = document.getElementById("emailCadastro").value;
    let senhaCadastro = document.getElementById("senhaCadastro").value;
    let confirmarSenha = document.getElementById("confirmarSenha").value;
    let resultadoCadastro = document.getElementById("resultadoCadastro");
    
    let recaptcha_response = grecaptcha.getResponse()

    if(recaptcha_response === ""){
        resultadoCadastro.innerText = "Por favor, confirme que você não é um robô"
        resultadoCadastro.style.color = "red"
        return
    }

    fetch("/cadastro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nomeCadastro, emailCadastro, senhaCadastro, confirmarSenha, "g-recaptcha-response": recaptcha_response })
    })
    .then(res => res.json())
    .then(data => {
        resultadoCadastro.innerHTML = data.mensagem;

        if (data.mensagem === "Usuário cadastrado com sucesso!") {
            resultadoCadastro.style.color = "green";

            fetch("/enviar_email", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ emailCadastro })
            })
            .then(res => res.json())
            .then(data => {
                console.log("Email enviado:", data);
                window.location.href = "/login";
            })
            .catch(error => {
                console.error("Erro ao enviar email", error);
            });
        } else {
            resultadoCadastro.style.color = "red";
        }

        grecaptcha.reset()
    })
    .catch(error => {
        resultadoCadastro.innerText = "Erro ao se conectar com o servidor";
        console.error(error);
    });
}
