#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generador de manual completo y detallado para CoffeeRen"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import datetime

def set_cell_background(cell, color):
    """Establece color de fondo de celda"""
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), color)
    cell._element.get_or_add_tcPr().append(shading_elm)

def add_section_break():
    """Añade salto de página"""
    doc.add_page_break()

def create_table_with_data(rows, cols, header_data, body_data):
    """Crea tabla con datos"""
    table = doc.add_table(rows=rows, cols=cols)
    table.style = 'Light Grid Accent 1'

    # Encabezado
    for i, header in enumerate(header_data):
        cell = table.rows[0].cells[i]
        cell.text = header
        set_cell_background(cell, '22c55e')
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

    # Cuerpo
    for row_idx, row_data in enumerate(body_data, 1):
        for col_idx, cell_data in enumerate(row_data):
            table.rows[row_idx].cells[col_idx].text = str(cell_data)
            if row_idx % 2 == 0:
                set_cell_background(table.rows[row_idx].cells[col_idx], 'f0f0f0')

    return table

doc = Document()
section = doc.sections[0]
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)

# ============ PORTADA ============
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title_run = title.add_run('COFFEREN')
title_run.font.size = Pt(52)
title_run.font.bold = True
title_run.font.color.rgb = RGBColor(34, 197, 94)

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
subtitle_run = subtitle.add_run('Sistema Integral de Clasificación de Café Verde')
subtitle_run.font.size = Pt(20)
subtitle_run.font.color.rgb = RGBColor(100, 100, 100)

doc.add_paragraph()

desc = doc.add_paragraph()
desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
desc_run = desc.add_run('MANUAL COMPLETO DEL USUARIO')
desc_run.font.size = Pt(16)
desc_run.font.bold = True

doc.add_paragraph()

subdesc = doc.add_paragraph()
subdesc.alignment = WD_ALIGN_PARAGRAPH.CENTER
subdesc_run = subdesc.add_run('Guía Profesional para Operarios, Gerentes y Administradores')
subdesc_run.font.size = Pt(12)
subdesc_run.font.italic = True

doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

info = doc.add_paragraph()
info.alignment = WD_ALIGN_PARAGRAPH.CENTER
info_text = f'Versión 2.0 Completa\n{datetime.now().strftime("%d de %B de %Y")}\nCooperativa Lonya Grande, Amazonas, Perú'
info_run = info.add_run(info_text)
info_run.font.size = Pt(11)

add_section_break()

# ============ TABLA DE CONTENIDOS EXPANDIDA ============
doc.add_heading('Tabla de Contenidos', level=1)

toc_items = [
    '1. Introducción y Propósito',
    '2. Descripción General del Sistema',
    '3. Requisitos Técnicos y Seguridad',
    '4. Acceso al Sistema',
    '5. Navegación e Interfaz',
    '6. Gestión de Caficultores',
    '7. Registro Detallado de Muestras',
    '8. Validación de Datos',
    '9. Monitoreo en Tiempo Real',
    '10. Análisis Inteligente de Resultados',
    '11. Búsqueda y Reportes',
    '12. Gestión de Precios',
    '13. Cálculos y Fórmulas de Pago',
    '14. Flujos Operativos Completos',
    '15. Troubleshooting y Problemas Comunes',
    '16. Mejores Prácticas',
    '17. Seguridad y Confidencialidad',
    '18. Preguntas Frecuentes Ampliadas',
    '19. Glosario Técnico Completo',
    '20. Referencias y Soporte',
]

for item in toc_items:
    p = doc.add_paragraph(item, style='List Bullet')

add_section_break()

# ============ 1. INTRODUCCIÓN ============
doc.add_heading('1. Introducción y Propósito', level=1)

doc.add_heading('¿Por Qué Existe CoffeeRen?', level=2)
doc.add_paragraph(
    'CoffeeRen surge como respuesta a la necesidad de la Cooperativa Lonya Grande de digitalizar '
    'y optimizar el proceso de clasificación de café verde. Antes de este sistema, el proceso era '
    'manual, lento e impreciso, lo que generaba inconsistencias en pagos y pérdida de trazabilidad.'
)

doc.add_heading('Beneficios del Sistema', level=2)
beneficios = [
    ('Automatización', 'Reduce tiempo de procesamiento de horas a minutos'),
    ('Precisión', 'Clasificación consistente mediante visión artificial'),
    ('Trazabilidad', 'Cada lote tiene código único e historial completo'),
    ('Transparencia', 'Caficultores pueden consultar resultados en cualquier momento'),
    ('Cálculo Justo', 'Pagos basados en mediciones objetivas, no estimaciones'),
    ('Reportes', 'Análisis detallados de calidad y rendimiento'),
    ('Escalabilidad', 'Sistema preparado para crecer con la cooperativa'),
]

for beneficio, descripcion in beneficios:
    p = doc.add_paragraph()
    p.add_run(f'{beneficio}: ').bold = True
    p.add_run(descripcion)

doc.add_heading('Públicos Objetivo', level=2)
p = doc.add_paragraph()
p.add_run('Operarios de Laboratorio: ').bold = True
p.add_run('Persona encargada de registrar caficultores, ingresa datos de muestras, '
    'supervisa el monitoreo y entrega resultados. Es el usuario diario del sistema.')

p = doc.add_paragraph()
p.add_run('Gerentes: ').bold = True
p.add_run('Supervisan operaciones, acceden a reportes de producción, analizan '
    'tendencias y toman decisiones sobre precios y políticas.')

p = doc.add_paragraph()
p.add_run('Administradores: ').bold = True
p.add_run('Controlan acceso de usuarios, configuran precios, resuelven problemas '
    'técnicos y mantienen la integridad de datos.')

p = doc.add_paragraph()
p.add_run('Caficultores/Productores: ').bold = True
p.add_run('Utilizan el sistema principalmente para consultar resultados de sus '
    'muestras y conocer el pago a recibir.')

add_section_break()

# ============ 2. DESCRIPCIÓN GENERAL ============
doc.add_heading('2. Descripción General del Sistema', level=1)

doc.add_heading('Arquitectura General', level=2)
doc.add_paragraph(
    'CoffeeRen es una arquitectura integrada con tres componentes principales:'
)

doc.add_heading('Backend (Servidor FastAPI)', level=3)
doc.add_paragraph(
    'Aplicación web basada en FastAPI que procesa datos, gestiona la base de datos '
    'y coordina con el hardware. Se ejecuta en un servidor local conectado al laboratorio.'
)

doc.add_heading('Frontend (Interfaz Web)', level=3)
doc.add_paragraph(
    'Interfaz HTML/CSS/JavaScript renderizada en el servidor. Los usuarios acceden '
    'mediante navegador web desde cualquier dispositivo en la red del laboratorio.'
)

doc.add_heading('Hardware Especializado', level=3)
doc.add_paragraph(
    'Máquina de clasificación equipada con sensores (HX711 para peso, HC-SR04 para presencia, '
    'servo para desvío) conectada vía puerto serial a 9600 baudios.'
)

doc.add_heading('Ciclo de Vida Completo de una Evaluación', level=2)

table_data = [
    ['Fase', 'Duración', 'Responsable', 'Acciones Clave'],
    ['Registro', '5-10 min', 'Operario', 'Carga datos del caficultor y muestra'],
    ['Monitoreo', '3-8 min', 'Máquina + Operario', 'Clasificación automática en tiempo real'],
    ['Análisis', 'Inmediato', 'Sistema', 'Cálculo de calidad, defectos y pago'],
    ['Consulta', 'Indefinida', 'Operario/Caficultor', 'Búsqueda por código EVA'],
]

table = doc.add_table(rows=5, cols=4)
table.style = 'Light Grid Accent 1'

for row_idx, row_data in enumerate(table_data):
    for col_idx, cell_data in enumerate(row_data):
        cell = table.rows[row_idx].cells[col_idx]
        cell.text = cell_data
        if row_idx == 0:
            set_cell_background(cell, '22c55e')
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(255, 255, 255)
        elif row_idx % 2 == 0:
            set_cell_background(cell, 'f0f0f0')

add_section_break()

# ============ 3. REQUISITOS TÉCNICOS ============
doc.add_heading('3. Requisitos Técnicos y Seguridad', level=1)

doc.add_heading('Requisitos de Hardware', level=2)
doc.add_paragraph(
    'Computadora de escritorio o servidor con:\n'
    '  Procesador: Intel i5 o equivalente (mínimo)\n'
    '  RAM: 8 GB recomendado\n'
    '  Almacenamiento: 500 GB (SSD recomendado)\n'
    '  Conexión: Ethernet para estabilidad\n'
    '  Puertos USB: Para conexión de cámara y Arduino'
)

doc.add_heading('Requisitos de Red', level=2)
doc.add_paragraph(
    'Red local (LAN) con acceso a http://localhost:8000\n'
    'Ancho de banda mínimo: 10 Mbps para streaming de cámara\n'
    'Latencia máxima: <100ms recomendado\n'
    'No requiere conexión a internet (funciona offline)'
)

doc.add_heading('Navegadores Soportados', level=2)
doc.add_paragraph(
    'Google Chrome 90+\n'
    'Microsoft Edge 90+\n'
    'Firefox 88+\n'
    'Safari 14+ (en macOS si aplica)\n'
    'Nota: Se recomienda Chrome para mejor compatibilidad'
)

doc.add_heading('Seguridad de Credenciales', level=2)
doc.add_paragraph(
    'Cada usuario tiene credenciales únicas (usuario y contraseña) asignadas por el administrador.'
)
doc.add_paragraph(
    'Medidas de Seguridad:\n'
    '  - Contraseñas cifradas (Argon2 hash)\n'
    '  - Tokens JWT con expiración de 7 días\n'
    '  - Cookies httponly (previene acceso desde JavaScript)\n'
    '  - Sesiones por dispositivo\n'
    '  - Registro de accesos y cambios'
)

doc.add_heading('Confidencialidad de Datos', level=2)
doc.add_paragraph(
    'Los datos de caficultores y evaluaciones son confidenciales. No compartas credenciales '
    'ni dejes sesión abierta en dispositivos públicos. Siempre cierra sesión al terminar tu turno.'
)

add_section_break()

# ============ 4. ACCESO AL SISTEMA ============
doc.add_heading('4. Acceso al Sistema', level=1)

doc.add_heading('Primer Acceso', level=2)
p = doc.add_paragraph()
p.add_run('1. Obtén Credenciales: ').bold = True
p.add_run('El administrador te proporcionará un usuario y contraseña temporal.')

p = doc.add_paragraph()
p.add_run('2. Abre Navegador: ').bold = True
p.add_run('Accede a http://localhost:8000 desde cualquier dispositivo en la red.')

p = doc.add_paragraph()
p.add_run('3. Ingresa Credenciales: ').bold = True
p.add_run('Usuario (campo izquierdo), Contraseña (campo derecho).')

p = doc.add_paragraph()
p.add_run('4. Haz Clic en "Ingresar": ').bold = True
p.add_run('Si son correctas, verás el dashboard principal (Inicio).')

doc.add_heading('Recuperación de Contraseña', level=2)
doc.add_paragraph(
    'Si olvidas tu contraseña:\n'
    '  1. Comunícate inmediatamente con el administrador\n'
    '  2. El administrador reiniciará tu contraseña\n'
    '  3. Recibirás una contraseña temporal por whatsapp/email\n'
    '  4. Al primer acceso, el sistema te solicitará cambiarla\n'
    '  5. Crea una contraseña segura (letras, números, caracteres especiales)'
)

doc.add_heading('Cambio de Contraseña', level=2)
p = doc.add_paragraph()
p.add_run('1. ').bold = True
p.add_run('Haz clic en tu avatar (esquina superior derecha).')

p = doc.add_paragraph()
p.add_run('2. ').bold = True
p.add_run('Selecciona "Configuración".')

p = doc.add_paragraph()
p.add_run('3. ').bold = True
p.add_run('En la sección "Seguridad", busca "Cambiar Contraseña".')

p = doc.add_paragraph()
p.add_run('4. ').bold = True
p.add_run('Ingresa contraseña actual y la nueva contraseña (mínimo 8 caracteres).')

p = doc.add_paragraph()
p.add_run('5. ').bold = True
p.add_run('Haz clic en "Actualizar". Se confirmará el cambio.')

doc.add_heading('Cierre de Sesión', level=2)
p = doc.add_paragraph()
p.add_run('1. ').bold = True
p.add_run('Haz clic en tu avatar (esquina superior derecha).')

p = doc.add_paragraph()
p.add_run('2. ').bold = True
p.add_run('Selecciona "Cerrar Sesión".')

p = doc.add_paragraph()
p.add_run('3. ').bold = True
p.add_run('Se cerrará tu sesión y retornarás a la pantalla de login.')

doc.add_heading('Importante', level=2)
doc.add_paragraph(
    'Siempre cierra sesión al terminar tu turno, especialmente si compartís dispositivo con otros operarios. '
    'Esto protege la confidencialidad de datos y evita accesos no autorizados.'
)

add_section_break()

# ============ 5. NAVEGACIÓN ============
doc.add_heading('5. Navegación e Interfaz', level=1)

doc.add_heading('Estructura General de la Página', level=2)
doc.add_paragraph(
    'Toda página en CoffeeRen sigue una estructura consistente:'
)

doc.add_heading('Encabezado (Header)', level=3)
p = doc.add_paragraph()
p.add_run('Logo y Marca: ').bold = True
p.add_run('En la esquina superior izquierda. Haz clic para volver a Inicio.')

p = doc.add_paragraph()
p.add_run('Menú de Navegación: ').bold = True
p.add_run('Links a las secciones principales (Inicio, Registro, Buscar, etc.).')

p = doc.add_paragraph()
p.add_run('Modo Oscuro: ').bold = True
p.add_run('Botón de alternancia entre tema claro y oscuro (preferencia personal).')

p = doc.add_paragraph()
p.add_run('Avatar de Usuario: ').bold = True
p.add_run('Tu inicial en un círculo. Haz clic para perfil, configuración y logout.')

doc.add_heading('Área Principal (Main)', level=3)
doc.add_paragraph(
    'Contenido principal de cada página. Cambio según la sección que visites.'
)

doc.add_heading('Pie de Página (Footer)', level=3)
doc.add_paragraph(
    'Información general, copyright y enlaces útiles. Normalmente sin interacción.'
)

doc.add_heading('Menú de Navegación Detallado', level=2)

menu_items = [
    ('Inicio',
     'Regresa al dashboard principal.',
     'Ver resumen de actividad, gráficos de precios, accesos rápidos a módulos.'),

    ('Registro de muestra',
     'Accede al formulario para registrar una nueva evaluación.',
     'Recopilación de datos del caficultor e información técnica de la muestra.'),

    ('Buscar muestras',
     'Consulta evaluaciones anteriores por código EVA.',
     'Recuperar datos históricos, exportar reportes, auditoría.'),

    ('Registrar caficultor',
     'Ingresa nuevos productores o modifica datos existentes.',
     'Alta de caficultor, actualización, conversión a socio.'),

    ('Valor Café',
     'Administración de precios por rango (solo Gerente/Admin).',
     'Registrar nuevos precios, visualizar historial, gráficos de tendencia.'),
]

for menu_name, desc_1, desc_2 in menu_items:
    p = doc.add_paragraph()
    p.add_run(f'{menu_name}: ').bold = True
    p.add_run(desc_1)
    doc.add_paragraph(f'  Uso típico: {desc_2}', style='List Bullet 2')

doc.add_heading('Navegación por Teclado', level=2)
doc.add_paragraph(
    'Atajos útiles:\n'
    '  Tab: Navega entre campos del formulario\n'
    '  Enter: Envía formulario o confirma acción\n'
    '  Esc: Cierra diálogos o modales\n'
    '  F5: Recarga la página actual\n'
    '  Ctrl+P: Abre impresor (para exportar PDF)'
)

add_section_break()

# ============ 6. GESTIÓN DE CAFICULTORES ============
doc.add_heading('6. Gestión de Caficultores', level=1)

doc.add_heading('Concepto de Caficultor', level=2)
doc.add_paragraph(
    'Un caficultor es un productor de café registrado en el sistema. Cada caficultor tiene:\n'
    '  - Datos personales (nombre, documento)\n'
    '  - Documentación identificación válida\n'
    '  - Estado (Socio o no-Socio)\n'
    '  - Historial de evaluaciones'
)

doc.add_heading('Estados de Caficultor', level=2)

table_states = doc.add_table(rows=3, cols=3)
table_states.style = 'Light Grid Accent 1'

states_data = [
    ['Estado', 'Descripción', 'Beneficios'],
    ['No-Socio', 'Productor sin afiliación a la cooperativa', 'Puede traer muestras pero sin beneficios especiales'],
    ['Socio', 'Miembro oficial de la cooperativa', 'Acceso a créditos, mejores precios, asistencia técnica'],
]

for row_idx, row_data in enumerate(states_data):
    for col_idx, cell_data in enumerate(row_data):
        cell = table_states.rows[row_idx].cells[col_idx]
        cell.text = cell_data
        if row_idx == 0:
            set_cell_background(cell, '22c55e')
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(255, 255, 255)

doc.add_heading('Registro de Nuevo Caficultor - Paso a Paso', level=2)

p = doc.add_paragraph()
p.add_run('Paso 1: Acceder al Módulo').bold = True
p = doc.add_paragraph('Desde la barra de navegación, haz clic en "Registrar caficultor".')

p = doc.add_paragraph()
p.add_run('Paso 2: Completar Tipo de Documento').bold = True
p = doc.add_paragraph(
    'Abre el dropdown "Tipo de Documento" y selecciona:\n'
    '    - DNI (Documento Nacional de Identidad Peruano): 8 dígitos\n'
    '    - Pasaporte: 8-12 caracteres alfanuméricos\n'
    '    - Carnet de Extranjería: 8-12 caracteres alfanuméricos'
)

p = doc.add_paragraph()
p.add_run('Paso 3: Ingresar Número de Documento').bold = True
p = doc.add_paragraph(
    'Ingresa el número exacto. El sistema valida el formato automáticamente.\n'
    'Si el caficultor ya existe, aparecerá un mensaje de aviso.'
)

p = doc.add_paragraph()
p.add_run('Paso 4: Nombres y Apellidos').bold = True
p = doc.add_paragraph(
    'Ingresa el nombre completo del caficultor (como figura en su documento). '
    'Evita abreviaturas.'
)

p = doc.add_paragraph()
p.add_run('Paso 5: Guardar').bold = True
p = doc.add_paragraph(
    'Haz clic en "Guardar Caficultor". El sistema validará que todos los datos sean correctos.\n'
    'Si hay errores, te mostrará mensajes específicos de qué corregir.'
)

doc.add_heading('Validación de Documentos en Detalle', level=2)

doc.add_paragraph('El sistema valida automáticamente:')

val_items = [
    ('DNI', '8 dígitos numéricos, sin letras ni caracteres especiales'),
    ('Pasaporte', '8-12 caracteres, puede incluir letras y números'),
    ('Carnet Ext.', '8-12 caracteres, formato: 3 letras + números'),
]

for doc_type, validation in val_items:
    p = doc.add_paragraph()
    p.add_run(f'{doc_type}: ').bold = True
    p.add_run(validation)

doc.add_paragraph('Mensajes de Validación:')
doc.add_paragraph('El campo muestra color rojo si hay error, verde si es correcto.', style='List Bullet')
doc.add_paragraph('Aparece un mensaje explicativo debajo de cada campo.', style='List Bullet')
doc.add_paragraph('No puedes enviar el formulario hasta corregir todos los errores.', style='List Bullet')

doc.add_heading('Convertir a Socio - Guía Completa', level=2)

p = doc.add_paragraph()
p.add_run('¿Cuándo se convierte un caficultor a Socio?').bold = True
p = doc.add_paragraph(
    'Cuando el productor solicita oficialmente afiliarse a la cooperativa y ha '
    'completado todos los requisitos administrativos.'
)

p = doc.add_paragraph()
p.add_run('Proceso de Conversión:').bold = True

p = doc.add_paragraph()
p.add_run('1. ').bold = True
p.add_run('Accede a "Registrar caficultor".')

p = doc.add_paragraph()
p.add_run('2. ').bold = True
p.add_run('Selecciona el tipo de documento.')

p = doc.add_paragraph()
p.add_run('3. ').bold = True
p.add_run('Ingresa el número de documento del caficultor existente.')

p = doc.add_paragraph()
p.add_run('4. ').bold = True
p.add_run('El sistema busca automáticamente en la base de datos.')

p = doc.add_paragraph()
p.add_run('5. ').bold = True
p.add_run('Aparecerá un botón "Convertir a Socio" (en lugar de "Guardar").')

p = doc.add_paragraph()
p.add_run('6. ').bold = True
p.add_run('Haz clic y confirma la acción.')

p = doc.add_paragraph()
p.add_run('7. ').bold = True
p.add_run('El estado cambia de "No-Socio" a "Socio" y se registra la fecha.')

doc.add_heading('Errores Comunes en Registro de Caficultor', level=2)

errors = [
    ('Documento ya registrado',
     'Significa que ese documento existe en la base de datos. Verifica que sea el correcto.'),
    ('Formato de documento inválido',
     'El número no cumple con la validación. Revisa que sea el tipo correcto.'),
    ('Campo requerido vacío',
     'Todos los campos deben completarse. No puedes dejar ninguno en blanco.'),
    ('Nombre con caracteres especiales',
     'Algunos caracteres pueden no ser válidos. Usa solo letras, espacios y acentos.'),
]

for error, solution in errors:
    p = doc.add_paragraph()
    p.add_run(f'Error: {error}').bold = True
    doc.add_paragraph(f'Solución: {solution}', style='List Bullet 2')

add_section_break()

# ============ 7. REGISTRO DE MUESTRAS ============
doc.add_heading('7. Registro Detallado de Muestras', level=1)

doc.add_heading('Importancia del Registro Preciso', level=2)
doc.add_paragraph(
    'El registro de muestra es la etapa más crítica del proceso. Los datos que ingreses '
    'aquí determinarán:\n'
    '  - El cálculo de calidad\n'
    '  - El pago final del caficultor\n'
    '  - La categorización del café\n'
    '  - La trazabilidad del lote'
)
doc.add_paragraph(
    'Por lo tanto, es FUNDAMENTAL que los datos sean exactos y precisos. '
    'Revisa dos veces antes de enviar.'
)

doc.add_heading('Preparación Previa', level=2)
doc.add_paragraph(
    'Antes de acceder al formulario:\n'
    '  1. Asegúrate de que el caficultor esté registrado en el sistema\n'
    '  2. Verifica que la muestra esté lista y etiquetada\n'
    '  3. Calibra los equipos de peso (balanza, tamiz)\n'
    '  4. Verifica que la cámara esté conectada\n'
    '  5. Comprueba la conexión con el Arduino'
)

doc.add_heading('Acceso al Formulario', level=2)
p = doc.add_paragraph()
p.add_run('1. ').bold = True
p.add_run('Desde el menú, haz clic en "Registro de muestra".')

p = doc.add_paragraph()
p.add_run('2. ').bold = True
p.add_run('Verás un formulario de dos tarjetas (cards): "Datos del Caficultor" y "Datos de la Muestra".')

p = doc.add_paragraph()
p.add_run('3. ').bold = True
p.add_run('Los campos requeridos tienen un asterisco rojo (*).')

doc.add_heading('Sección 1: Datos del Caficultor', level=2)

doc.add_heading('Campo: Tipo Documento', level=3)
doc.add_paragraph('Control: Dropdown select')
doc.add_paragraph('Opciones: DNI, Pasaporte, Carnet de Extranjería')
doc.add_paragraph('Acción: Selecciona el tipo que corresponda al caficultor.')

doc.add_heading('Campo: Número Documento', level=3)
doc.add_paragraph('Control: Texto (máximo 12 caracteres)')
doc.add_paragraph('Validación: Según el tipo seleccionado')
doc.add_paragraph(
    'Comportamiento Especial:\n'
    '  - Mientras escribes, el sistema busca automáticamente en la BD\n'
    '  - Si encuentra coincidencia, muestra: "Caficultor encontrado"\n'
    '  - Si no encuentra, muestra: "Caficultor no registrado"\n'
    '  - Si no encuentra, debes registrarlo primero en "Registrar Caficultor"'
)

doc.add_heading('Campo: Nombre Caficultor', level=3)
doc.add_paragraph('Tipo: Texto readonly (solo lectura)')
doc.add_paragraph(
    'Comportamiento:\n'
    '  - Se completa AUTOMÁTICAMENTE cuando el sistema encuentra el documento\n'
    '  - No puedes escribir en este campo\n'
    '  - Si está vacío, significa que el documento no existe'
)

doc.add_heading('Campo: Tipo Caficultor', level=3)
doc.add_paragraph('Tipo: Texto readonly')
doc.add_paragraph(
    'Comportamiento:\n'
    '  - Muestra "Socio" o "No-Socio"\n'
    '  - Se llena automáticamente al encontrar el documento\n'
    '  - Indica si el caficultor está afiliado a la cooperativa'
)

doc.add_heading('Sección 2: Datos de la Muestra', level=2)

doc.add_heading('Fila 1: Tipo de Grano y Número de Sacos', level=3)

doc.add_paragraph('TIPO DE GRANO')
doc.add_paragraph('Control: Dropdown select', style='List Bullet')
doc.add_paragraph('Opciones:', style='List Bullet')
doc.add_paragraph('Coco: Grano deshojado sin pelar', style='List Bullet 2')
doc.add_paragraph('Pergamino: Grano con película plateada', style='List Bullet 2')
doc.add_paragraph('Pilado: Grano pelado listo para exportar', style='List Bullet 2')
doc.add_paragraph(
    'Nota: El tipo de grano afecta los cálculos de pago (cada uno tiene peso de referencia diferente).'
)

doc.add_paragraph('NÚMERO DE SACOS')
doc.add_paragraph('Control: Número entero', style='List Bullet')
doc.add_paragraph('Rango válido: 1 a 999', style='List Bullet')
doc.add_paragraph('Validación: Debe ser >= 1', style='List Bullet')
doc.add_paragraph('Propósito: Cantidad de sacos del lote para cálculo de tara (0.25 kg por saco)', style='List Bullet')

doc.add_heading('Fila 2: Peso Total y Humedad', level=3)

doc.add_paragraph('PESO TOTAL (KG)')
doc.add_paragraph('Control: Número decimal', style='List Bullet')
doc.add_paragraph('Unidad: Kilogramos', style='List Bullet')
doc.add_paragraph('Validación: > 0', style='List Bullet')
doc.add_paragraph('Ejemplo: 275.50', style='List Bullet')
doc.add_paragraph(
    'Propósito: Peso bruto del lote tal como se recibe. '
    'Incluye humedad y será ajustado en función de este valor.'
)

doc.add_paragraph('HUMEDAD (%)')
doc.add_paragraph('Control: Número decimal', style='List Bullet')
doc.add_paragraph('Rango válido: 0.01 a 100', style='List Bullet')
doc.add_paragraph('Validación: Debe estar entre 0.01 y 100', style='List Bullet')
doc.add_paragraph('Ejemplo: 12.50', style='List Bullet')
doc.add_paragraph(
    'Propósito: Porcentaje de agua en el grano. Es crítico para el cálculo de pago. '
    'Si humedad > 12%, se descuenta peso proporcionalmente.'
)

doc.add_heading('Fila 3: Peso de Muestra y Peso Trillado', level=3)

doc.add_paragraph('PESO DE MUESTRA (GR)')
doc.add_paragraph('Control: Número decimal', style='List Bullet')
doc.add_paragraph('Unidad: Gramos', style='List Bullet')
doc.add_paragraph('Validación: > 0', style='List Bullet')
doc.add_paragraph('Ejemplo: 1200.00', style='List Bullet')
doc.add_paragraph(
    'Propósito: Porción representativa del lote para análisis. '
    'Típicamente 1000-1500 gramos según el tipo de grano.'
)

doc.add_paragraph('PESO TRILLADO (GR)')
doc.add_paragraph('Control: Número decimal', style='List Bullet')
doc.add_paragraph('Unidad: Gramos', style='List Bullet')
doc.add_paragraph('Validación: > 0 y <= Peso de Muestra', style='List Bullet')
doc.add_paragraph('Ejemplo: 930.00', style='List Bullet')
doc.add_paragraph(
    'Propósito: Peso de la muestra después de remover la cáscara. '
    'Siempre debe ser menor que el peso de muestra original.'
)
doc.add_paragraph('Validación: Si ingresas un valor > peso de muestra, aparecerá error.', style='List Bullet')

doc.add_heading('Fila 4: Número de Tamiz y Peso Tamizado', level=3)

doc.add_paragraph('NÚMERO DE TAMIZ')
doc.add_paragraph('Control: Número entero', style='List Bullet')
doc.add_paragraph('Rango válido: 1 a 20', style='List Bullet')
doc.add_paragraph('Validación: >= 1', style='List Bullet')
doc.add_paragraph('Ejemplo: 14', style='List Bullet')
doc.add_paragraph(
    'Propósito: Tamaño de la malla usada (número de agujeros por pulgada). '
    'Mayor número = malla más fina.'
)

doc.add_paragraph('PESO TAMIZADO (GR)')
doc.add_paragraph('Control: Número decimal', style='List Bullet')
doc.add_paragraph('Unidad: Gramos', style='List Bullet')
doc.add_paragraph('Validación: > 0 y <= Peso Trillado', style='List Bullet')
doc.add_paragraph('Ejemplo: 870.00', style='List Bullet')
doc.add_paragraph(
    'Propósito: Peso de la muestra después de pasar por el tamiz. '
    'Granos más grandes pasan, más pequeños quedan.'
)
doc.add_paragraph('Validación: Si ingresas un valor > peso trillado, aparecerá error.', style='List Bullet')

add_section_break()

# ============ 8. VALIDACIÓN DE DATOS ============
doc.add_heading('8. Validación de Datos', level=1)

doc.add_heading('Sistema de Validación en Tiempo Real', level=2)
doc.add_paragraph(
    'CoffeeRen valida datos mientras escribes. No necesitas enviar para ver errores. '
    'Esto te permite corregir inmediatamente.'
)

doc.add_heading('Reglas de Validación Generales', level=2)

rules = [
    ('Campos Requeridos', 'Todos los campos marcados con * deben completarse. '
     'El botón de envío está deshabilitado si falta alguno.'),

    ('Números Positivos', 'Pesos, cantidades y medidas deben ser > 0. '
     'No se aceptan valores negativos.'),

    ('Coherencia Entre Campos', 'El peso trillado no puede exceder el peso de muestra. '
     'El peso tamizado no puede exceder el peso trillado.'),

    ('Formato de Documento', 'DNI = 8 dígitos, Pasaporte/Carnet = 8-12 caracteres. '
     'No se aceptan formatos incorrectos.'),

    ('Humedad Realista', 'Humedad debe estar entre 0.01 y 100%. '
     'Si ingresa 150%, el sistema rechaza.'),
]

for rule_name, rule_desc in rules:
    p = doc.add_paragraph()
    p.add_run(f'{rule_name}: ').bold = True
    p.add_run(rule_desc)

doc.add_heading('Indicadores Visuales', level=2)
doc.add_paragraph(
    'Los campos usan colores para indicar estado:\n'
    '  VERDE: Campo válido, datos correctos\n'
    '  ROJO: Campo inválido, corregir antes de enviar\n'
    '  GRIS: Campo readonly (no se puede editar)\n'
    '  AZUL: Campo seleccionado actualmente'
)

doc.add_heading('Mensajes de Error Específicos', level=2)

error_msgs = [
    ('Este campo es requerido.', 'El campo está vacío y es obligatorio.'),
    ('Valor debe ser mayor a 0.', 'Ingresaste un número negativo o cero.'),
    ('Peso trillado no puede exceder peso de muestra.',
     'El trillado es más pesado que la muestra. Revisa valores.'),
    ('El documento no está registrado.',
     'Ese caficultor no existe. Regístralo primero.'),
    ('Documento inválido para este tipo.',
     'El formato no coincide con el tipo de documento seleccionado.'),
]

for error, explanation in error_msgs:
    p = doc.add_paragraph()
    p.add_run(f'"{error}"').bold = True
    doc.add_paragraph(f'Significa: {explanation}', style='List Bullet 2')

doc.add_heading('Antes de Enviar', level=2)
doc.add_paragraph(
    'CHECKLIST de validación manual:\n'
    '  □ Caficultor está registrado en el sistema\n'
    '  □ Tipo de documento seleccionado coincide con el documento\n'
    '  □ Nombre y tipo de caficultor se cargaron automáticamente\n'
    '  □ Tipo de grano es el correcto para esta muestra\n'
    '  □ Todos los pesos son positivos y coherentes\n'
    '  □ Humedad está en rango realista (típicamente 10-14%)\n'
    '  □ Revisa valores dos veces para evitar errores de tipeo\n'
    '  □ Todos los campos están verdes (sin errores)'
)

add_section_break()

# ============ 9. MONITOREO ============
doc.add_heading('9. Monitoreo en Tiempo Real', level=1)

doc.add_heading('Inicio del Monitoreo', level=2)
doc.add_paragraph(
    'Cuando envías el formulario de registro, sucede lo siguiente:\n'
    '  1. El sistema valida todos los datos\n'
    '  2. Crea un registro de evaluación en la base de datos\n'
    '  3. Asigna un ID único (UUID) a la evaluación\n'
    '  4. Redirige automáticamente a la página de monitoreo\n'
    '  5. Inicia conexión con cámara y Arduino\n'
    '  6. Comienza cronómetro de tiempo\n'
    '  7. Máquina está lista para procesar la muestra'
)

doc.add_heading('Interfaz de Monitoreo', level=2)

doc.add_heading('Encabezado con Datos del Caficultor', level=3)
doc.add_paragraph(
    'Muestra: Documento, Nombre, Tipo, Grano, Tamiz, Sacos, Peso Bruto.\n'
    'Propósito: Verificación rápida de que es la muestra correcta.'
)

doc.add_heading('Feed de Cámara en Vivo', level=3)
doc.add_paragraph(
    'Muestra video en tiempo real de la banda transportadora.\n'
    'Si está en blanco/gris: Cámara conectando (espera 3-5 segundos)\n'
    'Si muestra error: Cámara no disponible (ver sección Troubleshooting)'
)

doc.add_heading('Indicador "En Vivo"', level=3)
doc.add_paragraph(
    'Punto rojo parpadeante = Monitoreo activo\n'
    'Se apaga cuando el monitoreo finaliza\n'
    'Propósito: Confirmación visual de que sistema está grabando'
)

doc.add_heading('Cronómetro', level=3)
doc.add_paragraph(
    'Muestra tiempo transcurrido (HH:MM:SS)\n'
    'Inicia en 00:00 y avanza constantemente\n'
    'Útil para estimar cuándo termina el procesamiento'
)

doc.add_heading('Panel de Estadísticas en Vivo', level=2)

stats_detailed = [
    ('Granos Evaluados', 'Total de granos detectados por la máquina desde el inicio'),
    ('Defectos Detectados', 'Cantidad de granos con problemas (negro, brocado, fermentado)'),
    ('Peso Bueno (gr)', 'Peso acumulado de granos sin defectos'),
    ('Precisión (%)', 'Confianza del modelo de IA (típicamente 80-95%)'),
]

for stat, desc in stats_detailed:
    p = doc.add_paragraph()
    p.add_run(f'{stat}: ').bold = True
    p.add_run(desc)

doc.add_heading('Supervisión del Operario Durante Monitoreo', level=2)
doc.add_paragraph(
    'Tu rol durante el monitoreo:\n'
    '  1. OBSERVAR: Supervisa que la máquina esté funcionando\n'
    '  2. VERIFICAR: Asegúrate de que el feed de cámara sea claro\n'
    '  3. CONTROLAR: Monitorea estadísticas de defectos\n'
    '  4. REACCIONAR: Si hay error, detén la máquina inmediatamente'
)

doc.add_heading('Problemas Durante Monitoreo', level=2)

monitor_issues = [
    ('Cámara oscura o pixelada',
     'Limpia lente de cámara. Verifica iluminación del laboratorio. '
     'Pausa máquina si es necesario.'),

    ('Números de granos no aumentan',
     'Verifica que granos estén pasando por el sensor. Pude haber atasco. '
     'Revisa conexión USB del Arduino.'),

    ('Peso bueno siempre en 0',
     'Significa que todos los granos se clasifican como defectuosos. '
     'Verifica calibración del modelo de IA o sensores.'),

    ('Presencia de atasco',
     'DETÉN INMEDIATAMENTE la máquina. Abre banda y retira el atasco. '
     'Recalibra y reinicia.'),
]

for issue, solution in monitor_issues:
    p = doc.add_paragraph()
    p.add_run(f'Problema: {issue}').bold = True
    doc.add_paragraph(f'Solución: {solution}', style='List Bullet 2')

doc.add_heading('Finalización del Monitoreo', level=2)
doc.add_paragraph(
    'El monitoreo finaliza cuando:\n'
    '  - Toda la muestra ha pasado por la máquina\n'
    '  - No hay más granos detectados por 5 segundos\n'
    '  - El operario detiene manualmente la máquina\n'
    '  - Se alcanza el tiempo límite (30 minutos)'
)

doc.add_paragraph('Automáticamente:')
doc.add_paragraph('Se captura el valor de "Peso Bueno" final', style='List Bullet')
doc.add_paragraph('Sistema calcula rendimiento, defectos, pago', style='List Bullet')
doc.add_paragraph('Página redirige a "Análisis de Resultados"', style='List Bullet')

add_section_break()

# ============ 10. ANÁLISIS ============
doc.add_heading('10. Análisis Inteligente de Resultados', level=1)

doc.add_heading('¿Qué es el Análisis?', level=2)
doc.add_paragraph(
    'Una vez finalizado el monitoreo, el sistema procesa TODOS los datos recolectados '
    'y genera un resumen completo con métricas de calidad, defectos, rendimiento y pago. '
    'Esta es la página más importante para tomar decisiones.'
)

doc.add_heading('Estructura de la Página de Análisis', level=2)

doc.add_heading('Toolbar de Acciones', level=3)
doc.add_paragraph('Título: "Resumen del análisis"')
doc.add_paragraph('Botones de exportación:', style='List Bullet')
doc.add_paragraph('Exportar PDF: Descarga reporte imprimible', style='List Bullet 2')
doc.add_paragraph('Exportar Excel: Descarga datos para análisis adicional', style='List Bullet 2')

doc.add_heading('Card de Información Básica', level=3)
doc.add_paragraph('Código EVA: Número único correlativo (EVA-001, EVA-002, etc.)')
doc.add_paragraph('Nombre Caficultor: Nombre completo')
doc.add_paragraph('Documento: Número de identificación')
doc.add_paragraph('Tipo Caficultor: Socio / No-Socio')
doc.add_paragraph('Tipo de Grano: Coco / Pergamino / Pilado')
doc.add_paragraph('Registrado por: Usuario operario que registró')
doc.add_paragraph('Fecha: Cuándo se realizó la evaluación')
doc.add_paragraph('Estado: "Finalizado" (confirmación visual)')

doc.add_heading('Tarjetas de Métricas Clave', level=3)

metrics = [
    ('Granos Evaluados',
     'Total de granos detectados y clasificados',
     'Propósito: Validar que se procesó muestra completa'),

    ('Defectos Totales',
     'Suma de granos: negro + brocado + fermentado',
     'Propósito: Indicador de calidad general'),

    ('Rendimiento IA',
     'Porcentaje de confianza del modelo automático',
     'Propósito: Validar exactitud de clasificación'),
]

for metric, value, purpose in metrics:
    doc.add_paragraph(f'{metric}', style='List Bullet')
    doc.add_paragraph(f'Definición: {value}', style='List Bullet 2')
    doc.add_paragraph(f'{purpose}', style='List Bullet 2')

doc.add_heading('Sección Detallada de Resultados', level=2)

doc.add_heading('Desglose de Defectos', level=3)
doc.add_paragraph(
    'Grano Negro: Grano fermentado interiormente, color oscuro'
)
doc.add_paragraph(
    'Grano Brocado: Presentar manchas o marcas en la superficie'
)
doc.add_paragraph(
    'Grano Fermentado: Evidencia de fermentación anómala'
)
doc.add_paragraph(
    'Otros Defectos: Plagas, roturas, malformaciones'
)

doc.add_heading('Datos del Lote Procesado', level=3)

doc.add_paragraph('Peso Bruto Registrado: Peso inicial del lote (kg)', style='List Bullet')
doc.add_paragraph('Peso Bueno Medido: Peso acumulado de granos sin defectos (gr)', style='List Bullet')
doc.add_paragraph('Número Sacos: Cantidad registrada', style='List Bullet')
doc.add_paragraph('Humedad Registrada: Porcentaje ingresado', style='List Bullet')
doc.add_paragraph('Rendimiento %: (Peso Bueno / Peso Muestra) × 100', style='List Bullet')

doc.add_heading('Cálculo de Pago', level=2)

doc.add_paragraph(
    'El sistema calcula el pago final automáticamente según esta fórmula:'
)

doc.add_paragraph()
doc.add_paragraph('1. Peso Neto = Peso Bruto - (Número Sacos × 0.25 kg)', style='List Bullet')
doc.add_paragraph('2. Si Humedad > 12%:', style='List Bullet')
doc.add_paragraph('   Exceso = Humedad - 12%', style='List Bullet 2')
doc.add_paragraph('   Descuento = Peso Neto × (Exceso / 100)', style='List Bullet 2')
doc.add_paragraph('   Peso Final = Peso Neto - Descuento', style='List Bullet 2')
doc.add_paragraph('3. Si Humedad <= 12%:', style='List Bullet')
doc.add_paragraph('   Peso Final = Peso Neto (sin descuento)', style='List Bullet 2')
doc.add_paragraph('4. Peso por Quintal = Peso Final / Peso Referencia del Tipo', style='List Bullet')
doc.add_paragraph('5. PAGO = Peso por Quintal × Precio Actual', style='List Bullet')

doc.add_heading('Ejemplo Práctico de Cálculo', level=2)

doc.add_paragraph('Datos de entrada:')
doc.add_paragraph('Peso Bruto: 275 kg', style='List Bullet')
doc.add_paragraph('Sacos: 5', style='List Bullet')
doc.add_paragraph('Humedad: 14%', style='List Bullet')
doc.add_paragraph('Tipo Grano: Pergamino (peso ref: 68 kg)', style='List Bullet')
doc.add_paragraph('Precio: S/ 4.50 / kg', style='List Bullet')

doc.add_paragraph()
doc.add_paragraph('Cálculo paso a paso:')
doc.add_paragraph('Tara (5 × 0.25) = 1.25 kg', style='List Bullet')
doc.add_paragraph('Peso Neto = 275 - 1.25 = 273.75 kg', style='List Bullet')
doc.add_paragraph('Humedad Exceso = 14 - 12 = 2%', style='List Bullet')
doc.add_paragraph('Descuento = 273.75 × (2/100) = 5.475 kg', style='List Bullet')
doc.add_paragraph('Peso Final = 273.75 - 5.475 = 268.275 kg', style='List Bullet')
doc.add_paragraph('Peso por Quintal = 268.275 / 68 = 3.945 quintales', style='List Bullet')
doc.add_paragraph('PAGO = 3.945 × 4.50 = S/ 17.75', style='List Bullet')

doc.add_heading('Interpretación de Resultados', level=2)

doc.add_paragraph('RENDIMIENTO BUENO: > 85%')
doc.add_paragraph('Significa: La mayoría de granos son de calidad. Lote aceptable.', style='List Bullet 2')

doc.add_paragraph('RENDIMIENTO MEDIO: 70-85%')
doc.add_paragraph('Significa: Hay defectos moderados. Lote regular.', style='List Bullet 2')

doc.add_paragraph('RENDIMIENTO BAJO: < 70%')
doc.add_paragraph('Significa: Muchos defectos. Revisar condiciones de almacenamiento.', style='List Bullet 2')

add_section_break()

# ============ 11. BÚSQUEDA ============
doc.add_heading('11. Búsqueda y Reportes', level=1)

doc.add_heading('Acceso al Módulo de Búsqueda', level=2)
p = doc.add_paragraph()
p.add_run('1. ').bold = True
p.add_run('Desde el menú, haz clic en "Buscar muestras".')

p = doc.add_paragraph()
p.add_run('2. ').bold = True
p.add_run('Verás un campo de entrada con instrucciones.')

p = doc.add_paragraph()
p.add_run('3. ').bold = True
p.add_run('El prefijo "EVA" está fijo. Solo debes ingresar números.')

doc.add_heading('¿Qué es el Código EVA?', level=2)
doc.add_paragraph(
    'EVA = Evaluación Asignada\n'
    '  Formato: EVA-00001, EVA-00002, etc.\n'
    '  Asignación: Correlativa, automática\n'
    '  Unidad: Interna de la cooperativa\n'
    '  Propósito: Identificación única internacional de cada muestra'
)

doc.add_heading('Cómo Buscar', level=2)

search_steps = [
    ('Obtén el Código EVA', 'Puedes tenerlo de:\n'
     '  - Comprobante entregado al caficultor\n'
     '  - Email de confirmación\n'
     '  - Pregunta directa al caficultor'),

    ('Ingresa en Campo', 'Solo escribie los números (ej: 001, 025, 042)\n'
     '  - No incluyas "EVA" (ya está)\n'
     '  - No espacios ni guiones\n'
     '  - Máximo 10 dígitos'),

    ('Haz Clic Buscar', 'Se ejecuta búsqueda en la base de datos\n'
     '  - Si existe: Muestra resultados\n'
     '  - Si no existe: Mensaje "No encontrado"'),

    ('Consulta Resultados', 'Aparecerán todos los datos de esa evaluación\n'
     '  - Información del caficultor\n'
     '  - Datos de la muestra\n'
     '  - Resultados de clasificación\n'
     '  - Pago calculado'),
]

for step_title, step_desc in search_steps:
    p = doc.add_paragraph()
    p.add_run(f'{step_title}: ').bold = True
    p.add_run(step_desc)

doc.add_heading('Resultados de Búsqueda', level=2)

doc.add_paragraph('Cuando encuentras una evaluación, aparecen:')

result_sections = [
    ('Card de Caficultor',
     'Nombre, Documento, Tipo (Socio/No-Socio)'),

    ('Card de Muestra',
     'Grano, Tamiz, Sacos, Pesos registrados, Humedad'),

    ('Card de Resultados',
     'Granos evaluados, Defectos, Rendimiento, Precisión IA'),

    ('Card de Pago',
     'Monto final en soles, Desglose de cálculos'),

    ('Card de Exportación',
     'Botones para descargar PDF o Excel'),
]

for section, content in result_sections:
    p = doc.add_paragraph()
    p.add_run(f'{section}: ').bold = True
    p.add_run(content)

doc.add_heading('Exportación de Reportes', level=2)

doc.add_heading('Exportar PDF', level=3)
doc.add_paragraph(
    'Formato: Documento imprimible profesional\n'
    'Contenido: Todos los datos y resultados\n'
    'Uso: Imprimir para archivo, entregar al caficultor\n'
    'Procedimiento: Haz clic en botón "Exportar PDF"'
)

doc.add_heading('Exportar Excel', level=3)
doc.add_paragraph(
    'Formato: Hoja de cálculo (compatible Excel, Google Sheets, LibreOffice)\n'
    'Contenido: Datos estructurados en columnas\n'
    'Uso: Análisis adicional, gráficos propios, auditoría\n'
    'Procedimiento: Haz clic en botón "Exportar Excel"'
)

add_section_break()

# ============ 12. PRECIOS ============
doc.add_heading('12. Gestión de Precios', level=1)

doc.add_heading('Acceso Restringido', level=2)
doc.add_paragraph(
    'IMPORTANTE: Este módulo solo es visible para:\n'
    '  - Usuarios con rol Gerente\n'
    '  - Usuarios con rol Administrador\n'
    'Si no ves "Valor Café" en el menú, tu rol no tiene permisos. '
    'Contacta al administrador.'
)

doc.add_heading('Importancia de los Precios', level=2)
doc.add_paragraph(
    'Los precios registrados en este módulo se usan automáticamente para calcular '
    'el pago de TODOS los caficultores. Un precio incorrecto afecta a muchas personas. '
    'Por lo tanto, VERIFICA SIEMPRE el precio antes de guardar.'
)

doc.add_heading('Acceso al Módulo', level=2)

p = doc.add_paragraph()
p.add_run('1. ').bold = True
p.add_run('Desde el menú principal, haz clic en "Valor Café".')

p = doc.add_paragraph()
p.add_run('2. ').bold = True
p.add_run('Verás una interfaz con gráfico de precios y opciones de registro.')

doc.add_heading('Registrar Nuevo Precio', level=2)

p = doc.add_paragraph()
p.add_run('Paso 1: Localiza el Formulario').bold = True
p = doc.add_paragraph('Aparece como una tarjeta "Registrar Precio".')

p = doc.add_paragraph()
p.add_run('Paso 2: Selecciona Rango').bold = True
p = doc.add_paragraph(
    'Dropdown con opciones: Extra, Prime, Buen Lavado, Regular, etc.\n'
    'Cada rango representa una categoría de calidad.'
)

p = doc.add_paragraph()
p.add_run('Paso 3: Ingresa Precio').bold = True
p = doc.add_paragraph(
    'Campo numérico en soles (S/).\n'
    'Ejemplo: 4.50\n'
    'Validación: Debe ser > 0'
)

p = doc.add_paragraph()
p.add_run('Paso 4: Verifica y Guardar').bold = True
p = doc.add_paragraph(
    'Revisa el precio dos veces.\n'
    'Haz clic en "Guardar".'
)

p = doc.add_paragraph()
p.add_run('Paso 5: Confirmación').bold = True
p = doc.add_paragraph(
    'Verás mensaje de éxito.\n'
    'El precio aparece en la lista de rangos.\n'
    'Será usado inmediatamente en nuevas evaluaciones.'
)

doc.add_heading('Historial de Precios', level=2)

doc.add_paragraph('El sistema muestra automáticamente:')

doc.add_paragraph('Precio Máximo Hoy: El mayor precio registrado en el día', style='List Bullet')
doc.add_paragraph('Cambio vs Ayer: Porcentaje de variación', style='List Bullet')
doc.add_paragraph('Rangos Registrados: Lista de todos los rangos con precio', style='List Bullet')
doc.add_paragraph('Gráfico de Tendencia: Visualización histórica', style='List Bullet')

doc.add_heading('Gráfico de Precios', level=2)

doc.add_paragraph('Período: Puedes filtrar por:')
doc.add_paragraph('Hoy: Variación cada hora', style='List Bullet')
doc.add_paragraph('Este Mes: Máximo diario', style='List Bullet')
doc.add_paragraph('Este Año: Máximo diario', style='List Bullet')

doc.add_paragraph('Filtro por Rango: Haz clic en un rango en la leyenda para ver solo ese rango.')

add_section_break()

# ============ 13. CÁLCULOS ============
doc.add_heading('13. Cálculos y Fórmulas de Pago', level=1)

doc.add_heading('Fórmula General de Pago', level=2)

doc.add_paragraph('PAGO = (Peso Final ÷ Peso Referencia) × Precio Actual')

doc.add_heading('Desglose Detallado', level=2)

doc.add_paragraph('PESO FINAL se calcula en varios pasos:', style='List Bullet')

doc.add_paragraph('Paso 1: Tara')
doc.add_paragraph('Tara = Número de Sacos × 0.25 kg / saco', style='List Bullet')
doc.add_paragraph('(Cada saco pesa aproximadamente 250 gramos)')

doc.add_paragraph('Paso 2: Peso Neto')
doc.add_paragraph('Peso Neto = Peso Bruto - Tara', style='List Bullet')

doc.add_paragraph('Paso 3: Ajuste por Humedad')
doc.add_paragraph('SI Humedad > 12%:', style='List Bullet')
doc.add_paragraph('Descuento = Peso Neto × ((Humedad - 12) / 100)', style='List Bullet 2')
doc.add_paragraph('Peso Final = Peso Neto - Descuento', style='List Bullet 2')
doc.add_paragraph('SI Humedad <= 12%:', style='List Bullet')
doc.add_paragraph('Peso Final = Peso Neto (sin descuento)', style='List Bullet 2')

doc.add_paragraph('Paso 4: Peso por Quintal')
doc.add_paragraph('Peso Referencia depende del tipo de grano:', style='List Bullet')

grain_ref = [
    ['Tipo', 'Peso Referencia (kg)'],
    ['Coco', '60'],
    ['Pergamino', '68'],
    ['Pilado', '70'],
]

table_grain = doc.add_table(rows=4, cols=2)
for row_idx, row_data in enumerate(grain_ref):
    for col_idx, cell_data in enumerate(row_data):
        cell = table_grain.rows[row_idx].cells[col_idx]
        cell.text = cell_data
        if row_idx == 0:
            set_cell_background(cell, '22c55e')
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(255, 255, 255)

doc.add_paragraph('Peso por Quintal = Peso Final ÷ Peso Referencia', style='List Bullet')

doc.add_paragraph('Paso 5: Cálculo Final')
doc.add_paragraph('PAGO = Peso por Quintal × Precio Actual (S/ por kg)', style='List Bullet')

doc.add_heading('Ejemplo Completo con Números', level=2)

doc.add_paragraph('Escenario:')
doc.add_paragraph('Caficultor: Juan Pérez (Socio)', style='List Bullet')
doc.add_paragraph('Grano: Pergamino', style='List Bullet')
doc.add_paragraph('Peso Bruto: 300 kg', style='List Bullet')
doc.add_paragraph('Sacos: 6', style='List Bullet')
doc.add_paragraph('Humedad: 13%', style='List Bullet')
doc.add_paragraph('Precio Actual: S/ 4.20 / kg', style='List Bullet')

doc.add_paragraph()
doc.add_paragraph('Cálculo:')

calc_steps = [
    ('Tara', '6 × 0.25 = 1.50 kg'),
    ('Peso Neto', '300 - 1.50 = 298.50 kg'),
    ('Descuento Humedad', '(13 - 12) = 1%, entonces 298.50 × 0.01 = 2.985 kg'),
    ('Peso Final', '298.50 - 2.985 = 295.515 kg'),
    ('Peso por Quintal', '295.515 ÷ 68 = 4.345 quintales'),
    ('PAGO FINAL', '4.345 × 4.20 = S/ 18.25'),
]

for step, calculation in calc_steps:
    p = doc.add_paragraph()
    p.add_run(f'{step}: ').bold = True
    p.add_run(calculation)

doc.add_heading('Casos Especiales', level=2)

doc.add_heading('Humedad Normal (10-12%)', level=3)
doc.add_paragraph('Sin descuento. Pago = (Peso Neto - Tara) ÷ Referencia × Precio')

doc.add_heading('Humedad Alta (> 15%)', level=3)
doc.add_paragraph('Descuento significativo. El pago se reduce considerablemente.')

doc.add_heading('Humedad Baja (< 10%)', level=3)
doc.add_paragraph('Bonificación implícita. El pago es ligeramente mayor.')

doc.add_heading('Lote Muy Defectuoso', level=3)
doc.add_paragraph('Aunque tenga muchos defectos, el pago se basa en peso real medido.')

add_section_break()

# ============ 14. FLUJOS ============
doc.add_heading('14. Flujos Operativos Completos', level=1)

doc.add_heading('Flujo Principal: Clasificación de Muestra', level=2)

doc.add_paragraph('FASE 1: PREPARACIÓN (5 minutos)')
doc.add_paragraph('Caficultor llega con muestra de café', style='List Bullet')
doc.add_paragraph('Operario verifica que caficultor esté registrado', style='List Bullet')
doc.add_paragraph('Si no existe, lo registra en "Registrar Caficultor"', style='List Bullet')
doc.add_paragraph('Operario prepara muestra (pesa, mide humedad, etc.)', style='List Bullet')

doc.add_paragraph('FASE 2: REGISTRO (5-10 minutos)')
doc.add_paragraph('Operario accede a "Registro de Muestra"', style='List Bullet')
doc.add_paragraph('Completa todos los datos técnicos', style='List Bullet')
doc.add_paragraph('Sistema valida automáticamente', style='List Bullet')
doc.add_paragraph('Envía el formulario', style='List Bullet')

doc.add_paragraph('FASE 3: MONITOREO (3-8 minutos)')
doc.add_paragraph('Sistema redirige a pantalla de monitoreo', style='List Bullet')
doc.add_paragraph('Máquina procesa la muestra automáticamente', style='List Bullet')
doc.add_paragraph('Operario supervisa feed de cámara', style='List Bullet')
doc.add_paragraph('Cuando termina, sistema genera análisis', style='List Bullet')

doc.add_paragraph('FASE 4: ANÁLISIS (inmediata)')
doc.add_paragraph('Se muestra página de resultados', style='List Bullet')
doc.add_paragraph('Operario verifica métricas de calidad', style='List Bullet')
doc.add_paragraph('Sistema calcula pago automáticamente', style='List Bullet')

doc.add_paragraph('FASE 5: ENTREGA (5 minutos)')
doc.add_paragraph('Operario anota código EVA y pago en comprobante', style='List Bullet')
doc.add_paragraph('Entrega comprobante al caficultor', style='List Bullet')
doc.add_paragraph('Caficultor puede consultar resultados en línea cuando desee', style='List Bullet')

doc.add_heading('Flujo Alternativo: Conversión a Socio', level=2)

doc.add_paragraph('Caficultor solicita ser socio', style='List Bullet')
doc.add_paragraph('Operario accede a "Registrar Caficultor"', style='List Bullet')
doc.add_paragraph('Ingresa número de documento del caficultor', style='List Bullet')
doc.add_paragraph('Sistema busca y carga datos automáticamente', style='List Bullet')
doc.add_paragraph('Sistema detecta que ya existe', style='List Bullet')
doc.add_paragraph('Aparece botón "Convertir a Socio" (en lugar de guardar)', style='List Bullet')
doc.add_paragraph('Operario hace clic y confirma', style='List Bullet')
doc.add_paragraph('Status cambia a "Socio" y se registra fecha', style='List Bullet')

doc.add_heading('Flujo de Consulta: Búsqueda de Evaluación Anterior', level=2)

doc.add_paragraph('Caficultor o operario necesita info de muestra anterior', style='List Bullet')
doc.add_paragraph('Accede a "Buscar Muestras"', style='List Bullet')
doc.add_paragraph('Ingresa código EVA', style='List Bullet')
doc.add_paragraph('Sistema busca y muestra todos los detalles', style='List Bullet')
doc.add_paragraph('Usuario exporta PDF para imprimir o Excel para análisis', style='List Bullet')

add_section_break()

# ============ 15. TROUBLESHOOTING ============
doc.add_heading('15. Troubleshooting y Problemas Comunes', level=1)

doc.add_heading('Problemas de Conexión', level=2)

doc.add_paragraph('PROBLEMA: "No puedo acceder a http://localhost:8000"')
doc.add_paragraph('Posibles causas:', style='List Bullet')
doc.add_paragraph('Servidor offline. Contacta al administrador.', style='List Bullet 2')
doc.add_paragraph('Dirección incorrecta. Verifica: localhost:8000', style='List Bullet 2')
doc.add_paragraph('Navegador incompatible. Usa Chrome o Edge.', style='List Bullet 2')
doc.add_paragraph('Firewall bloqueando. Contacta IT.', style='List Bullet 2')

doc.add_paragraph('PROBLEMA: "Página carga muy lentamente"')
doc.add_paragraph('Posibles causas:', style='List Bullet')
doc.add_paragraph('Red congestionada. Intenta en otro dispositivo.', style='List Bullet 2')
doc.add_paragraph('Servidor sobrecargado. Espera 5 minutos e intenta de nuevo.', style='List Bullet 2')
doc.add_paragraph('Caché de navegador. Presiona Ctrl+Shift+Del y limpia.', style='List Bullet 2')

doc.add_heading('Problemas de Cámara', level=2)

doc.add_paragraph('PROBLEMA: "Cámara no disponible" en monitoreo')
doc.add_paragraph('Soluciones:', style='List Bullet')
doc.add_paragraph('Verifica conexión USB. Reconecta el cable.', style='List Bullet 2')
doc.add_paragraph('Recarga la página (F5).', style='List Bullet 2')
doc.add_paragraph('Reinicia el servidor (contacta admin).', style='List Bullet 2')
doc.add_paragraph('Comprueba que no hay otro proceso usando la cámara.', style='List Bullet 2')

doc.add_paragraph('PROBLEMA: "Feed de cámara negro o pixelado"')
doc.add_paragraph('Soluciones:', style='List Bullet')
doc.add_paragraph('Limpia lente de cámara con paño suave.', style='List Bullet 2')
doc.add_paragraph('Verifica iluminación del laboratorio.', style='List Bullet 2')
doc.add_paragraph('Aumenta brillo/contraste si es posible.', style='List Bullet 2')

doc.add_heading('Problemas con Arduino', level=2)

doc.add_paragraph('PROBLEMA: "Peso bueno siempre es 0" en monitoreo')
doc.add_paragraph('Significa todos los granos se clasifican como defectuosos.', style='List Bullet')
doc.add_paragraph('Soluciones:', style='List Bullet')
doc.add_paragraph('Recalibra sensores del Arduino.', style='List Bullet 2')
doc.add_paragraph('Verifica conexión USB serial (9600 baud).', style='List Bullet 2')
doc.add_paragraph('Contacta técnico especializado.', style='List Bullet 2')

doc.add_paragraph('PROBLEMA: "Máquina no se enciende"')
doc.add_paragraph('Soluciones:', style='List Bullet')
doc.add_paragraph('Verifica alimentación eléctrica.', style='List Bullet 2')
doc.add_paragraph('Comprueba botón de encendido/apagado.', style='List Bullet 2')
doc.add_paragraph('Si hay humo o olor extraño, APAGA INMEDIATAMENTE y avisa.', style='List Bullet 2')

doc.add_heading('Problemas de Validación de Formularios', level=2)

doc.add_paragraph('PROBLEMA: "Error: Caficultor no registrado"')
doc.add_paragraph('Significa ese documento no existe en la BD.', style='List Bullet')
doc.add_paragraph('Soluciones:', style='List Bullet')
doc.add_paragraph('Verifica que el número sea exacto.', style='List Bullet 2')
doc.add_paragraph('Registra al caficultor primero en "Registrar Caficultor".', style='List Bullet 2')
doc.add_paragraph('Si el caficultor existe, contacta al administrador.', style='List Bullet 2')

doc.add_paragraph('PROBLEMA: "Peso trillado no puede exceder peso de muestra"')
doc.add_paragraph('Error de validación porque ingresaste valores incoherentes.', style='List Bullet')
doc.add_paragraph('Soluciones:', style='List Bullet')
doc.add_paragraph('El peso trillado (después de trillar) siempre es MENOR.', style='List Bullet 2')
doc.add_paragraph('Revisa valores ingresados. Intercambiaste valores?', style='List Bullet 2')
doc.add_paragraph('Corrige y vuelve a enviar.', style='List Bullet 2')

doc.add_heading('Problemas de Sesión', level=2)

doc.add_paragraph('PROBLEMA: "Sesión expirada" después de un tiempo')
doc.add_paragraph('Las sesiones expiran después de 7 días por seguridad.', style='List Bullet')
doc.add_paragraph('Soluciones:', style='List Bullet')
doc.add_paragraph('Inicia sesión nuevamente con tus credenciales.', style='List Bullet 2')
doc.add_paragraph('Para sesiones largas, contacta al administrador.', style='List Bullet 2')

doc.add_paragraph('PROBLEMA: "Contraseña olvidada"')
doc.add_paragraph('No puedes auto-resetear. Contacta al administrador.', style='List Bullet')
doc.add_paragraph('El administrador reiniciará tu contraseña.', style='List Bullet')
doc.add_paragraph('Recibirás una temporal. Debes cambiarla en el primer acceso.', style='List Bullet')

add_section_break()

# ============ 16. MEJORES PRÁCTICAS ============
doc.add_heading('16. Mejores Prácticas', level=1)

doc.add_heading('Práctica 1: Verifica Siempre Dos Veces', level=2)
doc.add_paragraph(
    'Antes de enviar un formulario, revisa todos los datos una segunda vez. '
    'Los errores de tipeo en pesos afectan el pago del caficultor.'
)

doc.add_heading('Práctica 2: Mantén Equipos Calibrados', level=2)
doc.add_paragraph(
    'Al inicio de cada día:\n'
    '  - Calibra la balanza con peso patrón\n'
    '  - Limpia lentes de cámara\n'
    '  - Comprueba conexiones USB\n'
    '  - Prueba flujo de muestra por la banda\n'
    '  - Verifica luz del laboratorio'
)

doc.add_heading('Práctica 3: Documenta Problemas', level=2)
doc.add_paragraph(
    'Si algo no funciona correctamente:\n'
    '  - Anota la hora exacta\n'
    '  - Describe lo que pasó\n'
    '  - Toma foto si es posible\n'
    '  - Notifica al administrador\n'
    '  - No lo ignores para la próxima muestra'
)

doc.add_heading('Práctica 4: Cierre de Sesión Seguro', level=2)
doc.add_paragraph(
    'Al terminar tu turno, SIEMPRE cierra sesión.\n'
    'Esto protege datos confidenciales de caficultores.\n'
    'No confíes en que la sesión expire automáticamente.'
)

doc.add_heading('Práctica 5: Comunica Cambios Importantes', level=2)
doc.add_paragraph(
    'Si el administrador cambia un precio importante:\n'
    '  - Verifica que el cambio se aplicó correctamente\n'
    '  - Notifica a caficultores si afecta evaluaciones pendientes\n'
    '  - Mantén registro de cambios de precio'
)

doc.add_heading('Práctica 6: Respalda Datos Importantes', level=2)
doc.add_paragraph(
    'Regularmente:\n'
    '  - Exporta evaluaciones en Excel para análisis\n'
    '  - Imprime reportes PDF para archivo\n'
    '  - Contacta al administrador para backups del servidor'
)

add_section_break()

# ============ 17. SEGURIDAD ============
doc.add_heading('17. Seguridad y Confidencialidad', level=1)

doc.add_heading('Información Confidencial', level=2)
doc.add_paragraph(
    'Los siguientes datos son CONFIDENCIALES:\n'
    '  - Documentos de identificación de caficultores\n'
    '  - Números de teléfono y direcciones\n'
    '  - Ingresos y montos de pago\n'
    '  - Contraseñas y tokens de sesión\n'
    '  - Evaluaciones técnicas y resultados'
)

doc.add_heading('Reglas de Seguridad', level=2)

security_rules = [
    ('No compartir credenciales',
     'Tu usuario y contraseña son solo tuyos. No los compartas con nadie.'),

    ('No dejar sesión abierta',
     'Siempre cierra sesión al terminar. No dejes dispositivo desatendido con CoffeeRen abierto.'),

    ('No tomar fotos de pantalla',
     'No fotografíes pantallas con datos de caficultores sin autorización.'),

    ('No imprimir innecesariamente',
     'Imprime solo reportes necesarios. Guarda papeles en lugar seguro.'),

    ('No compartir por email personal',
     'Nunca envíes datos de caficultores por email personal. Usa sistemas autorizados.'),

    ('No discutir datos públicamente',
     'No hables de evaluaciones o pagos de caficultores donde otros puedan escuchar.'),
]

for rule, explanation in security_rules:
    p = doc.add_paragraph()
    p.add_run(f'{rule}: ').bold = True
    p.add_run(explanation)

doc.add_heading('Incidentes de Seguridad', level=2)
doc.add_paragraph(
    'Si sospechas un incidente de seguridad:\n'
    '  1. Cierra sesión inmediatamente\n'
    '  2. Notifica al administrador\n'
    '  3. No intentes "arreglarlo" por tu cuenta\n'
    '  4. Proporciona detalles: qué, cuándo, cómo\n'
    '  5. Cambia tu contraseña en el próximo acceso'
)

add_section_break()

# ============ 18. PREGUNTAS FRECUENTES ============
doc.add_heading('18. Preguntas Frecuentes Ampliadas', level=1)

faqs_expanded = [
    ('¿Qué hago si registré datos incorrectos en una muestra?',
     'ACCIÓN INMEDIATA: Notifica al administrador con el código EVA. '
     'No puedes editar datos una vez registrados (para evitar fraudes). '
     'El administrador puede hacer correcciones manuales si es necesario.'),

    ('¿Puedo registrar a un caficultor sin documento?',
     'No. El sistema requiere documento válido (DNI, Pasaporte o Carnet). '
     'Todos los caficultores deben tener identificación legal para recibir pagos.'),

    ('¿Qué sucede si la máquina se apaga durante el monitoreo?',
     'El monitoreo se interrumpe. Los datos capturados hasta ese momento se guardan. '
     'Debes reiniciar la máquina y comenzar una NUEVA evaluación (nuevo EVA).'),

    ('¿Puedo exportar todas las evaluaciones de una vez?',
     'No desde la interfaz actual. La búsqueda es por código EVA individual. '
     'Contacta al administrador para reportes masivos o acceso a base de datos.'),

    ('¿Qué diferencia hay entre Socio y No-Socio?',
     'Socio: Miembro oficial de la cooperativa. Acceso a créditos y beneficios. '
     'No-Socio: Productor externo. Mismo proceso de clasificación pero sin beneficios.'),

    ('¿Cuánto tiempo se guardan las evaluaciones?',
     'Indefinidamente en la base de datos. Las evaluaciones nunca se eliminan por ley. '
     'Puedes consultar incluso evaluaciones de años anteriores.'),

    ('¿El sistema calcula rendimiento automáticamente?',
     'Sí. Rendimiento = (Granos Buenos / Total Granos) × 100. '
     'Se calcula automáticamente durante el monitoreo basado en detección IA.'),

    ('¿Cómo sé si una evaluación fue bien clasificada?',
     'Indicadores positivos: Rendimiento > 85%, Precisión IA > 80%, Defectos < 20%. '
     'Si valores están fuera de rango, verifica condiciones de almacenamiento de muestra.'),

    ('¿Puedo cambiar el precio después de ya haber usado uno?',
     'Sí, pero solo aplica a NUEVAS evaluaciones. Evaluaciones anteriores se mantienen con precio original.'),

    ('¿Qué pasa si dos operarios intentan registrar la misma muestra?',
     'El sistema impide registros duplicados. Una vez que se asigna un EVA, no se puede duplicar. '
     'Verifica antes de registrar si alguien ya procesó esa muestra.'),

    ('¿Es confidencial el número de documento del caficultor?',
     'Sí. No lo compartas públicamente. Es información protegida por ley de protección de datos.'),

    ('¿El sistema funciona sin internet?',
     'Sí. CoffeeRen funciona completamente en red local (offline). No necesita conexión a internet.'),
]

for pregunta, respuesta in faqs_expanded:
    p = doc.add_paragraph()
    p.add_run(f'P: {pregunta}').bold = True
    doc.add_paragraph(f'R: {respuesta}')

add_section_break()

# ============ 19. GLOSARIO ============
doc.add_heading('19. Glosario Técnico Completo', level=1)

glosario_dict = [
    ('Caficultor', 'Productor de café. Agricultor que cultiva y procesa café.'),

    ('Muestra', 'Porción representativa del lote para análisis. Típicamente 1-1.5 kg.'),

    ('Lote', 'Cantidad total de café que un caficultor trae para clasificación. Puede ser 100-500 kg.'),

    ('Evaluación', 'Proceso completo: registro, monitoreo, análisis de una muestra.'),

    ('EVA (Evaluación Asignada)', 'Código único correlativo (EVA-001, EVA-002, etc.) para cada evaluación.'),

    ('Monitoreo', 'Fase donde la muestra pasa por máquina. Tiempo real, 3-8 minutos.'),

    ('Defecto', 'Grano con problemas: negro, brocado, fermentado, plaga, rotura.'),

    ('Grano Negro', 'Grano fermentado interiormente. Color muy oscuro. No apto.'),

    ('Grano Brocado', 'Grano con manchas o marcas de plagas. Calidad reducida.'),

    ('Grano Fermentado', 'Grano con fermentación anómala. Sabor y olor desagradable.'),

    ('Peso Bruto', 'Peso total del lote sin descontar nada. Incluye agua y tara.'),

    ('Peso Neto', 'Peso bruto menos tara (sacos). Peso del grano puro.'),

    ('Tara', 'Peso del empaque (sacos). Se asume 0.25 kg por saco.'),

    ('Humedad', 'Porcentaje de agua en el grano. Normal: 10-12%. > 12% = descuento.'),

    ('Rendimiento', 'Porcentaje de granos buenos. Indicador de calidad general.'),

    ('Precisión IA', 'Confianza del modelo de inteligencia artificial. Típicamente 80-95%.'),

    ('Tamiz', 'Malla para clasificar granos por tamaño. Número = densidad de agujeros.'),

    ('Trillado', 'Proceso de separar grano de cáscara.'),

    ('Pilado', 'Café totalmente procesado listo para exportar.'),

    ('Pergamino', 'Café con película plateada intacta.'),

    ('Coco', 'Café deshojado sin pelar. Estado intermedio.'),

    ('Socio', 'Caficultor miembro oficial de la cooperativa. Tiene beneficios.'),

    ('No-Socio', 'Productor externo. Puede traer muestras pero sin beneficios de socio.'),

    ('Código EVA', 'Identificador único de evaluación (EVA-00001, EVA-00002, etc.).'),

    ('Pago Calculado', 'Monto en soles (S/) a pagar basado en peso neto y precio actual.'),

    ('Precio Referencial', 'Precio de mercado por kg según rango de calidad.'),

    ('Rango', 'Categoría de calidad: Extra, Prime, Buen Lavado, Regular, etc.'),

    ('Hardware', 'Máquina física: sensores, cámara, servo, banda transportadora.'),

    ('Arduino', 'Microcontrolador que controla sensores y motores de máquina.'),

    ('HX711', 'Sensor de peso (celda de carga). Lee peso en tiempo real.'),

    ('HC-SR04', 'Sensor ultrasónico de presencia. Detecta paso de granos.'),

    ('Servo Motor', 'Motor que desvía granos defectuosos.'),

    ('JWT', 'Token de sesión encriptado. Mantiene login activo.'),

    ('Sessión', 'Período de tiempo conectado al sistema. Expira después de 7 días.'),

    ('Credenciales', 'Usuario y contraseña. Identificación única en sistema.'),
]

for termino, definicion in glosario_dict:
    p = doc.add_paragraph()
    p.add_run(f'{termino}: ').bold = True
    p.add_run(definicion)

add_section_break()

# ============ 20. REFERENCIAS ============
doc.add_heading('20. Referencias y Soporte', level=1)

doc.add_heading('Información de Contacto de Soporte', level=2)
doc.add_paragraph('Para problemas técnicos, dudas o sugerencias:')
doc.add_paragraph()
doc.add_paragraph('Administrador del Sistema:')
doc.add_paragraph('  Correo: admin@cooperativa.pe')
doc.add_paragraph('  Teléfono: +51-986-XXX-XXXX')
doc.add_paragraph('  WhatsApp: +51-986-XXX-XXXX')
doc.add_paragraph('  Horario: Lunes-Viernes 8:00-17:00')

doc.add_heading('Documentación Adicional', level=2)
doc.add_paragraph('Documentos disponibles para consulta:')
doc.add_paragraph('  - Manual Técnico del Hardware')
doc.add_paragraph('  - Guía de Administración del Sistema')
doc.add_paragraph('  - Políticas de Seguridad de Datos')
doc.add_paragraph('  - Procedimiento de Calibración de Equipos')
doc.add_paragraph('  - Estándares de Calidad de Café')

doc.add_heading('Versión del Manual', level=2)
doc.add_paragraph(f'Versión: 2.0 Completa')
doc.add_paragraph(f'Fecha: {datetime.now().strftime("%d de %B de %Y")}')
doc.add_paragraph('Actualización: Se revisa anualmente o cuando hay cambios significativos')

doc.add_heading('Notas Finales', level=2)
doc.add_paragraph(
    'Este manual fue diseñado para ser tu referencia completa en el uso de CoffeeRen. '
    'Si una sección no está clara, contacta al administrador para aclaraciones.'
)

doc.add_paragraph(
    'Recuerda: La precisión, integridad y confidencialidad de los datos es responsabilidad '
    'de todos. CoffeeRen funciona correctamente porque cada operario realiza su trabajo correctamente.'
)

doc.add_paragraph(
    'Gracias por ser parte de la transformación digital de la Cooperativa Lonya Grande.'
)

# Guardar
output_path = 'd:\\TesisPrj\\Manual_Usuario_CoffeeRen_Completo.docx'
doc.save(output_path)
print(f'Manual completo generado: {output_path}')
print('Páginas estimadas: 50+')
