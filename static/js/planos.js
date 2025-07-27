

function selecionarPlano(plano, valor){
    fetch('/selecionar-plano', {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ plano: plano, valor:valor})
    })
    .then(res => res.json())
    .then(data => {
        if(data.sucesso){
            window.location.href = "/pagamento"
        }

        else{
            alert("Erro ao selecionar plano")
        }
    })
}