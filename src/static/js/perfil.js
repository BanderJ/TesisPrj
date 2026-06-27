    // Navigation entre secciones
    document.querySelectorAll('.perfil-nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.getAttribute('data-section');

            // Remover active de todos los links
            document.querySelectorAll('.perfil-nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Ocultar todas las secciones
            document.querySelectorAll('.perfil-section').forEach(s => {
                s.style.display = 'none';
            });

            // Mostrar solo la sección seleccionada
            const selectedSection = document.getElementById(section);
            if (selectedSection) {
                selectedSection.style.display = 'flex';
            }
        });
    });

    // Inicializar mostrando solo la primera sección (account-control)
    document.querySelectorAll('.perfil-section').forEach((s, index) => {
        s.style.display = index === 0 ? 'flex' : 'none';
    });

    // ─────────────────────────────────────────────────────────────
    // FORMULARIO: DATOS PERSONALES
    // ─────────────────────────────────────────────────────────────
    const formDatos = document.getElementById('formDatos');
    const btnGuardarDatos = document.getElementById('btnGuardarDatos');
    const nombre = document.getElementById('nombre');
    const apePaterno = document.getElementById('apePaterno');
    const apeMaterno = document.getElementById('apeMaterno');
    const telefono = document.getElementById('telefono');
    const correo = document.getElementById('correo');

    // Validación de teléfono - solo números
    telefono.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/[^0-9]/g, '');
    });

    btnGuardarDatos.addEventListener('click', async () => {
        if (!nombre.value.trim()) {
            CoffeeModal.error('El nombre es requerido.');
            return;
        }
        if (!apePaterno.value.trim()) {
            CoffeeModal.error('El apellido paterno es requerido.');
            return;
        }
        if (!apeMaterno.value.trim()) {
            CoffeeModal.error('El apellido materno es requerido.');
            return;
        }

        const telValue = telefono.value.trim();
        if (telValue && (telValue.length !== 9 || !/^\d+$/.test(telValue))) {
            CoffeeModal.error('El teléfono debe tener exactamente 9 dígitos.');
            return;
        }

        const correoValue = correo.value.trim();
        if (correoValue && !correoValue.includes('@')) {
            CoffeeModal.error('El correo debe ser válido.');
            return;
        }

        const payload = {
            nombre: nombre.value.trim(),
            ape_paterno: apePaterno.value.trim(),
            ape_materno: apeMaterno.value.trim(),
            telefono: telValue || null,
            correo: correoValue || null,
        };

        const btnOriginal = btnGuardarDatos.innerHTML;
        try {
            btnGuardarDatos.disabled = true;
            btnGuardarDatos.innerHTML = '<span style="opacity:0.7">Guardando...</span>';

            const res = await fetch('/perfil/datos-personales', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || 'Error al guardar');
            }

            CoffeeModal.success('Datos actualizados correctamente.', 'Cambios guardados');
        } catch (error) {
            CoffeeModal.error(error.message || 'No se pudo actualizar los datos.');
        } finally {
            btnGuardarDatos.disabled = false;
            btnGuardarDatos.innerHTML = btnOriginal;
        }
    });

    // ─────────────────────────────────────────────────────────────
    // FORMULARIO: CAMBIAR CONTRASEÑA
    // ─────────────────────────────────────────────────────────────
    const formContrasena = document.getElementById('formContrasena');
    const btnCambiarContrasena = document.getElementById('btnCambiarContrasena');
    const claveActual = document.getElementById('claveActual');
    const claveNueva = document.getElementById('claveNueva');
    const confirmarClave = document.getElementById('confirmarClave');

    // Validación de contraseña — usando CoffeeValidators
    CoffeeValidators.contrasena({
        inputEl:    'claveNueva',
        contadorEl: 'contadorNueva',
        max: 30,
        reqs: {
            length:    'req-length',
            uppercase: 'req-uppercase',
            number:    'req-number',
            special:   'req-special',
        },
    });

    CoffeeValidators.contrasena({
        inputEl:    'confirmarClave',
        contadorEl: 'contadorConfirmar',
        max: 30,
    });

    CoffeeValidators.confirmar({
        claveEl:     'claveNueva',
        confirmarEl: 'confirmarClave',
        matchEl:     'passwordMatch',
        matchTextEl: 'passwordMatchText',
    });

    btnCambiarContrasena.addEventListener('click', async () => {
        if (!claveActual.value) {
            CoffeeModal.error('Debes ingresar tu contraseña actual.');
            return;
        }
        if (!claveNueva.value || claveNueva.value.length < 8) {
            CoffeeModal.error('La nueva contraseña debe tener mínimo 8 caracteres.');
            return;
        }
        if (!confirmarClave.value) {
            CoffeeModal.error('Debes confirmar la nueva contraseña.');
            return;
        }
        if (claveNueva.value !== confirmarClave.value) {
            CoffeeModal.error('Las contraseñas no coinciden.');
            return;
        }

        const payload = {
            clave_actual: claveActual.value,
            clave_nueva: claveNueva.value,
            confirmar_clave: confirmarClave.value,
        };

        const btnOriginal = btnCambiarContrasena.innerHTML;
        try {
            btnCambiarContrasena.disabled = true;
            btnCambiarContrasena.innerHTML = '<span style="opacity:0.7">Procesando...</span>';

            const res = await fetch('/perfil/cambiar-contrasena', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || 'Error al cambiar contraseña');
            }

            CoffeeModal.success('Contraseña actualizada correctamente.', 'Cambio exitoso');

            setTimeout(() => {
                CoffeeModal.info(
                    'Debe reiniciar sesión con su nueva contraseña. Se cerrará la sesión ahora.',
                    'Por favor inicie sesión con su nueva contraseña'
                );

                setTimeout(() => {
                    window.location.href = '/auth/logout';
                }, 2500);
            }, 1500);
        } catch (error) {
            CoffeeModal.error(error.message || 'No se pudo cambiar la contraseña.');
        } finally {
            btnCambiarContrasena.disabled = false;
            btnCambiarContrasena.innerHTML = btnOriginal;
        }
    });
