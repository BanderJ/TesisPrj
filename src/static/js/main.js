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

        avatarBtn.addEventListener('click', () => {
            dropdownMenu.classList.toggle('active');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.user-menu-wrapper')) {
                dropdownMenu.classList.remove('active');
            }
        });

        // Navigation active state
        const currentPath = window.location.pathname === '/' ? '/inicio' : window.location.pathname;
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });

        // ── CoffeeModal: sistema de notificaciones global ──
        window.CoffeeModal = (() => {
            const _CFG = {
                success: { icon: 'M5 13l4 4L19 7',                                                                                        bg: 'rgba(22,163,74,0.15)',  color: '#16a34a', btn: '#16a34a', title: '¡Operación exitosa!' },
                error:   { icon: 'M6 18L18 6M6 6l12 12',                                                                                   bg: 'rgba(220,38,38,0.15)', color: '#dc2626', btn: '#dc2626', title: 'Ha ocurrido un error' },
                warning: { icon: 'M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z', bg: 'rgba(217,119,6,0.15)', color: '#d97706', btn: '#d97706', title: 'Atención' },
                info:    { icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',                                             bg: 'rgba(37,99,235,0.15)', color: '#2563eb', btn: '#2563eb', title: 'Información' },
            };

            const overlay    = document.getElementById('cm-overlay');
            const box        = document.getElementById('cm-box');
            const iconRing   = document.getElementById('cm-icon-ring');
            const iconSvg    = document.getElementById('cm-icon-svg');
            const titleEl    = document.getElementById('cm-title');
            const msgEl      = document.getElementById('cm-msg');
            const okBtn      = document.getElementById('cm-ok');
            const cancelBtn  = document.getElementById('cm-cancel');
            const progress   = document.getElementById('cm-progress');
            let _timer           = null;
            let _confirmResolve  = null;

            function _resetButtons() {
                cancelBtn.style.display = 'none';
                cancelBtn.style.flex    = '';
                okBtn.textContent       = 'Entendido';
                okBtn.style.flex        = '1';
            }

            function close(result = false) {
                clearTimeout(_timer);
                if (_confirmResolve) {
                    _confirmResolve(result);
                    _confirmResolve = null;
                }
                _resetButtons();
                box.style.opacity        = '0';
                box.style.transform      = 'scale(0.88) translateY(14px)';
                progress.style.animation = 'none';
                setTimeout(() => {
                    overlay.style.display = 'none';
                    overlay.setAttribute('aria-hidden', 'true');
                }, 260);
            }

            function _animate() {
                overlay.style.display = 'flex';
                overlay.setAttribute('aria-hidden', 'false');
                box.style.transition = 'none';
                box.style.opacity    = '0';
                box.style.transform  = 'scale(0.88) translateY(14px)';
                requestAnimationFrame(() => requestAnimationFrame(() => {
                    box.style.transition = 'transform 0.30s cubic-bezier(0.34,1.56,0.64,1), opacity 0.22s ease';
                    box.style.opacity    = '1';
                    box.style.transform  = 'scale(1) translateY(0)';
                }));
            }

            function show({ type = 'info', message = '', title = '', duration = 5500 }) {
                clearTimeout(_timer);
                _confirmResolve = null;
                const cfg = _CFG[type] || _CFG.info;

                iconRing.style.backgroundColor = cfg.bg;
                iconRing.style.color           = cfg.color;
                iconSvg.innerHTML              = `<path d="${cfg.icon}"/>`;
                titleEl.textContent            = title || cfg.title;
                msgEl.textContent              = message;
                okBtn.style.backgroundColor    = cfg.btn;
                progress.style.backgroundColor = cfg.btn;

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
                    const cfg = _CFG[type] || _CFG.warning;

                    iconRing.style.backgroundColor = cfg.bg;
                    iconRing.style.color           = cfg.color;
                    iconSvg.innerHTML              = `<path d="${cfg.icon}"/>`;
                    titleEl.textContent            = title || cfg.title;
                    msgEl.textContent              = message;
                    okBtn.style.backgroundColor    = cfg.btn;
                    progress.style.backgroundColor = cfg.btn;

                    okBtn.textContent       = okText;
                    okBtn.style.flex        = '1';
                    cancelBtn.textContent   = cancelText;
                    cancelBtn.style.display = 'block';
                    cancelBtn.style.flex    = '1';
                    progress.style.animation = 'none';

                    _animate();
                    setTimeout(() => cancelBtn.focus(), 80);
                });
            }

            okBtn.addEventListener('click',     () => close(true));
            cancelBtn.addEventListener('click',  () => close(false));
            document.getElementById('cm-close').addEventListener('click', () => close(false));
            overlay.addEventListener('click', e => { if (e.target === overlay) close(false); });
            document.addEventListener('keydown', e => { if (e.key === 'Escape') close(false); });

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
        // ── Términos y condiciones modal ──
        (() => {
            const overlay = document.getElementById('tc-overlay');
            const box     = document.getElementById('tc-box');

            function openTC() {
                overlay.style.display = 'flex';
                overlay.setAttribute('aria-hidden', 'false');
                box.style.transition = 'none';
                box.style.opacity    = '0';
                box.style.transform  = 'scale(0.92) translateY(14px)';
                requestAnimationFrame(() => requestAnimationFrame(() => {
                    box.style.transition = 'transform 0.28s cubic-bezier(0.34,1.56,0.64,1), opacity 0.20s ease';
                    box.style.opacity    = '1';
                    box.style.transform  = 'scale(1) translateY(0)';
                }));
            }

            function closeTC() {
                box.style.opacity   = '0';
                box.style.transform = 'scale(0.92) translateY(14px)';
                setTimeout(() => {
                    overlay.style.display = 'none';
                    overlay.setAttribute('aria-hidden', 'true');
                }, 240);
            }

            document.getElementById('btnTerminos').addEventListener('click', openTC);
            document.getElementById('tc-close').addEventListener('click', closeTC);
            document.getElementById('tc-ok').addEventListener('click', closeTC);
            overlay.addEventListener('click', e => { if (e.target === overlay) closeTC(); });
            document.addEventListener('keydown', e => {
                if (e.key === 'Escape' && overlay.style.display !== 'none') closeTC();
            });
        })();

        // ── Cargar información de cooperativa ──
        (async () => {
            try {
                const res = await fetch('/cooperativas/mi-cooperativa');

                if (res.status === 404) {
                    console.warn('Usuario sin cooperativa asociada');
                    return;
                }

                if (!res.ok) {
                    console.error('Error HTTP:', res.status, res.statusText);
                    return;
                }

                const data = await res.json();
                const header = document.getElementById('cooperativaHeader');
                const banner = document.getElementById('cooperativaBanner');
                const nombre = document.getElementById('cooperativaNombre');
                const desc = document.getElementById('cooperativaDescripcion');

                nombre.textContent = data.nombre || 'Cooperativa';
                desc.textContent = data.descripcion || '';

                if (data.imagen_url) {
                    banner.style.backgroundImage = `url('${data.imagen_url}')`;
                }

                header.style.display = 'block';
            } catch (error) {
                console.error('Error cargando cooperativa:', error);
            }
        })();
