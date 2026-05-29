from src.database.bd import Connection

db = Connection()
try:
    sql = '''
    SELECT id, nombre, ape_paterno, ape_materno, sexo, fecha_nacimiento,
           tipo_documento_id, num_documento, telefono, ubigeo, estado
    FROM persona
    WHERE estado = 'A'
    LIMIT 5
    '''
    resultados = db.obtener(sql, ())
    print('=== PRIMERAS 5 PERSONAS ACTIVAS ===')
    for row in resultados:
        print(f"Documento: {row['num_documento']}, Nombre: {row['nombre']} {row['ape_paterno']}, Estado: {row['estado']}")

    if resultados:
        doc_test = resultados[0]['num_documento']
        print(f'\n=== BUSCANDO DOCUMENTO: {doc_test} ===')

        sql_test = '''
        SELECT id, nombre, ape_paterno, ape_materno, sexo, fecha_nacimiento,
               tipo_documento_id, num_documento, telefono, ubigeo, estado
        FROM persona
        WHERE num_documento = %s AND estado = 'A'
        LIMIT 1
        '''
        resultado = db.obtener_uno(sql_test, (doc_test,))
        print(f'Resultado encontrado: {resultado is not None}')
        if resultado:
            print(f'  - ID: {resultado["id"]}')
            print(f'  - Nombre: {resultado["nombre"]} {resultado["ape_paterno"]} {resultado["ape_materno"]}')
finally:
    db.close()
