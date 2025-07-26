

function selecionarPlano(plano){
    fetch('/selecionar-plano', {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ plano: plano})
    })
    .then(res => res.json())
    .then(data => {
        if(data.sucesso){
            alert("Plano selecionado com sucesso")
        }

        else{
            alert("Erro ao selecionar plano")
        }
    })
}