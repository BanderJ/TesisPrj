#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generador de manual de usuario para CoffeeRen en formato Word"""

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

doc = Document()
section = doc.sections[0]
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)

# ============ PORTADA ============
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title_run = title.add_run('COFFEREN')
title_run.font.size = Pt(48)
title_run.font.bold = True
title_run.font.color.rgb = RGBColor(34, 197, 94)

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
subtitle_run = subtitle.add_run('Sistema de Clasificación Inteligente de Café Verde')
subtitle_run.font.size = Pt(18)
subtitle_run.font.color.rgb = RGBColor(100, 100, 100)

doc.add_paragraph()
doc.add_paragraph()

desc = doc.add_paragraph()
desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
desc_run = desc.add_run('Manual del Usuario - Guía Operativa Completa')
desc_run.font.size = Pt(14)
desc_run.font.italic = True

doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

info = doc.add_paragraph()
info.alignment = WD_ALIGN_PARAGRAPH.CENTER
info_run = info.add_run(f'Versión 1.0\n{datetime.now().strftime("%B de %Y")}')
info_run.font.size = Pt(11)

doc.add_page_break()

# ============ TABLA DE CONTENIDOS ============
doc.add_heading('Tabla de Contenidos', level=1)

toc_items = [
    '1. Introducción',
    '2. Descripción General del Sistema',
    '3. Acceso al Sistema',
    '4. Interfaz Principal',
    '5. Módulo: Registro de Caficultor',
    '6. Módulo: Registro de Muestra',
    '7. Módulo: Monitoreo en Tiempo Real',
    '8. Módulo: Análisis de Resultados',
    '9. Módulo: Búsqueda de Muestras',
    '10. Módulo: Gestión de Precios de Café',
    '11. Flujos Principales',
    '12. Preguntas Frecuentes',
    '13. Glosario de Términos',
]

for item in toc_items:
    p = doc.add_paragraph(item, style='List Bullet')

doc.add_page_break()

# ============ INTRODUCCIÓN ============
doc.add_heading('1. Introducción', level=1)

doc.add_heading('Propósito de este Manual', level=2)
doc.add_paragraph(
    'Este manual proporciona orientación detallada para los operarios, gerentes y administradores '
    'que utilizan CoffeeRen, el sistema de clasificación inteligente de café verde. El objetivo es '
    'garantizar que todos los usuarios comprendan cómo navegar, registrar datos, monitorear procesos '
    'y analizar resultados de manera eficiente y precisa.'
)

doc.add_heading('A Quién Va Dirigido', level=2)
p = doc.add_paragraph()
p.add_run('Operarios de laboratorio: ').bold = True
p.add_run('Registran caficultores, ingresan datos de muestras y supervisan el monitoreo en tiempo real.')
p = doc.add_paragraph()
p.add_run('Gerentes: ').bold = True
p.add_run('Acceden a reportes, historial de precios y estadísticas de producción.')
p = doc.add_paragraph()
p.add_run('Administradores: ').bold = True
p.add_run('Controlan usuarios, precios de café y configuración del sistema.')

doc.add_page_break()

# ============ DESCRIPCIÓN GENERAL ============
doc.add_heading('2. Descripción General del Sistema', level=1)

doc.add_heading('¿Qué es CoffeeRen?', level=2)
doc.add_paragraph(
    'CoffeeRen es una plataforma web integrada que combina hardware especializado (sensores de peso, '
    'cámaras, servo motores) con inteligencia artificial para clasificar automáticamente granos de café. '
    'El sistema registra datos técnicos de cada muestra, monitorea el proceso en tiempo real y genera '
    'reportes detallados de calidad, defectos y rendimiento.'
)

doc.add_heading('Flujo General del Proceso', level=2)
doc.add_paragraph(
    '1. Un productor de café (caficultor) lleva su muestra al laboratorio.\n'
    '2. El operario registra los datos técnicos del caficultor y la muestra (pesos, humedad, tipo de grano).\n'
    '3. El sistema inicia el monitoreo automático: la muestra pasa por la banda transportadora.\n'
    '4. La cámara e inteligencia artificial detectan granos defectuosos en tiempo real.\n'
    '5. Se calcula automáticamente el rendimiento y el pago correspondiente.\n'
    '6. Se genera un código único (EVA) para cada muestra y un resumen de análisis.\n'
    '7. El operario o el caficultor pueden consultar resultados en cualquier momento.'
)

doc.add_heading('Componentes Principales', level=2)
p = doc.add_paragraph()
p.add_run('Registro de Caficultores: ').bold = True
p.add_run('Base de datos de productores con información de contacto y documentación.')
p = doc.add_paragraph()
p.add_run('Registro de Muestras: ').bold = True
p.add_run('Captura técnica de datos físicos (pesos, humedad, tipo de grano).')
p = doc.add_paragraph()
p.add_run('Monitoreo en Vivo: ').bold = True
p.add_run('Supervisión en tiempo real con cámara y sensores.')
p = doc.add_paragraph()
p.add_run('Análisis Inteligente: ').bold = True
p.add_run('Clasificación automática de defectos usando visión artificial.')
p = doc.add_paragraph()
p.add_run('Reportes Históricos: ').bold = True
p.add_run('Búsqueda y consulta de evaluaciones anteriores.')
p = doc.add_paragraph()
p.add_run('Gestión de Precios: ').bold = True
p.add_run('Registrar y visualizar precios de café por rango de calidad.')

doc.add_page_break()

# ============ ACCESO AL SISTEMA ============
doc.add_heading('3. Acceso al Sistema', level=1)

doc.add_heading('Requisitos Previos', level=2)
doc.add_paragraph(
    'Un dispositivo con navegador web (Chrome, Edge, Firefox o Safari recomendados)\n'
    'Conexión a internet estable\n'
    'Credenciales de acceso (usuario y contraseña) proporcionadas por el administrador'
)

doc.add_heading('Inicio de Sesión', level=2)
p = doc.add_paragraph()
p.add_run('1. ').bold = True
p.add_run('Abre tu navegador e ingresa a la dirección: http://localhost:8000')
p = doc.add_paragraph()
p.add_run('2. ').bold = True
p.add_run('Verás una pantalla de login con dos campos:')
p = doc.add_paragraph('    Usuario (tu nombre de usuario)')
p = doc.add_paragraph('    Contraseña (tu contraseña confidencial)')
p = doc.add_paragraph()
p.add_run('3. ').bold = True
p.add_run('Ingresa tus credenciales y haz clic en "Ingresar".')
p = doc.add_paragraph()
p.add_run('4. ').bold = True
p.add_run('Si las credenciales son correctas, accederás al panel principal (Inicio).')

doc.add_page_break()

# ============ INTERFAZ PRINCIPAL ============
doc.add_heading('4. Interfaz Principal', level=1)

doc.add_heading('Descripción de la Pantalla de Inicio', level=2)
doc.add_paragraph(
    'La pantalla principal (Inicio) es tu centro de operaciones. Desde aquí puedes acceder '
    'a todos los módulos del sistema y visualizar información crítica en tiempo real.'
)

doc.add_heading('Elementos de la Interfaz', level=2)
p = doc.add_paragraph()
p.add_run('Encabezado (Header): ').bold = True
p.add_run('En la parte superior contiene el logo de CoffeeRen, el menú de navegación y opciones de usuario.')
p = doc.add_paragraph()
p.add_run('Menú de Navegación: ').bold = True
p.add_run('Accesos directos a las secciones principales del sistema.')
p = doc.add_paragraph()
p.add_run('Panel de KPIs: ').bold = True
p.add_run('Métricas rápidas (lotes procesados, rendimiento promedio, defectos detectados).')
p = doc.add_paragraph()
p.add_run('Gráfico de Precios: ').bold = True
p.add_run('Visualización del histórico de precios de café por rango de calidad.')
p = doc.add_paragraph()
p.add_run('Flujo Operativo: ').bold = True
p.add_run('Tarjetas de acceso rápido a las acciones más comunes.')

doc.add_heading('Menú de Navegación', level=2)
items = [
    ('Inicio', 'Vuelve al panel principal y al dashboard'),
    ('Registro de muestra', 'Accede al formulario para registrar una nueva muestra de café'),
    ('Buscar muestras', 'Consulta evaluaciones anteriores por código EVA'),
    ('Registrar caficultor', 'Ingresa nuevos productores o convierte a socio'),
    ('Valor Café', 'Administra precios (solo para Gerente/Admin)'),
]
for menu_item, desc in items:
    p = doc.add_paragraph()
    p.add_run(f'{menu_item}: ').bold = True
    p.add_run(desc)

doc.add_page_break()

# ============ REGISTRO DE CAFICULTOR ============
doc.add_heading('5. Módulo: Registro de Caficultor', level=1)

doc.add_heading('¿Qué es un Caficultor?', level=2)
doc.add_paragraph(
    'Un caficultor es el productor de café (agricultor) que lleva sus muestras al laboratorio '
    'para clasificación. CoffeeRen mantiene un registro de todos los productores, su documentación '
    'y su estado (Socio o no-Socio de la cooperativa).'
)

doc.add_heading('Registrar un Nuevo Caficultor', level=2)
p = doc.add_paragraph()
p.add_run('1. ').bold = True
p.add_run('Desde el menú principal, haz clic en "Registrar caficultor".')
p = doc.add_paragraph()
p.add_run('2. ').bold = True
p.add_run('Completa el formulario con la siguiente información:')
p = doc.add_paragraph('    Tipo de Documento: DNI, Pasaporte o Carnet de Extranjería')
p = doc.add_paragraph('    Número de Documento: El número correspondiente al documento seleccionado')
p = doc.add_paragraph('    Nombre Completo: Nombre y apellido del caficultor')
p = doc.add_paragraph()
p.add_run('3. ').bold = True
p.add_run('Verifica que los datos sean correctos.')
p = doc.add_paragraph()
p.add_run('4. ').bold = True
p.add_run('Haz clic en "Guardar" para registrar al caficultor.')

doc.add_heading('Validación de Documentos', level=2)
doc.add_paragraph(
    'El sistema valida automáticamente el formato del documento:\n'
    'DNI: debe ser exactamente 8 dígitos numéricos\n'
    'Pasaporte: 8 a 12 caracteres alfanuméricos\n'
    'Carnet de Extranjería: 8 a 12 caracteres alfanuméricos'
)

doc.add_page_break()

# ============ REGISTRO DE MUESTRA ============
doc.add_heading('6. Módulo: Registro de Muestra', level=1)

doc.add_heading('¿Por Qué Registrar Muestras?', level=2)
doc.add_paragraph(
    'El registro de muestra es el primer paso en el proceso de clasificación. Aquí se capturan '
    'todos los datos técnicos que identifican y caracterizan el lote de café del productor. '
    'Estos datos son esenciales para el cálculo de pagos y análisis de calidad.'
)

doc.add_heading('Datos del Caficultor', level=2)
p = doc.add_paragraph()
p.add_run('Tipo Documento: ').bold = True
p.add_run('Selecciona el tipo de documento identificación (DNI, Pasaporte, Carnet).')
p = doc.add_paragraph()
p.add_run('Número Documento: ').bold = True
p.add_run('Ingresa el número. El sistema automáticamente busca si el caficultor existe.')
p = doc.add_paragraph()
p.add_run('Nombre Caficultor: ').bold = True
p.add_run('Se completa automáticamente cuando se encuentra el documento.')
p = doc.add_paragraph()
p.add_run('Tipo Caficultor: ').bold = True
p.add_run('Indica si es Socio o no-Socio (se carga automáticamente).')

doc.add_heading('Datos de la Muestra', level=2)
items_muestra = [
    ('Tipo de Grano', 'Selecciona entre: Coco, Pergamino o Pilado'),
    ('Número de Sacos', 'Cantidad de sacos del lote (mínimo 1)'),
    ('Peso Total (kg)', 'Peso bruto total del lote en kilogramos'),
    ('Humedad (%)', 'Porcentaje de humedad del grano (0-100%)'),
    ('Peso de Muestra (gr)', 'Peso de la muestra representativa en gramos'),
    ('Peso Trillado (gr)', 'Peso después del proceso de trillado'),
    ('Número de Tamiz', 'Tamaño del tamiz usado (número entero)'),
    ('Peso Tamizado (gr)', 'Peso después de pasar por el tamiz'),
]
for label, desc in items_muestra:
    p = doc.add_paragraph()
    p.add_run(f'{label}: ').bold = True
    p.add_run(desc)

doc.add_heading('Validaciones Automáticas', level=2)
doc.add_paragraph(
    'El formulario valida automáticamente mientras escribes:\n'
    'Los campos numéricos deben ser positivos\n'
    'El peso trillado no puede exceder el peso de muestra\n'
    'El peso tamizado no puede exceder el peso trillado\n'
    'Los mensajes de error aparecen debajo de cada campo'
)

doc.add_page_break()

# ============ MONITOREO ============
doc.add_heading('7. Módulo: Monitoreo en Tiempo Real', level=1)

doc.add_heading('¿Qué es el Monitoreo?', level=2)
doc.add_paragraph(
    'El monitoreo es la fase donde el café pasa por la máquina clasificadora. En tiempo real, '
    'el sistema registra cada grano, detecta defectos usando visión artificial y recolecta '
    'datos de peso y calidad.'
)

doc.add_heading('Durante el Monitoreo', level=2)
doc.add_paragraph(
    'Supervisa el feed de cámara para verificar que la máquina funcione correctamente.\n'
    'Observa las estadísticas en tiempo real (granos evaluados, defectos, peso bueno).\n'
    'Si algo falla, detén inmediatamente la máquina.\n'
    'Una vez que toda la muestra ha pasado, el sistema avanza automáticamente a análisis.'
)

doc.add_page_break()

# ============ ANÁLISIS ============
doc.add_heading('8. Módulo: Análisis de Resultados', level=1)

doc.add_heading('¿Qué es el Análisis?', level=2)
doc.add_paragraph(
    'Una vez finalizado el monitoreo, el sistema procesa todos los datos y genera '
    'un resumen detallado con métricas de calidad, categorización y cálculo de pago.'
)

doc.add_heading('Información del Análisis', level=2)
p = doc.add_paragraph()
p.add_run('Código EVA: ').bold = True
p.add_run('Identificador único correlativo de la evaluación.')
p = doc.add_paragraph()
p.add_run('Caficultor: ').bold = True
p.add_run('Nombre y documento del productor.')
p = doc.add_paragraph()
p.add_run('Granos Evaluados: ').bold = True
p.add_run('Total de granos procesados.')
p = doc.add_paragraph()
p.add_run('Defectos Totales: ').bold = True
p.add_run('Número de granos con problemas.')
p = doc.add_paragraph()
p.add_run('Rendimiento: ').bold = True
p.add_run('Porcentaje de granos buenos.')
p = doc.add_paragraph()
p.add_run('Pago Calculado: ').bold = True
p.add_run('Monto a pagar basado en peso neto, humedad y precio de mercado.')

doc.add_page_break()

# ============ BÚSQUEDA ============
doc.add_heading('9. Módulo: Búsqueda de Muestras', level=1)

doc.add_heading('Buscar Evaluaciones Anteriores', level=2)
p = doc.add_paragraph()
p.add_run('1. ').bold = True
p.add_run('Desde el menú, haz clic en "Buscar muestras".')
p = doc.add_paragraph()
p.add_run('2. ').bold = True
p.add_run('Ingresa los números del código EVA (ej: 001, 025, 042).')
p = doc.add_paragraph()
p.add_run('3. ').bold = True
p.add_run('Haz clic en "Buscar".')
p = doc.add_paragraph()
p.add_run('4. ').bold = True
p.add_run('El sistema mostrará todos los detalles de esa evaluación.')
p = doc.add_paragraph()
p.add_run('5. ').bold = True
p.add_run('Opcionalmente, exporta en PDF o Excel.')

doc.add_page_break()

# ============ PRECIOS ============
doc.add_heading('10. Módulo: Gestión de Precios de Café', level=1)

doc.add_heading('Nota de Acceso', level=2)
doc.add_paragraph(
    'Este módulo solo es accesible para Gerentes o Administradores. '
    'Si no lo ves en el menú, tu rol no tiene permisos.'
)

doc.add_heading('Registrar un Nuevo Precio', level=2)
p = doc.add_paragraph()
p.add_run('1. ').bold = True
p.add_run('Desde el menú, haz clic en "Valor Café".')
p = doc.add_paragraph()
p.add_run('2. ').bold = True
p.add_run('Selecciona el rango de calidad y el precio.')
p = doc.add_paragraph()
p.add_run('3. ').bold = True
p.add_run('Haz clic en "Guardar".')
p = doc.add_paragraph()
p.add_run('4. ').bold = True
p.add_run('El precio se usará automáticamente en cálculos futuros.')

doc.add_heading('Visualizar Historial', level=2)
doc.add_paragraph(
    'El panel muestra precio máximo actual, cambio respecto a ayer y gráfico de tendencia. '
    'Puedes filtrar por período (día, mes, año) y por rango.'
)

doc.add_page_break()

# ============ FLUJOS ============
doc.add_heading('11. Flujos Principales', level=1)

doc.add_heading('Flujo Completo: De Caficultor a Pago', level=2)

table = doc.add_table(rows=7, cols=2)
table.style = 'Light Grid Accent 1'
hdr_cells = table.rows[0].cells
hdr_cells[0].text = 'Paso'
hdr_cells[1].text = 'Acción'

flujo_steps = [
    ('1. Registrar Caficultor', 'Verifica si el productor existe; si no, regístralo.'),
    ('2. Registrar Muestra', 'Completa datos técnicos del lote (pesos, humedad, tipo).'),
    ('3. Iniciar Monitoreo', 'Al enviar, inicia automáticamente el monitoreo en vivo.'),
    ('4. Supervisar', 'Observa la cámara y estadísticas en tiempo real.'),
    ('5. Análisis', 'El sistema genera resumen de calidad y calcula pago.'),
    ('6. Entregar Resultado', 'Comunica código EVA y resultados al caficultor.'),
]

for i, (step, desc) in enumerate(flujo_steps, 1):
    row_cells = table.rows[i].cells
    row_cells[0].text = step
    row_cells[1].text = desc

doc.add_page_break()

# ============ PREGUNTAS FRECUENTES ============
doc.add_heading('12. Preguntas Frecuentes', level=1)

faqs = [
    ('¿Qué hago si el caficultor no está registrado?',
     'Accede a Registrar Caficultor, completa datos y guarda.'),

    ('¿Qué validaciones tiene el formulario?',
     'Verifica que pesos sean positivos y coherentes entre sí.'),

    ('¿Puedo modificar datos después de registrar?',
     'No, los datos se bloquean para garantizar integridad.'),

    ('¿Qué es el código EVA?',
     'Código único asignado automáticamente a cada muestra procesada.'),

    ('¿Cómo se calcula el pago?',
     'Peso neto - ajuste por humedad, dividido por referencia, por precio actual.'),

    ('¿Puedo exportar resultados?',
     'Sí, en PDF (impresión) o Excel (análisis adicional).'),

    ('¿Qué pasa si la cámara se desconecta?',
     'El monitoreo se pausa. Reconecta y recarga la página.'),

    ('¿Quién puede cambiar precios?',
     'Solo Gerentes o Administradores.'),

    ('¿Cuánto dura el monitoreo?',
     'Típicamente 3 a 8 minutos dependiendo del tamaño del lote.'),

    ('¿Dónde veo el historial?',
     'En Buscar Muestras, usando el código EVA.'),
]

for pregunta, respuesta in faqs:
    p = doc.add_paragraph()
    p.add_run(f'P: {pregunta}').bold = True
    doc.add_paragraph(f'R: {respuesta}')

doc.add_page_break()

# ============ GLOSARIO ============
doc.add_heading('13. Glosario de Términos', level=1)

glosario = [
    ('Caficultor', 'Productor o agricultor que cultiva café.'),
    ('Muestra', 'Porción representativa del lote para clasificación.'),
    ('Monitoreo', 'Fase de supervisión en tiempo real durante el procesamiento.'),
    ('Defecto', 'Grano con problemas: negro, brocado, fermentado.'),
    ('Rendimiento', 'Porcentaje de granos buenos respecto al total.'),
    ('EVA', 'Código único correlativo asignado a cada evaluación.'),
    ('Peso Bruto', 'Peso total del lote sin descontar tara.'),
    ('Peso Neto', 'Peso del grano después de descontar tara.'),
    ('Humedad', 'Porcentaje de agua contenida en el grano.'),
    ('Tamiz', 'Malla para clasificar granos por tamaño.'),
    ('Trillado', 'Proceso de separar grano de cáscara.'),
    ('Socio', 'Caficultor miembro oficial de la cooperativa.'),
    ('Precisión IA', 'Confianza del sistema en su clasificación.'),
    ('Rango', 'Categoría de calidad del café.'),
]

for termino, def_text in glosario:
    p = doc.add_paragraph()
    p.add_run(f'{termino}: ').bold = True
    p.add_run(def_text)

doc.add_page_break()

# ============ CIERRE ============
doc.add_heading('Conclusión', level=1)

doc.add_paragraph(
    'CoffeeRen fue diseñado para simplificar el proceso de clasificación de café '
    'desde el registro hasta el análisis final. Este manual ha cubierto todos los módulos '
    'y flujos principales que necesitas para operar el sistema efectivamente.'
)

doc.add_paragraph(
    'Recuerda que la precisión en el registro de datos es fundamental. Los datos que ingreses '
    'determinan la calidad de los análisis y el cálculo justo de pagos a los caficultores.'
)

doc.add_paragraph(
    'Si surge alguna duda o encuentras un problema, consulta primero la sección de '
    'Preguntas Frecuentes. Si el problema persiste, contacta al administrador del sistema.'
)

# Guardar
output_path = 'd:\\TesisPrj\\Manual_Usuario_CoffeeRen.docx'
doc.save(output_path)
print(f'Documento generado: {output_path}')
