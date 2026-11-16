"""Verifica la versión del CSV sin dependencias externas."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verificar():
    manifest = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8'))
    archivo = ROOT / manifest['archivo']
    digest = hashlib.sha256(archivo.read_bytes()).hexdigest()
    if digest != manifest['sha256']:
        raise ValueError('El CSV no corresponde a la versión registrada. No entrenar hasta revisar el cambio.')
    with archivo.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != manifest['columnas']:
            raise ValueError('Esquema de columnas incorrecto')
        filas = sum(1 for _ in reader)
    if filas != manifest['filas']:
        raise ValueError('Cantidad de filas incorrecta')
    return manifest


if __name__ == '__main__':
    datos = verificar()
    print(f"OK: datos {datos['version']}, {datos['filas']} filas, SHA-256 verificado")
