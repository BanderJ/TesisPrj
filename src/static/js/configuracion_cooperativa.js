    let cooperativaId = null;
    let tiposPersonal = [];
    let tiposDocumento = [];

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
                } else if (section === 'usuarios') {
                    cargarUsuarios();
                } else if (section === 'caficultores') {
                    cargarCaficultores();
                }
            }
        });
    });

    // === Cargar información inicial ===
    async function cargarCooperativa() {
        const loadingState = document.getElementById('loadingState');

        try {
            const res = await fetch('/cooperativas/mi-cooperativa');
            if (!res.ok) throw new Error('No se pudo cargar la cooperativa');

            const data = await res.json();
            cooperativaId = data.cooperativa_id;

            // Llenar formulario básico
            document.getElementById('nombre').value = data.nombre || '';
            document.getElementById('codigo').value = data.codigo || '';
            document.getElementById('direccion').value = data.direccion || '';
            document.getElementById('telefono').value = data.telefono || '';
            document.getElementById('correo').value = data.correo || '';
            document.getElementById('descripcion').value = data.descripcion || '';
            document.getElementById('imagen_url').value = data.imagen_url || '';

            if (data.imagen_url) {
                document.getElementById('imagenPreview').src = data.imagen_url;
                document.getElementById('previewContainer').hidden = false;
            }

            // Mostrar secciones de admin
            if (isAdmin) {
                document.getElementById('navTiposGrano').hidden = false;
                document.getElementById('navUsuarios').hidden = false;
                document.getElementById('navCaficultores').hidden = false;
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
            CoffeeModal.warning('Completa nombre y peso válido');
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
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || 'Error al guardar');
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

    async function cargarTiposGrano() {
        const tbody = document.getElementById('tiposGranoBody');
        try {
            const res = await fetch('/tipo-grano/listar');
            if (!res.ok) throw new Error('No se pudo cargar tipos de grano');

            const tipos = await res.json();
            if (tipos.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;padding:2rem;color:var(--muted-foreground);">No hay tipos de grano registrados</td></tr>';
                return;
            }

            tbody.innerHTML = tipos.map(tipo => `
                <tr>
                    <td><strong>${tipo.nombre}</strong></td>
                    <td>${tipo.peso_qq}</td>
                    <td class="acciones-celda">
                        <button type="button" class="btn-tabla" onclick="editarTipo(${tipo.id}, '${tipo.nombre}', ${tipo.peso_qq})">Editar</button>
                        <button type="button" class="btn-tabla btn-inactivar" onclick="eliminarTipo(${tipo.id})">Eliminar</button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            console.error('Error:', error);
            tbody.innerHTML = `<tr><td colspan="3" style="text-align:center;padding:2rem;color:var(--destructive);">Error: ${error.message}</td></tr>`;
        }
    }

    window.editarTipo = function(tipoId, nombre, peso) {
        abrirModalTipoGrano('editar', { id: tipoId, nombre, peso_qq: peso });
    };

    window.eliminarTipo = async function(tipoId) {
        const ok = await CoffeeModal.confirm({
            message: '¿Eliminar este tipo de grano?',
            okText: 'Sí, eliminar',
            cancelText: 'Cancelar',
        });
        if (!ok) return;

        try {
            const res = await fetch(`/tipo-grano/${tipoId}`, { method: 'DELETE' });
            if (!res.ok) throw new Error('Error al eliminar');
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
                    direccion: document.getElementById('direccion').value || null,
                    telefono: document.getElementById('telefono').value || null,
                    correo: document.getElementById('correo').value || null,
                    descripcion: document.getElementById('descripcion').value || null,
                    imagen_url: document.getElementById('imagen_url').value || null,
                }),
            });

            if (!res.ok) throw new Error('Error al guardar');
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
            if (!res.ok) throw new Error('Error al subir');
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
            document.getElementById('buscarEstado').innerHTML = '<span>Ingresa el documento para buscar datos de la persona</span>';
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
        const nombre = crearNombre.value.trim();
        const apePaterno = crearApePaterno.value.trim();
        const apeMaterno = crearApeMaterno.value.trim();
        crearUsuarioPreview.value = (nombre && apePaterno && apeMaterno)
            ? (nombre[0] + apePaterno + apeMaterno[0]).toLowerCase()
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
            if (!res.ok) throw new Error('Error al cargar usuarios');

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
                <td>@${u.usuario}</td>
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
                    <button type="button" class="btn-tabla ${u.estado === 'A' ? 'btn-inactivar' : 'btn-activar'}"
                            onclick="cambiarEstadoUsuario('${u.personal_id}', '${u.estado === 'A' ? 'I' : 'A'}')">
                        ${u.estado === 'A' ? 'Desactivar' : 'Activar'}
                    </button>
                </td>
            </tr>
        `).join('');
    }

    window.editarUsuario = async function(personalId) {
        try {
            const res = await fetch(`/perfil/usuarios/${personalId}`);
            if (!res.ok) throw new Error('No se pudo cargar el usuario');
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

            if (!res.ok) throw new Error('Error');
            CoffeeModal.success(`Usuario ${accion}do correctamente`);
            cargarUsuarios();
        } catch (error) {
            CoffeeModal.error(error.message);
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
            CoffeeModal.warning('Completa todos los campos requeridos');
            return;
        }

        if (modoModal === 'crear') {
            const tipoDoc = parseInt(crearTipoDocumento.value);
            const numDoc  = crearNumDocumento.value.trim();
            if (!tipoDoc || !numDoc || !clave) {
                CoffeeModal.warning('Completa tipo de documento, número de documento y contraseña');
                return;
            }
            if (clave !== confirmar) { CoffeeModal.warning('Las contraseñas no coinciden'); return; }

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
                if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || 'Error');
                CoffeeModal.success('Usuario creado correctamente');
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
            if (clave && clave !== confirmar) { CoffeeModal.warning('Las contraseñas no coinciden'); return; }

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
                if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || 'Error');
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
            if (!res.ok) throw new Error('Error al cargar caficultores');
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
                    <td>${c.num_documento}</td>
                    <td><span style="padding:2px 10px;border-radius:20px;font-size:12px;font-weight:600;${badgeStyle}">${c.tipo_caficultor}</span></td>
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
            { label: 'N° Documento',     valor: c.num_documento },
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

    // Inicializar
    async function inicializarCrearUsuario() {
        await ubicacionValidator.cargarDepartamentos();
        cargarCooperativa();
    }

    inicializarCrearUsuario();
