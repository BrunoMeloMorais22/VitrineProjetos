async function redefinir() {
    const novaSenha = document.getElementById("novaSenha").value;
    const feedback = document.getElementById("feedbackSenhaNova");

    if (!novaSenha) {
        feedback.innerText = "Por favor, insira a nova senha.";
        return;
    }

    try {
        const response = await fetch(window.location.pathname, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ novaSenha })
        });

        const data = await response.json();
        feedback.innerText = data.mensagem;
        feedback.style.color = "green";
        setTimeout(() => {
          window.location.href = "/login"
        })

    } catch (error) {
        console.error("Erro:", error);
        feedback.innerText = "Erro ao redefinir a senha. Tente novamente.";
        feedback.style.color = "red";
    }
}
