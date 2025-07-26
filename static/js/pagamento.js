
document.addEventListener("DOMContentLoaded", () => {
    const credito = document.getElementById("credito")
    const debito = document.getElementById("debito")
    const pix = document.getElementById("pix")

    document.getElementById("creditoBtn").addEventListener("click", () => {
        mostrarMetodo("credito")
    })

    document.getElementById("debitoBtn").addEventListener("click", () => {
        mostrarMetodo("debito")
    })

    document.getElementById("pixBtn").addEventListener("click", () => {
        mostrarMetodo("pix")
    })

    function mostrarMetodo(metodo) {
        credito.style.display = "none";
        debito.style.display = "none";
        pix.style.display = "none";

        document.getElementById(metodo).style.display = "block";
    }
})