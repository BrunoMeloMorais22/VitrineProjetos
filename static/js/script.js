
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


var socket = io.connect("http://127.0.0.1:5000");


let contador = 0

document.addEventListener("DOMContentLoaded", function() {
    let savedUsername = localStorage.getItem("username")

    if(savedUsername){
        document.getElementById("username").value = savedUsername
    }
})

function toggleComentarios(){
    const section = document.getElementById("comentario-section")
    section.style.display = section.style.display === "none" ? "block" : "none"
}

socket.on("message", function(data){
    let chat = document.getElementById("chat")
    let div = document.createElement("div")
    let hora_atual = new Date();
    let hora_formatada = hora_atual.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    let data_formatada = hora_atual.toLocaleDateString('pt-BR');

    div.className = "comentario";

div.innerHTML = `
  
  <div class="mensagem">
    <strong> <i class="fa-solid fa-user"></i> ${data.username}</strong>
    <div class="texto-msg">${data.message}</div>
    <button onclick="editar(this)" class="editar-btn">Editar</button>
    <div style="font-size: 12px; color: gray; margin-top: 4px;">${data_formatada} às ${hora_formatada}</div>
  </div>
`;


chat.appendChild(div);

contador ++
      document.getElementById("contador-comentarios").textContent = contador
})

function sendMessage() {
      let username = document.getElementById("username").value.trim();
      let msg = document.getElementById("msg").value.trim();

      if (!username) {
        alert("Digite o nome de usuário");
        return;
      }

      localStorage.setItem("username", username);

      if (msg !== "") {
        socket.emit("message", { username: username, message: msg });
        document.getElementById("msg").value = "";
      }
    }

    function editar(botao) {
        const mensagemDiv = botao.parentElement;
        const msgTexto = mensagemDiv.querySelector('.texto-msg'); 
        if (botao.textContent === "Editar") {
          msgTexto.setAttribute("contenteditable", "true");
          msgTexto.focus();
          botao.textContent = "Salvar";
          msgTexto.style.backgroundColor = "#fff8dc";
        } else {
            msgTexto.setAttribute("contenteditable", "false");
            botao.textContent = "Editar";
            msgTexto.style.backgroundColor = "transparent";

            botao.remove()
        }
    }
