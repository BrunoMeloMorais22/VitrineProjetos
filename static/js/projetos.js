const linguagensSelecionadas = [];

document.querySelectorAll(".chip").forEach(chip => {
  chip.addEventListener("click", () => {
    chip.classList.toggle("ativo");

    const linguagem = chip.getAttribute("data-lang");

    if (chip.classList.contains("ativo")) {
      linguagensSelecionadas.push(linguagem);
    } else {
      const index = linguagensSelecionadas.indexOf(linguagem);
      if (index > -1) linguagensSelecionadas.splice(index, 1);
    }
  });
});

document.getElementById("form-projeto").addEventListener("submit", async function (e) {
  e.preventDefault();

  const form = e.target;
  const nomeProjeto = form.nomeProjeto.value.trim();
  const nomePessoaProjeto = form.nomePessoaProjeto.value.trim();
  const descricaoProjeto = form.descricaoProjeto.value.trim();
  const link = form.link.value.trim();

  if (!nomeProjeto || !descricaoProjeto || linguagensSelecionadas.length === 0) {
    document.getElementById("resultadoProjeto").innerText =
      "Preencha todos os campos e selecione pelo menos uma linguagem.";
    return;
  }
  const formData = new FormData(form);
  formData.set("linguagens", linguagensSelecionadas.join(","));

  try {
    const response = await fetch("/cadastrar_projeto", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    document.getElementById("resultadoProjeto").innerText = data.mensagem;

    if (data.mensagem === "Projeto cadastrado com sucesso") {
      form.reset();
      linguagensSelecionadas.length = 0;
      document.querySelectorAll(".chip").forEach(chip => chip.classList.remove("ativo"));

      setTimeout(() => {
        window.location.href = "/";
      }, 1500);
    }
  } catch (err) {
    document.getElementById("resultadoProjeto").innerText = "Erro ao cadastrar projeto.";
    console.error("Erro:", err);
  }
});
