    let cooperativaId = null;
    let tiposPersonal = [];
    let tiposDocumento = [];

    // === Contador descripción ===
    document.getElementById('descripcion').addEventListener('input', function () {
        document.getElementById('contadorDescripcion').textContent = `${this.value.length}/255`;
    });

    // === Navegación entre secciones ===
    document.querySelectorAll('.perfil-nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.getAttribute('data-section');

            // Remover active de todos los links
            document.querySelectorAll('.perfil-nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Ocultar todas las secciones
            document.querySelectorAll('.perfil-section').forEach(s => {
                s.hidden = true;
            });

            // Mostrar solo la sección seleccionada
            const selectedSection = document.getElementById(section);
            if (selectedSection) {
                selectedSection.hidden = false;
                if (section === 'tipos-grano') {
                    cargarTiposGrano();
                } else if (section === 'bono-socio') {
                    cargarBonoSocio();
                } else if (section === 'usuarios') {
                    cargarUsuarios();
                } else if (section === 'caficultores') {
                    cargarCaficultores();
                } else if (section === 'auditoria') {
                    inicializarAuditoria();
                } else if (section === 'reportes') {
                    inicializarReportes();
                }
            }
        });
    });

    // === Cargar información inicial ===
    async function cargarCooperativa() {
        const loadingState = document.getElementById('loadingState');

        try {
            const res = await fetch('/cooperativas/mi-cooperativa');
            if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo cargar la cooperativa.'));

            const data = await res.json();
            cooperativaId = data.cooperativa_id;

            // Llenar formulario básico
            document.getElementById('nombre').value = data.nombre || '';
            document.getElementById('codigo').value = data.codigo || '';
            document.getElementById('direccion').value = data.ubicacion || '';
            document.getElementById('telefono').value = data.telefono || '';
            document.getElementById('correo').value = data.correo || '';
            const descEl = document.getElementById('descripcion');
            descEl.value = data.descripcion || '';
            document.getElementById('contadorDescripcion').textContent = `${descEl.value.length}/255`;
            document.getElementById('imagen_url').value = data.imagen_url || '';

            if (data.imagen_url) {
                document.getElementById('imagenPreview').src = data.imagen_url;
                document.getElementById('previewContainer').hidden = false;
            }

            // Mostrar secciones de admin
            if (isAdmin) {
                document.getElementById('navTiposGrano').hidden = false;
                document.getElementById('navBonoSocio').hidden = false;
                document.getElementById('navUsuarios').hidden = false;
                document.getElementById('navCaficultores').hidden = false;
                document.getElementById('navAuditoria').hidden = false;
                document.getElementById('navReportes').hidden = false;
                await cargarCatalogos();
            }

            loadingState.hidden = true;
            document.querySelector('.perfil-section').hidden = false;

        } catch (error) {
            console.error('Error:', error);
            loadingState.innerHTML = `<p style="color: var(--destructive);">${error.message}</p>`;
        }
    }

    // === Cargar catálogos ===
    async function cargarCatalogos() {
        try {
            const resTipos = await fetch('/tipo-personal/listar');
            const resDocumentos = await fetch('/tipo-documento/listar');

            if (resTipos.ok) {
                tiposPersonal = await resTipos.json();
                const select = document.getElementById('crearTipoPersonal');
                tiposPersonal.forEach(tipo => {
                    const option = document.createElement('option');
                    option.value = tipo.id;
                    option.textContent = tipo.nombre;
                    select.appendChild(option);
                });
            }

            if (resDocumentos.ok) {
                tiposDocumento = await resDocumentos.json();
                const select = document.getElementById('crearTipoDocumento');
                tiposDocumento.forEach(doc => {
                    const option = document.createElement('option');
                    option.value = doc.id;
                    option.textContent = doc.nombre;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error cargando catálogos:', error);
        }
    }

    // === Tipos de grano ===
    const modalTipoGrano = document.getElementById('modalTipoGrano');
    let modoTipoGrano = 'crear'; // 'crear' | 'editar'
    let tipoGranoIdEditando = null;

    function abrirModalTipoGrano(modo, datos = null) {
        modoTipoGrano = modo;
        tipoGranoIdEditando = datos?.id || null;
        const titulo = document.getElementById('modalTipoGranoTitulo');
        const btnGuardar = document.getElementById('btnGuardarTipoGrano');
        document.getElementById('formTipoGranoModal').reset();

        if (modo === 'crear') {
            titulo.textContent = 'Agregar tipo de grano';
            btnGuardar.textContent = 'Agregar tipo';
        } else {
            titulo.textContent = 'Editar tipo de grano';
            btnGuardar.textContent = 'Guardar cambios';
            document.getElementById('modalTipoNombre').value = datos.nombre || '';
            document.getElementById('modalTipoPeso').value = datos.peso_qq || '';
        }

        modalTipoGrano.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        document.getElementById('modalTipoNombre').focus();
    }

    function cerrarModalTipoGrano() {
        modalTipoGrano.style.display = 'none';
        document.body.style.overflow = '';
        document.getElementById('formTipoGranoModal').reset();
    }

    document.getElementById('btnCerrarModalTipoGrano').addEventListener('click', cerrarModalTipoGrano);
    document.getElementById('btnCancelarTipoGrano').addEventListener('click', cerrarModalTipoGrano);
    modalTipoGrano.addEventListener('click', (e) => { if (e.target === modalTipoGrano) cerrarModalTipoGrano(); });

    document.getElementById('btnAbrirCrearTipoGrano').addEventListener('click', () => abrirModalTipoGrano('crear'));

    document.getElementById('btnGuardarTipoGrano').addEventListener('click', async () => {
        const nombre = document.getElementById('modalTipoNombre').value.trim();
        const peso = parseFloat(document.getElementById('modalTipoPeso').value);

        if (!nombre || isNaN(peso) || peso <= 0) {
            CoffeeModal.warning('Completa el nombre y un peso válido.');
            return;
        }

        const btn = document.getElementById('btnGuardarTipoGrano');
        const btnLabel = btn.textContent;
        btn.disabled = true;
        btn.innerHTML = '<span style="opacity:.7">Guardando...</span>';

        try {
            let res;
            if (modoTipoGrano === 'crear') {
                res = await fetch('/tipo-grano/crear', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nombre, peso_qq: peso }),
                });
            } else {
                res = await fetch(`/tipo-grano/${tipoGranoIdEditando}`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nombre, peso_qq: peso }),
                });
            }

            if (!res.ok) {
                throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo guardar el tipo de grano.'));
            }

            CoffeeModal.success(modoTipoGrano === 'crear' ? 'Tipo de grano creado' : 'Tipo de grano actualizado');
            cerrarModalTipoGrano();
            await cargarTiposGrano();
        } catch (error) {
            CoffeeModal.error(error.message);
        } finally {
            btn.disabled = false;
            btn.textContent = btnLabel;
        }
    });

    function escapeHtml(texto) {
        return String(texto ?? '').replace(/[&<>"']/g, (c) => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
        }[c]));
    }

    // === Beneficio de socio ===
    // El backend guarda cada cambio como un registro nuevo; aquí solo se muestra.
    function pintarBonoSocio(data) {
        const vigente = data.vigente;
        document.getElementById('bonoVigenteMonto').textContent =
            vigente ? `S/ ${Number(vigente.monto).toFixed(2)}` : 'Sin configurar';
        document.getElementById('bonoVigenteDetalle').textContent =
            vigente ? `Desde ${vigente.fecha}${vigente.registrado_por ? ' · ' + vigente.registrado_por : ''}` : '';

        const tbody = document.getElementById('bonoHistorialBody');
        if (!data.historial.length) {
            tbody.innerHTML = '<tr><td colspan="3" class="tabla-vacia">Todavía no hay cambios registrados</td></tr>';
            return;
        }
        tbody.innerHTML = data.historial.map(h => `
            <tr>
                <td>${escapeHtml(h.fecha)}</td>
                <td class="celda-num">${Number(h.monto).toFixed(2)}</td>
                <td>${escapeHtml(h.registrado_por || '—')}</td>
            </tr>
        `).join('');
    }

    async function cargarBonoSocio() {
        try {
            const res = await fetch('/bono-socio');
            if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo cargar el beneficio de socio.'));
            pintarBonoSocio(await res.json());
        } catch (error) {
            CoffeeModal.error(error.message);
        }
    }

    const bonoInput = document.getElementById('bonoMonto');
    const bonoHint  = document.getElementById('bonoMontoHint');

    function validarBonoMonto() {
        const valor = bonoInput.value.trim();
        let mensaje = '';
        if (valor === '') mensaje = 'Ingrese el monto.';
        else if (!/^\d{1,5}(\.\d{1,2})?$/.test(valor)) mensaje = 'Use un monto válido con hasta 2 decimales.';
        bonoHint.textContent = mensaje;
        return !mensaje;
    }

    bonoInput.addEventListener('input', validarBonoMonto);

    document.getElementById('formBonoSocio').addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!validarBonoMonto()) return;
        const monto = Number(bonoInput.value).toFixed(2);
        const ok = await CoffeeModal.confirm({
            title: 'Cambiar beneficio de socio',
            message: `Las entregas de socios que se completen desde ahora recibirán S/ ${monto}. Las evaluaciones anteriores no cambian.`,
            okText: 'Guardar',
            cancelText: 'Cancelar',
        });
        if (!ok) return;

        const btn = document.getElementById('btnGuardarBono');
        const textoOriginal = btn.innerHTML;
        btn.disabled = true;
        btn.textContent = 'Guardando…';
        try {
            const res = await fetch('/bono-socio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ monto }),
            });
            if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo guardar el beneficio de socio.'));
            pintarBonoSocio(await res.json());
            bonoInput.value = '';
            bonoHint.textContent = '';
            CoffeeModal.success(`El beneficio de socio ahora es S/ ${monto} por entrega.`);
        } catch (error) {
            CoffeeModal.error(error.message);
        } finally {
            btn.disabled = false;
            btn.innerHTML = textoOriginal;
        }
    });

    async function cargarTiposGrano() {
        const tbody = document.getElementById('tiposGranoBody');
        try {
            const res = await fetch('/tipo-grano/listar');
            if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudieron cargar los tipos de grano.'));

            const tipos = await res.json();
            if (tipos.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;padding:2rem;color:var(--muted-foreground);">No hay tipos de grano registrados</td></tr>';
                return;
            }

            // data-* en vez de interpolar en onclick: un nombre con comillas
            // (ej. "Piloto's") rompía el atributo generado y el botón dejaba
            // de funcionar (o ejecutaba HTML/JS arbitrario inyectado en el nombre).
            tbody.innerHTML = tipos.map(tipo => `
                <tr>
                    <td><strong>${escapeHtml(tipo.nombre)}</strong></td>
                    <td>${tipo.peso_qq}</td>
                    <td class="acciones-celda">
                        <button type="button" class="btn-tabla btn-editar-tipo" data-id="${tipo.id}" data-nombre="${escapeHtml(tipo.nombre)}" data-peso="${tipo.peso_qq}">Editar</button>
                        <button type="button" class="btn-tabla btn-inactivar btn-eliminar-tipo" data-id="${tipo.id}">Eliminar</button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            console.error('Error:', error);
            tbody.innerHTML = `<tr><td colspan="3" style="text-align:center;padding:2rem;color:var(--destructive);">Error: ${error.message}</td></tr>`;
        }
    }

    document.getElementById('tiposGranoBody').addEventListener('click', (e) => {
        const btnEditar = e.target.closest('.btn-editar-tipo');
        if (btnEditar) {
            editarTipo(Number(btnEditar.dataset.id), btnEditar.dataset.nombre, Number(btnEditar.dataset.peso));
            return;
        }
        const btnEliminar = e.target.closest('.btn-eliminar-tipo');
        if (btnEliminar) eliminarTipo(Number(btnEliminar.dataset.id));
    });

    function editarTipo(tipoId, nombre, peso) {
        abrirModalTipoGrano('editar', { id: tipoId, nombre, peso_qq: peso });
    }

    window.eliminarTipo = async function(tipoId) {
        const ok = await CoffeeModal.confirm({
            message: '¿Eliminar este tipo de grano?',
            okText: 'Sí, eliminar',
            cancelText: 'Cancelar',
        });
        if (!ok) return;

        try {
            const res = await fetch(`/tipo-grano/${tipoId}`, { method: 'DELETE' });
            if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo eliminar el tipo de grano.'));
            CoffeeModal.success('Tipo eliminado');
            await cargarTiposGrano();
        } catch (error) {
            CoffeeModal.error(error.message);
        }
    };

// Guardar cambios básicos
    document.getElementById('formBasicos').addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const btnOriginal = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span style="opacity:0.7">Guardando...</span>';

        try {
            const res = await fetch(`/cooperativas/${cooperativaId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nombre: document.getElementById('nombre').value,
                    codigo: document.getElementById('codigo').value || null,
                    ubicacion: document.getElementById('direccion').value || null,
                    telefono: document.getElementById('telefono').value || null,
                    correo: document.getElementById('correo').value || null,
                    descripcion: document.getElementById('descripcion').value || null,
                    imagen_url: document.getElementById('imagen_url').value || null,
                }),
            });

            if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo actualizar la cooperativa.'));
            CoffeeModal.success('Cooperativa actualizada');
        } catch (error) {
            CoffeeModal.error(error.message);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = btnOriginal;
        }
    });

    document.getElementById('imagen_file').addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            const formData = new FormData();
            formData.append('file', file);
            const res = await fetch('/cooperativas/upload-imagen', {
                method: 'POST',
                body: formData
            });
            if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo subir la imagen.'));
            const data = await res.json();
            document.getElementById('imagenPreview').src = data.imagen_url;
            document.getElementById('imagen_url').value = data.imagen_url;
            document.getElementById('previewContainer').hidden = false;
        } catch (error) {
            CoffeeModal.error(error.message);
        }
    });

    // === Usuarios ===
    const crearTipoDocumento = document.getElementById('crearTipoDocumento');
    const crearNumDocumento = document.getElementById('crearNumDocumento');
    const buscarEstado = document.getElementById('buscarEstado');
    const crearNombre = document.getElementById('crearNombre');
    const crearApePaterno = document.getElementById('crearApePaterno');
    const crearApeMaterno = document.getElementById('crearApeMaterno');
    const crearSexo = document.getElementById('crearSexo');
    const crearFechaNacimiento = document.getElementById('crearFechaNacimiento');
    const crearTelefono = document.getElementById('crearTelefono');
    const crearDepartamento = document.getElementById('crearDepartamento');
    const crearProvincia = document.getElementById('crearProvincia');
    const crearDistrito = document.getElementById('crearDistrito');
    const crearCorreo = document.getElementById('crearCorreo');
    const crearUsuarioPreview = document.getElementById('crearUsuarioPreview');
    const formCrearUsuario = document.getElementById('formUsuarioModal');
    const btnGuardarUsuario = document.getElementById('btnGuardarUsuario');
    const buscadorUsuarios = document.getElementById('buscadorUsuarios');
    const usuariosTableBody = document.getElementById('usuariosTableBody');

    // === Modal usuario ===
    const modalUsuario = document.getElementById('modalUsuario');
    let modoModal = 'crear'; // 'crear' | 'editar'
    let personalIdEditando = null;

    async function abrirModal(modo, datos = null) {
        modoModal = modo;
        personalIdEditando = datos?.personal_id || null;

        const titulo = document.getElementById('modalUsuarioTitulo');
        const bloqueBusqueda = document.getElementById('bloquesBusqueda');
        const labelClave = document.getElementById('labelClave');
        const labelConfirmar = document.getElementById('labelConfirmarClave');
        const nota = document.getElementById('modalNotaUsuario');

        if (modo === 'crear') {
            titulo.textContent = 'Crear usuario';
            bloqueBusqueda.style.display = '';
            labelClave.textContent = 'Contraseña *';
            labelConfirmar.textContent = 'Confirmar Contraseña *';
            document.getElementById('crearContrasena').required = true;
            nota.style.display = '';
            formCrearUsuario.reset();
            crearUsuarioPreview.value = '';
            document.getElementById('buscarEstado').className = 'buscar-estado';
            document.getElementById('buscarEstado').innerHTML = '<span>Ingresa el documento para buscar datos de la persona.</span>';
            btnGuardarUsuario.textContent = 'Crear usuario';
        } else {
            titulo.textContent = 'Editar usuario';
            bloqueBusqueda.style.display = 'none';
            labelClave.textContent = 'Nueva contraseña (opcional)';
            labelConfirmar.textContent = 'Confirmar nueva contraseña';
            document.getElementById('crearContrasena').required = false;
            nota.style.display = 'none';
            btnGuardarUsuario.textContent = 'Guardar cambios';

            if (datos) {
                crearNombre.value       = datos.nombre || '';
                crearApePaterno.value   = datos.ape_paterno || '';
                crearApeMaterno.value   = datos.ape_materno || '';
                crearSexo.value         = datos.sexo || '';
                crearFechaNacimiento.value = datos.fecha_nacimiento || '';
                crearTelefono.value     = datos.telefono || '';
                crearCorreo.value       = datos.correo || '';
                document.getElementById('crearTipoPersonal').value = datos.tipo_personal_id || '';
                crearUsuarioPreview.value = datos.usuario || '';

                if (datos.ubigeo) await ubicacionValidator.seleccionar(datos.ubigeo);
            }
        }

        modalUsuario.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    function cerrarModal() {
        modalUsuario.style.display = 'none';
        document.body.style.overflow = '';
        formCrearUsuario.reset();
        document.getElementById('crearContrasena').required = true;
        crearProvincia.disabled = true;
        crearDistrito.disabled = true;
        document.getElementById('crearPasswordMatch').classList.remove('show', 'match', 'mismatch');
    }

    document.getElementById('btnCerrarModal').addEventListener('click', cerrarModal);
    document.getElementById('btnCancelarModal').addEventListener('click', cerrarModal);
    modalUsuario.addEventListener('click', (e) => { if (e.target === modalUsuario) cerrarModal(); });

    document.getElementById('btnAbrirCrearUsuario').addEventListener('click', () => abrirModal('crear'));

    let usuariosActuales = [];
    let debounceTimer = null;

    // === Validación de contraseña — CoffeeValidators ===
    CoffeeValidators.contrasena({
        inputEl:    'crearContrasena',
        contadorEl: 'contadorCrearClave',
        max: 30,
        reqs: {
            length:    'crear-req-length',
            uppercase: 'crear-req-uppercase',
            number:    'crear-req-number',
            special:   'crear-req-special',
        },
    });
    CoffeeValidators.contrasena({ inputEl: 'crearConfirmarContrasena', contadorEl: 'contadorCrearConfirmar', max: 30 });
    CoffeeValidators.confirmar({
        claveEl:     'crearContrasena',
        confirmarEl: 'crearConfirmarContrasena',
        matchEl:     'crearPasswordMatch',
        matchTextEl: 'crearPasswordMatchText',
    });
    let departamentosData = [];
    let provinciasData = [];
    let distritosData = [];

    // === Cascada ubigeo — CoffeeValidators ===
    const ubicacionValidator = CoffeeValidators.ubigeo({
        deptoEl: 'crearDepartamento',
        provEl:  'crearProvincia',
        distEl:  'crearDistrito',
    });

    // === Documento — CoffeeValidators ===
    CoffeeValidators.documento({
        tipoEl:    'crearTipoDocumento',
        numEl:     'crearNumDocumento',
        tiposData: tiposDocumento,
        onSearch:  (numDoc) => consultarYAutollenar(numDoc),
    });

    // === Autollenar desde API (lógica de negocio específica — se mantiene) ===
    async function autollenarDesdeDni(data) {
        if (data.nombres)          crearNombre.value          = data.nombres;
        if (data.apellido_paterno) crearApePaterno.value      = data.apellido_paterno;
        if (data.apellido_materno) crearApeMaterno.value      = data.apellido_materno;
        if (data.sexo)             crearSexo.value            = data.sexo;
        if (data.fecha_nacimiento) crearFechaNacimiento.value = data.fecha_nacimiento;
        if (data.telefono)         crearTelefono.value        = data.telefono;
        await ubicacionValidator.seleccionar(data.ubigeo_sunat || data.ubigeo);
    }

    async function consultarYAutollenar(documento) {
        buscarEstado.innerHTML = '<span class="buscar-spinner"></span> Buscando...';
        buscarEstado.className = 'buscar-estado buscando';
        try {
            const respBD = await fetch(`/persona/consultar/${encodeURIComponent(documento)}`);
            if (respBD.ok) {
                const dataBD = await respBD.json();
                if (dataBD.encontrado) {
                    await autollenarDesdeDni(dataBD);
                    buscarEstado.innerHTML = 'Datos cargados desde la base de datos';
                    buscarEstado.className = 'buscar-estado encontrado';
                    generarUsuarioPreview();
                    return;
                }
            }
            // Fallback RENIEC solo para DNI
            const nombreTipo = (tiposDocumento.find(t => t.id === Number(crearTipoDocumento.value))?.nombre || '').toLowerCase().trim();
            if (nombreTipo !== 'dni') {
                buscarEstado.innerHTML = 'No se encontraron datos para este documento';
                buscarEstado.className = 'buscar-estado no-encontrado';
                return;
            }
            const respAPI = await fetch(`/dni/consultar/${encodeURIComponent(documento)}`);
            if (!respAPI.ok) { buscarEstado.innerHTML = 'No se encontraron datos en RENIEC'; buscarEstado.className = 'buscar-estado no-encontrado'; return; }
            const dataAPI = await respAPI.json();
            if (!dataAPI.encontrado) { buscarEstado.innerHTML = 'DNI no válido en RENIEC'; buscarEstado.className = 'buscar-estado no-encontrado'; return; }
            await autollenarDesdeDni(dataAPI);
            buscarEstado.innerHTML = 'Datos cargados desde RENIEC';
            buscarEstado.className = 'buscar-estado encontrado';
            generarUsuarioPreview();
        } catch (error) {
            buscarEstado.innerHTML = 'Error: ' + error.message;
            buscarEstado.className = 'buscar-estado no-encontrado';
        }
    }

    // Generar preview de usuario: primera letra nombre + apellido paterno + primera letra apellido materno
    function generarUsuarioPreview() {
        if (modoModal !== 'crear') return;
        const [nombre, apePaterno, apeMaterno] = [crearNombre, crearApePaterno, crearApeMaterno].map(
            (input) => input.value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s/g, '').toLowerCase()
        );
        crearUsuarioPreview.value = (nombre && apePaterno && apeMaterno)
            ? nombre[0] + apePaterno + apeMaterno[0]
            : '';
    }

    crearNombre.addEventListener('input', generarUsuarioPreview);
    crearApePaterno.addEventListener('input', generarUsuarioPreview);
    crearApeMaterno.addEventListener('input', generarUsuarioPreview);

    // Validar teléfono (solo números)
    crearTelefono.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/[^0-9]/g, '');
    });

    // Cargar lista de usuarios
    async function cargarUsuarios() {
        try {
            const res = await fetch('/perfil/usuarios');
            if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudieron cargar los usuarios.'));

            const data = await res.json();
            usuariosActuales = data.usuarios || [];
            aplicarFiltros();
        } catch (error) {
            usuariosTableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 2rem; color: #d32f2f;">Error: ${error.message}</td></tr>`;
        }
    }

    // Aplicar filtros de búsqueda
    function aplicarFiltros() {
        const textoBusqueda = buscadorUsuarios.value.toLowerCase();

        const usuariosFiltrados = usuariosActuales.filter(u => {
            const coincideTexto = !textoBusqueda ||
                u.nombre.toLowerCase().includes(textoBusqueda) ||
                u.usuario.toLowerCase().includes(textoBusqueda) ||
                u.num_documento.toLowerCase().includes(textoBusqueda);

            return coincideTexto;
        });

        mostrarUsuarios(usuariosFiltrados);
    }

    if (buscadorUsuarios) {
        buscadorUsuarios.addEventListener('input', aplicarFiltros);
    }

    function mostrarUsuarios(usuarios) {
        if (!usuarios || usuarios.length === 0) {
            usuariosTableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:2rem;color:var(--muted-foreground);">No hay usuarios registrados</td></tr>';
            return;
        }

        usuariosTableBody.innerHTML = usuarios.map(u => `
            <tr>
                <td><strong>${u.nombre} ${u.ape_paterno} ${u.ape_materno}</strong></td>
                <td>${u.usuario}</td>
                <td>${u.num_documento}</td>
                <td>${u.tipo_personal}</td>
                <td>
                    <span class="estado-badge ${u.estado === 'A' ? 'activo' : 'inactivo'}">
                        ${u.estado === 'A' ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td class="acciones-celda">
                    <button type="button" class="btn-tabla"
                            onclick="editarUsuario('${u.personal_id}')">
                        Editar
                    </button>
                    ${String(u.personal_id) === String(MI_PERSONAL_ID)
                        ? '<span class="info-text" style="font-size:.8rem;">Tu cuenta</span>'
                        : `<button type="button" class="btn-tabla ${u.estado === 'A' ? 'btn-inactivar' : 'btn-activar'}"
                            onclick="cambiarEstadoUsuario('${u.personal_id}', '${u.estado === 'A' ? 'I' : 'A'}')">
                        ${u.estado === 'A' ? 'Desactivar' : 'Activar'}
                    </button>`}
                </td>
            </tr>
        `).join('');
    }

    window.editarUsuario = async function(personalId) {
        try {
            const res = await fetch(`/perfil/usuarios/${personalId}`);
            if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo cargar el usuario.'));
            const datos = await res.json();
            await abrirModal('editar', datos);
        } catch (error) {
            CoffeeModal.error(error.message);
        }
    };

    window.cambiarEstadoUsuario = async function(personalId, nuevoEstado) {
        const accion = nuevoEstado === 'I' ? 'desactivar' : 'activar';
        const ok = await CoffeeModal.confirm({
            message: `¿${accion.charAt(0).toUpperCase() + accion.slice(1)} este usuario?`,
            okText: 'Sí, confirmar',
            cancelText: 'Cancelar',
        });
        if (!ok) return;

        try {
            const res = await fetch(`/perfil/usuarios/${personalId}/estado`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ estado: nuevoEstado }),
            });

            if (!res.ok) {
                throw new Error(await CoffeeHttp.mensajeError(res, `No se pudo ${accion} el usuario.`));
            }
            CoffeeModal.success(`Usuario ${accion}do correctamente`);
            cargarUsuarios();
        } catch (error) {
            CoffeeModal.error(error.message, 'Usuario restringido');
        }
    };

    // Guardar usuario (crear o editar)
    btnGuardarUsuario.addEventListener('click', async () => {
        const nombre      = crearNombre.value.trim();
        const apePaterno  = crearApePaterno.value.trim();
        const apeMaterno  = crearApeMaterno.value.trim();
        const sexo        = crearSexo.value;
        const fechaNac    = crearFechaNacimiento.value;
        const tipoPersonal = parseInt(document.getElementById('crearTipoPersonal').value);
        const telefono    = crearTelefono.value.trim();
        const correo      = crearCorreo.value.trim();
        const ubigeo      = crearDistrito.value || null;
        const clave       = document.getElementById('crearContrasena').value;
        const confirmar   = document.getElementById('crearConfirmarContrasena').value;

        if (!nombre || !apePaterno || !apeMaterno || !sexo || !fechaNac || !tipoPersonal) {
            CoffeeModal.warning('Completa todos los campos requeridos.');
            return;
        }

        if (modoModal === 'crear') {
            if (crearUsuarioPreview.value.length > 30) {
                CoffeeModal.warning('El nombre de usuario generado supera 30 caracteres; revise el nombre y los apellidos antes de crear la cuenta.');
                return;
            }
            const tipoDoc = parseInt(crearTipoDocumento.value);
            const numDoc  = crearNumDocumento.value.trim();
            if (!tipoDoc || !numDoc || !clave) {
                CoffeeModal.warning('Completa el tipo de documento, el número de documento y la contraseña.');
                return;
            }
            if (clave !== confirmar) { CoffeeModal.warning('Las contraseñas no coinciden.'); return; }

            const btnLabel = btnGuardarUsuario.innerHTML;
            btnGuardarUsuario.disabled = true;
            btnGuardarUsuario.innerHTML = '<span style="opacity:.7">Creando...</span>';
            try {
                const res = await fetch('/perfil/usuarios/crear', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        nombre, ape_paterno: apePaterno, ape_materno: apeMaterno,
                        sexo, fecha_nacimiento: fechaNac, tipo_documento_id: tipoDoc,
                        num_documento: numDoc, telefono: telefono || null,
                        correo: correo || null, ubigeo, tipo_personal_id: tipoPersonal, clave
                    }),
                });
                if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo crear el usuario.'));
                const data = await res.json();
                CoffeeModal.success(`Usuario creado correctamente: ${data.usuario}`);
                cerrarModal();
                cargarUsuarios();
            } catch (e) {
                CoffeeModal.error(e.message);
            } finally {
                btnGuardarUsuario.disabled = false;
                btnGuardarUsuario.innerHTML = btnLabel;
            }

        } else {
            // Editar
            if (clave && clave !== confirmar) { CoffeeModal.warning('Las contraseñas no coinciden.'); return; }

            const btnLabel = btnGuardarUsuario.innerHTML;
            btnGuardarUsuario.disabled = true;
            btnGuardarUsuario.innerHTML = '<span style="opacity:.7">Guardando...</span>';
            try {
                const res = await fetch(`/perfil/usuarios/${personalIdEditando}`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        nombre, ape_paterno: apePaterno, ape_materno: apeMaterno,
                        sexo, fecha_nacimiento: fechaNac,
                        telefono: telefono || null, correo: correo || null,
                        ubigeo, tipo_personal_id: tipoPersonal,
                        clave_nueva: clave || null
                    }),
                });
                if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo actualizar el usuario.'));
                CoffeeModal.success('Usuario actualizado correctamente');
                cerrarModal();
                cargarUsuarios();
            } catch (e) {
                CoffeeModal.error(e.message);
            } finally {
                btnGuardarUsuario.disabled = false;
                btnGuardarUsuario.innerHTML = btnLabel;
            }
        }
    });

    // ═══ CAFICULTORES ═══════════════════════════════════════

    let caficultoresActuales = [];

    async function cargarCaficultores() {
        const tbody = document.getElementById('caficultoresBody');
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:2rem;color:var(--muted-foreground);">Cargando...</td></tr>';
        try {
            const res = await fetch('/caficultor/listar');
            if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudieron cargar los caficultores.'));
            caficultoresActuales = await res.json();
            const conteo = document.getElementById('caficultoresConteo');
            conteo.textContent = `${caficultoresActuales.length} caficultor${caficultoresActuales.length !== 1 ? 'es' : ''} registrado${caficultoresActuales.length !== 1 ? 's' : ''}`;
            aplicarFiltroCaficultores();
        } catch (error) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:2rem;color:var(--destructive);">Error: ${error.message}</td></tr>`;
        }
    }

    function aplicarFiltroCaficultores() {
        const texto = (document.getElementById('buscadorCaficultores')?.value || '').toLowerCase();
        const filtrados = caficultoresActuales.filter(c => {
            const nombre = `${c.nombre} ${c.ape_paterno} ${c.ape_materno}`.toLowerCase();
            return !texto || nombre.includes(texto) || c.num_documento.toLowerCase().includes(texto) || c.tipo_caficultor.toLowerCase().includes(texto);
        });
        mostrarCaficultores(filtrados);
    }

    function mostrarCaficultores(lista) {
        const tbody = document.getElementById('caficultoresBody');
        if (!lista.length) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:2rem;color:var(--muted-foreground);">No se encontraron caficultores</td></tr>';
            return;
        }
        tbody.innerHTML = lista.map(c => {
            const nombre = `${c.nombre} ${c.ape_paterno} ${c.ape_materno}`;
            const ubicacion = [c.provincia, c.departamento].filter(Boolean).join(', ') || '—';
            const esSocio = c.es_socio;
            const badgeStyle = esSocio
                ? 'background:color-mix(in oklab,var(--primary) 15%,transparent);color:var(--primary);'
                : 'background:color-mix(in oklab,#f59e0b 15%,transparent);color:#b45309;';
            return `
                <tr style="cursor:pointer;" onclick="verDetalleCaficultor('${c.persona_id}')">
                    <td><strong>${nombre}</strong></td>
                    <td><span style="padding:2px 10px;border-radius:20px;font-size:12px;font-weight:600;${badgeStyle}">${c.tipo_caficultor}</span></td>
                    <td>${c.num_documento}</td>
                    <td style="color:var(--muted-foreground);font-size:13px;">${ubicacion}</td>
                    <td>${c.telefono || '—'}</td>
                    <td class="acciones-celda">
                        <button type="button" class="btn-tabla" onclick="event.stopPropagation();verDetalleCaficultor('${c.persona_id}')">Ver detalle</button>
                    </td>
                </tr>`;
        }).join('');
    }

    document.getElementById('buscadorCaficultores')?.addEventListener('input', aplicarFiltroCaficultores);

    window.verDetalleCaficultor = function(personaId) {
        const c = caficultoresActuales.find(x => x.persona_id === personaId);
        if (!c) return;

        const nombre = `${c.nombre} ${c.ape_paterno} ${c.ape_materno}`;
        const esSocio = c.tipo_caficultor_id === 1;
        const badgeStyle = esSocio
            ? 'background:color-mix(in oklab,var(--primary) 15%,transparent);color:var(--primary);'
            : 'background:color-mix(in oklab,#f59e0b 15%,transparent);color:#b45309;';
        const ubicacion = [c.distrito, c.provincia, c.departamento].filter(Boolean).join(' / ') || '—';

        document.getElementById('detalleCaficultorNombre').textContent = nombre;
        const badge = document.getElementById('detalleCaficultorBadge');
        badge.textContent = c.tipo_caficultor;
        badge.style.cssText = badgeStyle;

        const campos = [
            { label: 'N.º de documento',     valor: c.num_documento },
            { label: 'Sexo',             valor: c.sexo === 'M' ? 'Masculino' : c.sexo === 'F' ? 'Femenino' : c.sexo || '—' },
            { label: 'Fecha de nacimiento', valor: c.fecha_nacimiento || '—' },
            { label: 'Teléfono',         valor: c.telefono || '—' },
            { label: 'Ubigeo',           valor: c.ubigeo || '—' },
            { label: 'Ubicación',        valor: ubicacion },
            { label: 'Registrado como caficultor', valor: c.fecha_registro || '—' },
        ];

        document.getElementById('detalleCaficultorGrid').innerHTML = campos.map(({ label, valor }) => `
            <div style="padding:10px 12px;background:color-mix(in oklab,var(--muted) 40%,transparent);border-radius:8px;">
                <p style="margin:0 0 2px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;color:var(--muted-foreground);">${label}</p>
                <p style="margin:0;font-size:14px;font-weight:500;color:var(--foreground);">${valor}</p>
            </div>`).join('');

        document.getElementById('modalCaficultor').style.display = 'flex';
        document.body.style.overflow = 'hidden';
    };

    document.getElementById('btnCerrarModalCaficultor').addEventListener('click', () => {
        document.getElementById('modalCaficultor').style.display = 'none';
        document.body.style.overflow = '';
    });
    document.getElementById('modalCaficultor').addEventListener('click', (e) => {
        if (e.target === document.getElementById('modalCaficultor')) {
            document.getElementById('modalCaficultor').style.display = 'none';
            document.body.style.overflow = '';
        }
    });

    // ════════════════════════════════════════════════════
    // MÓDULO AUDITORÍA
    // ════════════════════════════════════════════════════

    let auditPagina = 1;
    let auditIniciada = false;

    const ACCION_BADGE = {
        LOGIN:                 'login',
        LOGIN_FALLIDO:         'login-fail',
        LOGOUT:                'logout',
        CREAR_EVALUACION:      'crear',
        COMPLETAR_EVALUACION:  'completar',
        CREAR_CAFICULTOR:      'crear',
        CONVERTIR_SOCIO:       'crear',
        CREAR_USUARIO:         'crear',
        ACTUALIZAR_USUARIO:    'actualizar',
        ACTIVAR_USUARIO:       'crear',
        DESACTIVAR_USUARIO:    'desactivar',
        CAMBIAR_CLAVE:         'actualizar',
        CAMBIAR_CLAVE_USUARIO: 'actualizar',
        ACTUALIZAR_PERFIL:     'actualizar',
        CREAR_COOPERATIVA:     'crear',
        ACTUALIZAR_COOPERATIVA:'actualizar',
        DESACTIVAR_COOPERATIVA:'desactivar',
        CREAR_VALOR_CAFE:      'crear',
        ACTUALIZAR_VALOR_CAFE: 'actualizar',
        ELIMINAR_VALOR_CAFE:   'eliminar',
    };

    function auditBadgeClass(accion) {
        return 'audit-badge audit-badge--' + (ACCION_BADGE[accion] || 'default');
    }

    function formatFecha(isoStr) {
        if (!isoStr) return '—';
        const d = new Date(isoStr);
        const pad = n => String(n).padStart(2, '0');
        return `${pad(d.getDate())}/${pad(d.getMonth()+1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
    }

    async function cargarAccionesDisponibles() {
        try {
            const res = await fetch('/auditoria/acciones');
            if (!res.ok) return;
            const { acciones } = await res.json();
            const sel = document.getElementById('filtroAccion');
            acciones.forEach(a => {
                const opt = document.createElement('option');
                opt.value = a;
                opt.textContent = a.replace(/_/g, ' ');
                sel.appendChild(opt);
            });
        } catch (_) {}
    }

    async function cargarAuditoria(pagina = 1) {
        const tbody = document.getElementById('auditTableBody');
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:2rem;color:var(--muted-foreground);">Cargando...</td></tr>';

        const params = new URLSearchParams();
        const usuario = document.getElementById('filtroUsuario').value.trim();
        const tipoP   = document.getElementById('filtroTipoPersonal').value;
        const accion  = document.getElementById('filtroAccion').value;
        const desde   = document.getElementById('filtroFechaDesde').value;
        const hasta   = document.getElementById('filtroFechaHasta').value;
        const limite  = document.getElementById('auditPorPagina').value || '10';

        if (usuario) params.set('usuario', usuario);
        if (tipoP)   params.set('tipo_personal_id', tipoP);
        if (accion)  params.set('accion', accion);
        if (desde)   params.set('fecha_desde', desde);
        if (hasta)   params.set('fecha_hasta', hasta);
        params.set('pagina', pagina);
        params.set('limite', limite);

        try {
            const res = await fetch('/auditoria?' + params.toString());
            if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo cargar la auditoría.'));
            const data = await res.json();

            document.getElementById('auditTotal').textContent =
                `${data.total.toLocaleString()} registro${data.total !== 1 ? 's' : ''} encontrado${data.total !== 1 ? 's' : ''}`;

            if (data.registros.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:2rem;color:var(--muted-foreground);">No hay registros para los filtros seleccionados.</td></tr>';
                document.getElementById('auditPaginacion').hidden = true;
                return;
            }

            tbody.innerHTML = data.registros.map(r => `
                <tr>
                    <td style="font-family:'JetBrains Mono';font-size:12px;white-space:nowrap;">${formatFecha(r.fecha_hora)}</td>
                    <td style="font-weight:600;">${r.usuario || '<span style="color:var(--muted-foreground);">—</span>'}</td>
                    <td style="font-size:12px;color:var(--muted-foreground);">${r.rol || '—'}</td>
                    <td><span class="${auditBadgeClass(r.accion)}">${r.accion.replace(/_/g,' ')}</span></td>
                    <td style="font-size:12px;color:var(--muted-foreground);">${r.tabla_afectada || '—'}</td>
                    <td style="font-size:13px;max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${(r.descripcion||'').replace(/"/g,'&quot;')}">${r.descripcion || '—'}</td>
                    <td style="font-family:'JetBrains Mono';font-size:12px;color:var(--muted-foreground);">${r.ip_cliente || '—'}</td>
                    <td><button class="audit-btn-detail" data-id='${JSON.stringify(r)}'>Ver</button></td>
                </tr>
            `).join('');

            // Bind detail buttons
            tbody.querySelectorAll('.audit-btn-detail').forEach(btn => {
                btn.addEventListener('click', () => abrirDetalleAudit(JSON.parse(btn.dataset.id)));
            });

            // Paginación
            auditPagina = pagina;
            const pag = document.getElementById('auditPaginacion');
            pag.hidden = data.total_paginas <= 1;
            document.getElementById('auditPaginaInfo').textContent = `Pág. ${pagina} / ${data.total_paginas}`;
            document.getElementById('btnPrevPage').disabled = pagina <= 1;
            document.getElementById('btnNextPage').disabled = pagina >= data.total_paginas;
            document.getElementById('btnNextPage').dataset.total = data.total_paginas;

        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:2rem;color:var(--destructive);">${err.message}</td></tr>`;
        }
    }

    function abrirDetalleAudit(r) {
        const modal = document.getElementById('modalAudit');
        const content = document.getElementById('auditModalContent');

        const campo = (label, value) => `
            <div class="audit-detail-block">
                <span class="audit-detail-label">${label}</span>
                <span class="audit-detail-value">${value || '—'}</span>
            </div>`;

        const esc = v => String(v ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

        function renderCambios(ant, nue) {
            // Si no hay ambos lados, mostrar el que existe como JSON completo
            if (!ant && !nue) return '';
            if (!ant) return `
                <div class="audit-detail-block">
                    <span class="audit-detail-label">Datos registrados</span>
                    <pre class="audit-json-block">${esc(JSON.stringify(nue, null, 2))}</pre>
                </div>`;
            if (!nue) return `
                <div class="audit-detail-block">
                    <span class="audit-detail-label">Datos al momento</span>
                    <pre class="audit-json-block">${esc(JSON.stringify(ant, null, 2))}</pre>
                </div>`;

            // Calcular diff: solo los campos que cambiaron
            const camposIgnorar = new Set(['fecha_registro', 'cooperativa_id']);
            const claves = new Set([...Object.keys(ant), ...Object.keys(nue)]);
            const diff = [];
            for (const k of claves) {
                if (camposIgnorar.has(k)) continue;
                const vAnt = JSON.stringify(ant[k]);
                const vNue = JSON.stringify(nue[k]);
                if (vAnt !== vNue) diff.push({ campo: k, antes: ant[k], despues: nue[k] });
            }

            if (diff.length === 0) return `
                <div class="audit-detail-block">
                    <span class="audit-detail-label">Cambios detectados</span>
                    <span class="audit-detail-value" style="color:var(--muted-foreground);">Sin diferencias registradas</span>
                </div>`;

            const filas = diff.map(d => `
                <tr>
                    <td style="font-weight:600;font-size:13px;padding:7px 10px;border-bottom:1px solid var(--border);white-space:nowrap;">${esc(d.campo)}</td>
                    <td style="font-size:13px;padding:7px 10px;border-bottom:1px solid var(--border);color:#dc2626;font-family:'JetBrains Mono';word-break:break-all;">${esc(String(d.antes ?? '—'))}</td>
                    <td style="font-size:13px;padding:7px 10px;border-bottom:1px solid var(--border);color:#16a34a;font-family:'JetBrains Mono';word-break:break-all;">${esc(String(d.despues ?? '—'))}</td>
                </tr>`).join('');

            return `
                <div class="audit-detail-block">
                    <span class="audit-detail-label">Cambios (${diff.length} campo${diff.length !== 1 ? 's' : ''})</span>
                    <table style="width:100%;border-collapse:collapse;margin-top:6px;border:1px solid var(--border);border-radius:8px;overflow:hidden;">
                        <thead>
                            <tr style="background:color-mix(in oklab,var(--muted) 30%,transparent);">
                                <th style="text-align:left;padding:6px 10px;font-size:11px;font-weight:600;color:var(--muted-foreground);">Campo</th>
                                <th style="text-align:left;padding:6px 10px;font-size:11px;font-weight:600;color:#dc2626;">Antes</th>
                                <th style="text-align:left;padding:6px 10px;font-size:11px;font-weight:600;color:#16a34a;">Después</th>
                            </tr>
                        </thead>
                        <tbody>${filas}</tbody>
                    </table>
                </div>`;
        }

        content.innerHTML = `
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                ${campo('Fecha / Hora', formatFecha(r.fecha_hora))}
                ${campo('Usuario', r.usuario)}
                ${campo('Rol', r.rol)}
                ${campo('Tipo de usuario', r.tipo_personal_id ? ['','Evaluador','Gerente','Administrador'][r.tipo_personal_id] : null)}
                ${campo('Acción', `<span class="${auditBadgeClass(r.accion)}">${r.accion.replace(/_/g,' ')}</span>`)}
                ${campo('Tabla afectada', r.tabla_afectada)}
                ${campo('Registro ID', r.registro_id)}
                ${campo('IP', r.ip_cliente)}
            </div>
            ${campo('Descripción', r.descripcion)}
            ${renderCambios(r.datos_anteriores, r.datos_nuevos)}
        `;

        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    async function inicializarAuditoria() {
        if (!auditIniciada) {
            auditIniciada = true;
            await cargarAccionesDisponibles();
        }
        cargarAuditoria(1);
    }

    document.getElementById('btnFiltrarAudit').addEventListener('click', () => cargarAuditoria(1));

    document.getElementById('btnLimpiarFiltros').addEventListener('click', () => {
        document.getElementById('filtroUsuario').value = '';
        document.getElementById('filtroTipoPersonal').value = '';
        document.getElementById('filtroAccion').value = '';
        document.getElementById('filtroFechaDesde').value = '';
        document.getElementById('filtroFechaHasta').value = '';
        cargarAuditoria(1);
    });

    document.getElementById('auditPorPagina').addEventListener('change', () => cargarAuditoria(1));

    document.getElementById('btnPrevPage').addEventListener('click', () => {
        if (auditPagina > 1) cargarAuditoria(auditPagina - 1);
    });
    document.getElementById('btnNextPage').addEventListener('click', () => {
        const total = parseInt(document.getElementById('btnNextPage').dataset.total || '1', 10);
        if (auditPagina < total) cargarAuditoria(auditPagina + 1);
    });

    document.getElementById('btnCerrarModalAudit').addEventListener('click', () => {
        document.getElementById('modalAudit').style.display = 'none';
        document.body.style.overflow = '';
    });
    document.getElementById('modalAudit').addEventListener('click', e => {
        if (e.target === document.getElementById('modalAudit')) {
            document.getElementById('modalAudit').style.display = 'none';
            document.body.style.overflow = '';
        }
    });

    // === Reportes ===
    let reportesIniciados = false;
    let catalogoReportes = [];
    let reportePagina = 1;
    let reporteConsulta = null;
    let filtrosReporteAplicados = new URLSearchParams();
    const selectReporte = document.getElementById('selectReporte');
    const formFiltrosReporte = document.getElementById('formFiltrosReporte');
    const btnFiltrarReporte = document.getElementById('btnFiltrarReporte');

    function estadoReporte(mensaje) {
        const p = document.createElement('p');
        p.className = 'reporte-estado';
        p.textContent = mensaje;
        document.getElementById('reporteContainer').replaceChildren(p);
    }

    async function inicializarReportes() {
        if (!reportesIniciados) {
            try {
                const res = await fetch('/reportes');
                if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo cargar el catálogo de reportes.'));
                catalogoReportes = await res.json();
                selectReporte.replaceChildren();
                catalogoReportes.forEach(r => {
                    const option = document.createElement('option');
                    option.value = r.codigo;
                    option.textContent = r.titulo;
                    selectReporte.appendChild(option);
                });
                reportesIniciados = true;
            } catch (error) {
                estadoReporte(error.message);
                return;
            }
        }
        cargarReporte();
    }

    async function cargarReporte(pagina = 1, aplicarFiltros = true) {
        const codigo = selectReporte.value;
        const meta = catalogoReportes.find(r => r.codigo === codigo);
        if (!meta) return;
        reporteConsulta?.abort();
        reporteConsulta = null;
        const container = document.getElementById('reporteContainer');
        const errorFiltro = document.getElementById('reporteFiltroError');
        errorFiltro.hidden = true;
        document.getElementById('reportePaginacion').hidden = true;
        container.setAttribute('aria-busy', 'false');
        btnFiltrarReporte.disabled = false;
        btnFiltrarReporte.textContent = 'Consultar';
        estadoReporte('Cargando reporte…');
        formFiltrosReporte.hidden = !meta.admite_filtros;
        document.getElementById('reporteDescripcion').textContent = meta.descripcion;
        if (aplicarFiltros) {
            if (meta.admite_filtros && !formFiltrosReporte.reportValidity()) {
                estadoReporte('Revise las fechas y vuelva a consultar el reporte.');
                return;
            }
            filtrosReporteAplicados = new URLSearchParams();
            if (meta.admite_filtros) {
                const campos = { desde: 'reporteDesde', hasta: 'reporteHasta', busqueda: 'reporteBusqueda', tipo_caficultor: 'reporteTipo' };
                Object.entries(campos).forEach(([clave, id]) => {
                    const valor = document.getElementById(id).value.trim();
                    if (valor) filtrosReporteAplicados.set(clave, valor);
                });
            }
        }
        const consulta = new AbortController();
        reporteConsulta = consulta;
        const params = new URLSearchParams(filtrosReporteAplicados);
        params.set('pagina', pagina);
        container.setAttribute('aria-busy', 'true');
        btnFiltrarReporte.disabled = true;
        btnFiltrarReporte.textContent = 'Consultando…';
        try {
            const res = await fetch(`/reportes/${encodeURIComponent(codigo)}?${params}`, { signal: consulta.signal });
            if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo cargar el reporte.'));
            const reporte = await res.json();
            if (consulta.signal.aborted) return;
            CoffeeReport.render(container, reporte, { verDetalle: abrirDetalleReporte });
            reportePagina = reporte.pagina;
            const total = reporte.total_filas;
            const paginacion = document.getElementById('reportePaginacion');
            paginacion.hidden = total == null;
            if (total != null) {
                const paginas = Math.max(1, Math.ceil(total / reporte.por_pagina));
                document.getElementById('reportePaginaTexto').textContent = `${total} registros · Página ${reportePagina} de ${paginas}`;
                document.getElementById('reporteAnterior').disabled = reportePagina <= 1;
                document.getElementById('reporteSiguiente').disabled = reportePagina >= paginas;
            }
        } catch (error) {
            if (consulta.signal.aborted) return;
            estadoReporte('No se pudo cargar el reporte. Revise los filtros y vuelva a consultar.');
            errorFiltro.textContent = error.message;
            errorFiltro.hidden = false;
        }
        finally {
            if (reporteConsulta === consulta) {
                container.setAttribute('aria-busy', 'false');
                btnFiltrarReporte.disabled = false;
                btnFiltrarReporte.textContent = 'Consultar';
            }
        }
    }

    selectReporte.addEventListener('change', () => cargarReporte());
    formFiltrosReporte.addEventListener('submit', e => {
        e.preventDefault();
        cargarReporte();
    });
    const reporteDesde = document.getElementById('reporteDesde');
    const reporteHasta = document.getElementById('reporteHasta');
    function validarFechasReporte() {
        reporteHasta.setCustomValidity(reporteDesde.value && reporteHasta.value && reporteDesde.value > reporteHasta.value
            ? 'La fecha final debe ser igual o posterior a la fecha inicial.' : '');
    }
    reporteDesde.addEventListener('input', validarFechasReporte);
    reporteHasta.addEventListener('input', validarFechasReporte);
    document.getElementById('btnLimpiarReporte').addEventListener('click', () => {
        formFiltrosReporte.reset();
        validarFechasReporte();
        cargarReporte();
    });
    document.getElementById('reporteAnterior').addEventListener('click', () => cargarReporte(reportePagina - 1, false));
    document.getElementById('reporteSiguiente').addEventListener('click', () => cargarReporte(reportePagina + 1, false));

    const modalReporte = document.getElementById('modalReporteEvaluacion');
    let detalleReporteConsulta = null;
    let overflowAntesReporte = '';
    async function abrirDetalleReporte(fila) {
        detalleReporteConsulta?.abort();
        const consulta = new AbortController();
        detalleReporteConsulta = consulta;
        const estado = document.getElementById('reporteDetalleEstado');
        const resumen = document.getElementById('reporteDetalleResumen');
        document.getElementById('reporteDetalleTitulo').textContent = `Detalle de ${fila.codigo}`;
        estado.textContent = 'Cargando evaluación…';
        estado.hidden = false;
        resumen.hidden = true;
        overflowAntesReporte = document.body.style.overflow;
        document.body.style.overflow = 'hidden';
        modalReporte.showModal();
        try {
            const res = await fetch(`/evaluacion/${encodeURIComponent(fila.evaluacion_id)}/resumen`, { signal: consulta.signal });
            if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo cargar el detalle de la evaluación.'));
            const data = await res.json();
            if (consulta.signal.aborted) return;
            CoffeeResumen.pintar(data);
            estado.hidden = true;
            resumen.hidden = false;
        } catch (error) {
            if (!consulta.signal.aborted) estado.textContent = error.message;
        }
    }
    document.getElementById('cerrarReporteDetalle').addEventListener('click', () => modalReporte.close());
    modalReporte.addEventListener('click', e => {
        if (e.target === modalReporte) {
            const rect = modalReporte.getBoundingClientRect();
            if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) modalReporte.close();
        }
    });
    modalReporte.addEventListener('close', () => {
        detalleReporteConsulta?.abort();
        document.body.style.overflow = overflowAntesReporte;
    });

    // Inicializar
    async function inicializarCrearUsuario() {
        await ubicacionValidator.cargarDepartamentos();
        cargarCooperativa();
    }

    inicializarCrearUsuario();
