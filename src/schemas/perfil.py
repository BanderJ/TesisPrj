from pydantic import BaseModel, Field, field_validator, ValidationInfo


class ActualizarDatosPersonales(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    ape_paterno: str = Field(..., min_length=1, max_length=30)
    ape_materno: str = Field(..., min_length=1, max_length=30)
    telefono: str | None = Field(None, min_length=9, max_length=9)
    correo: str | None = Field(None, max_length=100)

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not v.isdigit():
            raise ValueError("Teléfono debe contener solo dígitos")
        if len(v) != 9:
            raise ValueError("Teléfono debe tener exactamente 9 dígitos")
        return v


class CambiarContrasena(BaseModel):
    clave_actual: str = Field(..., min_length=1)
    clave_nueva: str = Field(..., min_length=8, max_length=30)
    confirmar_clave: str = Field(..., min_length=8, max_length=30)

    @field_validator("confirmar_clave")
    @classmethod
    def validar_coincidencia(cls, v: str, info: ValidationInfo) -> str:
        clave_nueva = info.data.get("clave_nueva")
        if clave_nueva and v != clave_nueva:
            raise ValueError("Las contraseñas no coinciden")
        return v


class CambiarContraseñaUsuario(BaseModel):
    clave_nueva: str = Field(..., min_length=8, max_length=30)
    confirmar_clave: str = Field(..., min_length=8, max_length=30)

    @field_validator("confirmar_clave")
    @classmethod
    def validar_coincidencia(cls, v: str, info: ValidationInfo) -> str:
        clave_nueva = info.data.get("clave_nueva")
        if clave_nueva and v != clave_nueva:
            raise ValueError("Las contraseñas no coinciden")
        return v


class CambiarEstadoUsuario(BaseModel):
    estado: str = Field(..., pattern="^[AI]$")


class ActualizarUsuario(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    ape_paterno: str = Field(..., min_length=1, max_length=30)
    ape_materno: str = Field(..., min_length=1, max_length=30)
    sexo: str = Field(..., pattern="^[MF]$")
    fecha_nacimiento: str = Field(...)
    telefono: str | None = Field(None, min_length=9, max_length=9)
    correo: str | None = Field(None, max_length=100)
    ubigeo: str | None = Field(None, pattern=r'^\d{6}$')
    tipo_personal_id: int = Field(..., ge=1, le=3)
    clave_nueva: str | None = Field(None, min_length=8, max_length=30)

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not v.isdigit():
            raise ValueError("Teléfono debe contener solo dígitos")
        if len(v) != 9:
            raise ValueError("Teléfono debe tener exactamente 9 dígitos")
        return v


class CrearUsuario(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    ape_paterno: str = Field(..., min_length=1, max_length=30)
    ape_materno: str = Field(..., min_length=1, max_length=30)
    sexo: str = Field(..., pattern="^[MF]$")
    fecha_nacimiento: str = Field(...)
    tipo_documento_id: int = Field(..., ge=1, le=3)
    num_documento: str = Field(..., min_length=8, max_length=12)
    telefono: str | None = Field(None, min_length=9, max_length=9)
    correo: str | None = Field(None, max_length=100)
    ubigeo: str | None = Field(None, pattern=r'^\d{6}$')
    tipo_personal_id: int = Field(..., ge=1, le=3)
    clave: str = Field(..., min_length=8, max_length=30)

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not v.isdigit():
            raise ValueError("Teléfono debe contener solo dígitos")
        if len(v) != 9:
            raise ValueError("Teléfono debe tener exactamente 9 dígitos")
        return v
