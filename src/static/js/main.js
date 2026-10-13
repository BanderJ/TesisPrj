        // Dark Mode Toggle
        const darkModeToggle = document.getElementById('darkModeToggle');
        const body = document.body;
        const sunIcon = document.getElementById('sunIcon');
        const moonIcon = document.getElementById('moonIcon');

        // Check for saved preference
        const savedMode = localStorage.getItem('theme') || 'light';
        body.classList.toggle('dark', savedMode === 'dark');
        updateDarkModeIcons();

        darkModeToggle.addEventListener('click', () => {
            const isDark = body.classList.toggle('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            updateDarkModeIcons();
        });

        function updateDarkModeIcons() {
            const isDark = body.classList.contains('dark');
            sunIcon.classList.toggle('hidden', !isDark);
            moonIcon.classList.toggle('hidden', isDark);
        }

        // Avatar Dropdown Toggle
        const avatarBtn = document.getElementById('avatarBtn');
        const dropdownMenu = document.getElementById('dropdownMenu');

        function setDropdown(abierto) {
            dropdownMenu.classList.toggle('active', abierto);
            avatarBtn.setAttribute('aria-expanded', String(abierto));
        }

        avatarBtn.addEventListener('click', () => {
            setDropdown(!dropdownMenu.classList.contains('active'));
        });

        // Close dropdown when clicking outside or pressing Escape
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.user-menu-wrapper')) setDropdown(false);
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && dropdownMenu.classList.contains('active')) {
                setDropdown(false);
                avatarBtn.focus();
            }
        });

        // Navigation active state
        const currentPath = window.location.pathname;
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });

        // ── CoffeeModal: sistema de notificaciones global ──
        // Estilos en main.css (.cm-*): el tono de cada tipo sale de data-type.
        window.CoffeeModal = (() => {
            const _CFG = {
                success: { icon: 'M5 13l4 4L19 7',                                                                                        title: 'Operación exitosa' },
                error:   { icon: 'M6 18L18 6M6 6l12 12',                                                                                   title: 'Ha ocurrido un error' },
                warning: { icon: 'M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z', title: 'Atención' },
                info:    { icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',                                             title: 'Información' },
            };

            const overlay    = document.getElementById('cm-overlay');
            const iconSvg    = document.getElementById('cm-icon-svg');
            const titleEl    = document.getElementById('cm-title');
            const msgEl      = document.getElementById('cm-msg');
            const okBtn      = document.getElementById('cm-ok');
            const cancelBtn  = document.getElementById('cm-cancel');
            const progress   = document.getElementById('cm-progress');
            let _timer           = null;
            let _hideTimer       = null;
            let _confirmResolve  = null;

            const _abierto = () => overlay.getAttribute('aria-hidden') === 'false';

            function _resetButtons() {
                cancelBtn.hidden  = true;
                okBtn.textContent = 'Entendido';
            }

            function close(result = false) {
                clearTimeout(_timer);
                if (_confirmResolve) {
                    _confirmResolve(result);
                    _confirmResolve = null;
                }
                _resetButtons();
                overlay.classList.add('is-closing');
                overlay.classList.remove('is-visible');
                progress.style.animation = 'none';
                _hideTimer = setTimeout(() => {
                    overlay.style.display = 'none';
                    overlay.classList.remove('is-closing');
                    overlay.setAttribute('aria-hidden', 'true');
                }, 160);
            }

            function _prepare(type, fallbackType, message, title) {
                const tipo = _CFG[type] ? type : fallbackType;
                overlay.dataset.type = tipo;
                iconSvg.innerHTML    = `<path d="${_CFG[tipo].icon}"/>`;
                titleEl.textContent  = title || _CFG[tipo].title;
                msgEl.textContent    = message;
            }

            function _animate() {
                clearTimeout(_hideTimer);  // cancela el ocultado pendiente de un close() reciente
                overlay.classList.remove('is-closing', 'is-visible');
                overlay.style.display = 'flex';
                overlay.setAttribute('aria-hidden', 'false');
                requestAnimationFrame(() => requestAnimationFrame(() => {
                    overlay.classList.add('is-visible');
                }));
            }

            function show({ type = 'info', message = '', title = '', duration = 5500 }) {
                clearTimeout(_timer);
                _confirmResolve = null;
                _prepare(type, 'info', message, title);
                _resetButtons();
                _animate();

                progress.style.animation = 'none';
                requestAnimationFrame(() => requestAnimationFrame(() => {
                    progress.style.animation = `cm-drain ${duration}ms linear forwards`;
                }));

                _timer = setTimeout(() => close(false), duration);
                setTimeout(() => okBtn.focus(), 80);
            }

            function confirm({ type = 'warning', message = '', title = '', okText = 'Sí', cancelText = 'No' }) {
                return new Promise(resolve => {
                    clearTimeout(_timer);
                    _confirmResolve = resolve;
                    _prepare(type, 'warning', message, title);

                    okBtn.textContent     = okText;
                    cancelBtn.textContent = cancelText;
                    cancelBtn.hidden      = false;
                    progress.style.animation = 'none';

                    _animate();
                    setTimeout(() => cancelBtn.focus(), 80);
                });
            }

            okBtn.addEventListener('click',     () => close(true));
            cancelBtn.addEventListener('click',  () => close(false));
            document.getElementById('cm-close').addEventListener('click', () => close(false));
            overlay.addEventListener('click', e => { if (e.target === overlay) close(false); });
            document.addEventListener('keydown', e => { if (e.key === 'Escape' && _abierto()) close(false); });

            return {
                show,
                confirm,
                success: (msg, ttl) => show({ type: 'success', message: msg, title: ttl }),
                error:   (msg, ttl) => show({ type: 'error',   message: msg, title: ttl, duration: 7000 }),
                warning: (msg, ttl) => show({ type: 'warning', message: msg, title: ttl }),
                info:    (msg, ttl) => show({ type: 'info',    message: msg, title: ttl }),
                close,
            };
        })();
        // ── Desglose del pago (análisis y reporte) ──
        // El backend ya calcula pago_base y bono_socio; aquí solo se arma el texto.
        // Vacío si la entrega no tuvo beneficio (externo o evaluación anterior al beneficio).
        window.CoffeePago = {
            detalle(d) {
                const bono = Number(d.bono_socio);
                if (!d.bono_socio || !(bono > 0) || d.pago_base == null) return '';
                return `Base S/ ${Number(d.pago_base).toFixed(2)} + beneficio socio S/ ${bono.toFixed(2)}`;
            },
            pintar(el, d) {
                const texto = this.detalle(d);
                el.textContent = texto;
                el.hidden = !texto;
            },
        };

        // ── Precios de café del día ──
        // Sin precios de hoy no se puede registrar una muestra (el backend lo
        // rechaza). Inicio y registro avisan con el mismo texto y la misma consulta.
        window.CoffeePrecios = {
            titulo: 'Precios de café pendientes',
            mensaje() {
                const base = 'No hay precios de café registrados hoy. Sin ellos no se puede registrar la muestra ni iniciar el monitoreo.';
                return document.body.hasAttribute('data-gestiona-precios')
                    ? `${base} Regístrelos en Valor de café para continuar.`
                    : `${base} Comunique al administrador o gerente que registre los precios del día para continuar.`;
            },
            /** true / false; null si no se pudo consultar (el backend sigue validando). */
            async hayPreciosHoy() {
                try {
                    const res = await fetch('/valor-cafe/resumen-rangos');
                    if (!res.ok) return null;
                    const { data } = await res.json();
                    return Array.isArray(data) && data.length > 0;
                } catch {
                    return null;
                }
            },
            avisar() {
                CoffeeModal.warning(this.mensaje(), this.titulo);
            },
            /** Avisa si hoy no hay precios. Devuelve true si avisó. */
            async avisarSiFaltan() {
                if (await this.hayPreciosHoy() !== false) return false;
                this.avisar();
                return true;
            },
        };

        // ── Términos y condiciones modal ──
        (() => {
            // Estilos y transición en main.css (.tc-*), mismo patrón que CoffeeModal
            const overlay = document.getElementById('tc-overlay');
            let _hideTimer = null;

            function openTC() {
                clearTimeout(_hideTimer);
                overlay.classList.remove('is-closing', 'is-visible');
                overlay.style.display = 'flex';
                overlay.setAttribute('aria-hidden', 'false');
                requestAnimationFrame(() => requestAnimationFrame(() => {
                    overlay.classList.add('is-visible');
                }));
            }

            function closeTC() {
                overlay.classList.add('is-closing');
                overlay.classList.remove('is-visible');
                _hideTimer = setTimeout(() => {
                    overlay.style.display = 'none';
                    overlay.classList.remove('is-closing');
                    overlay.setAttribute('aria-hidden', 'true');
                }, 160);
            }

            document.getElementById('btnTerminos').addEventListener('click', openTC);
            document.getElementById('tc-close').addEventListener('click', closeTC);
            document.getElementById('tc-ok').addEventListener('click', closeTC);
            overlay.addEventListener('click', e => { if (e.target === overlay) closeTC(); });
            document.addEventListener('keydown', e => {
                if (e.key === 'Escape' && overlay.getAttribute('aria-hidden') === 'false') closeTC();
            });
        })();

        // === Toggle ver/ocultar contraseña (delegado, reutilizable) ===
        // Cualquier página: envolver el input en .password-wrapper y agregar
        // un botón .password-toggle-btn con img .password-toggle-icon
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.password-toggle-btn');
            if (!btn) return;
            const input = btn.closest('.password-wrapper')?.querySelector('input');
            const icon = btn.querySelector('.password-toggle-icon');
            if (!input || !icon) return;

            const mostrar = input.type === 'password';
            input.type = mostrar ? 'text' : 'password';
            icon.src = mostrar ? '/static/icon/visibility_on.svg' : '/static/icon/visibility_off.svg';
            btn.setAttribute('aria-label', mostrar ? 'Ocultar contraseña' : 'Mostrar contraseña');
            btn.setAttribute('aria-pressed', String(mostrar));
        });
