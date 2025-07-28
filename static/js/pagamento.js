document.addEventListener("DOMContentLoaded", () => {
  const credito = document.getElementById("credito");
  const debito = document.getElementById("debito");
  const pix = document.getElementById("pix");
  const qrImagem = document.getElementById("qrImagem");

  const planosQR = {
    "39.90": "/static/image/pix-qrcode-1753729046655.png",
    "69.90": "/static/image/69.png"
  };

  function mostrarMetodo(metodo) {
    credito.style.display = "none";
    debito.style.display = "none";
    pix.style.display = "none";

    document.getElementById(metodo).style.display = "block";
  }

 function normalizarValor(valor) {
  valor = valor.replace("R$", "").replace(",", ".").trim();
  const numero = parseFloat(valor);
  return numero.toFixed(2);
}

  document.getElementById("creditoBtn").addEventListener("click", () => {
    mostrarMetodo("credito");
  });

  document.getElementById("debitoBtn").addEventListener("click", () => {
    mostrarMetodo("debito");
  });

  document.getElementById("pixBtn").addEventListener("click", () => {
    mostrarMetodo("pix");

    const valorBruto = document.getElementById("valorPagarPix").textContent;
    const valorLimpo = normalizarValor(valorBruto);

    if (planosQR[valorLimpo]) {
      qrImagem.src = planosQR[valorLimpo];
      qrImagem.alt = `QR Code Pix para R$ ${valorLimpo}`;
    } else {
      qrImagem.src = "";
      qrImagem.alt = "QR Code não disponível para esse valor.";
      console.warn("QR Code não encontrado para:", valorLimpo);
    }
  });
});
