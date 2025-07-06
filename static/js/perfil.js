const toggle = document.getElementById('toggleTheme');
    toggle.addEventListener('change', () => {
      document.body.classList.toggle('dark-mode', toggle.checked);
});