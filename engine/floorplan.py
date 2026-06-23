"""Dado do floor-plan (o .md é prosa; este é o que a cidade lê). Valida shape."""
ANDAR_STATUS = {"cheio", "provisional", "vazio"}
DIAGNOSTICO = {"no-caminho", "girando", "pulando"}


class FloorplanError(ValueError):
    pass


def validate_floorplan(fp):
    if fp.get("diagnostico") not in DIAGNOSTICO:
        raise FloorplanError(f"diagnostico fora do fechado: {fp.get('diagnostico')!r}")
    if not isinstance(fp.get("objetivo"), str):
        raise FloorplanError("objetivo ausente")
    for a in fp.get("andares", []):
        if a.get("status") not in ANDAR_STATUS:
            raise FloorplanError(f"andar status inválido: {a.get('status')!r}")
    return fp
