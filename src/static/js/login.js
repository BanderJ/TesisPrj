(() => {
    const savedMode = localStorage.getItem('theme') || 'light';
    document.body.classList.toggle('dark', savedMode === 'dark');

    const overlay = document.getElementById('rc-overlay');
    const abrirBtn = document.getElementById('btnOlvideClave');

    if (overlay && abrirBtn) {
        const cerrarBtn = document.getElementById('rc-close');
        const okBtn = document.getElementById('rc-ok');

        const abrirModal = () => {
            overlay.classList.add('is-open');
            overlay.setAttribute('aria-hidden', 'false');
            okBtn.focus();
        };

        const cerrarModal = () => {
            overlay.classList.remove('is-open');
            overlay.setAttribute('aria-hidden', 'true');
            abrirBtn.focus();
        };

        abrirBtn.addEventListener('click', abrirModal);
        cerrarBtn.addEventListener('click', cerrarModal);
        okBtn.addEventListener('click', cerrarModal);
        overlay.addEventListener('click', (event) => {
            if (event.target === overlay) {
                cerrarModal();
            }
        });
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && overlay.classList.contains('is-open')) {
                cerrarModal();
            }
        });
    }

    const passwordInput = document.getElementById('clave');
    const toggleButton = document.getElementById('toggleClaveBtn');
    const toggleIcon = document.getElementById('toggleClaveIcon');

    if (!passwordInput || !toggleButton || !toggleIcon) {
        return;
    }

    toggleButton.addEventListener('click', () => {
        const isHidden = passwordInput.type === 'password';
        passwordInput.type = isHidden ? 'text' : 'password';

        if (isHidden) {
            toggleButton.setAttribute('aria-label', 'Ocultar contraseña');
            toggleButton.setAttribute('aria-pressed', 'true');
            toggleIcon.src = '/static/icon/visibility_on.svg';
            toggleIcon.alt = 'Ocultar contraseña';
        } else {
            toggleButton.setAttribute('aria-label', 'Mostrar contraseña');
            toggleButton.setAttribute('aria-pressed', 'false');
            toggleIcon.src = '/static/icon/visibility_off.svg';
            toggleIcon.alt = 'Mostrar contraseña';
        }
    });
})();
