import os
import time

# Formato UUID canonico. Unico lugar donde vive el patron: lo usan las rutas
# que reciben un id por Path y los schemas que lo reciben en el body.
UUID_PATTERN: str = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"


def uuid7() -> str:
    """Generate a UUIDv7 (RFC 9562) — time-ordered, compatible with PostgreSQL uuidv7()."""
    ts_ms = int(time.time() * 1000)
    rand = int.from_bytes(os.urandom(10), "big")

    rand_a = (rand >> 68) & 0xFFF
    rand_b = (rand >> 6) & 0x3FFFFFFFFFFFFFFF

    uuid_int = (
        (ts_ms & 0xFFFFFFFFFFFF) << 80
        | 0x7 << 76
        | rand_a << 64
        | 0b10 << 62
        | rand_b
    )

    h = f"{uuid_int:032x}"
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"
