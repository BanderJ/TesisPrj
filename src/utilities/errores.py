class NoEncontradoError(ValueError):
    """El registro pedido no existe. Las rutas lo responden con 404; el resto de
    los ValueError de los services son reglas de negocio y se responden con 400."""
