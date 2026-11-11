"""Recomendación experimental de filtro; no modifica el motor de conversión.

No pretende medir calidad perceptual absoluta: decide a partir de textura local.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter, ImageOps, ImageStat


@dataclass(frozen=True)
class FilterSuggestion:
    filter_name: str
    reason: str
    texture_score: float


def recommend_filter(path: str | Path) -> FilterSuggestion:
    """Analiza una copia a 160px y devuelve lanczos o bicubic sin guardar nada."""
    with Image.open(path) as opened:
        # Limitar imágenes que podrían consumir demasiada memoria al decodificar.
        if opened.width * opened.height > 80_000_000:
            raise ValueError('La imagen supera el tamaño máximo admitido.')
        opened.seek(0)
        small = ImageOps.exif_transpose(opened)
        small.thumbnail((160, 160), Image.Resampling.BOX)
        rgba = small.convert('RGBA')

    # Fondo neutro para evaluar también bordes transparentes, sin modificar la imagen.
    composite = Image.new('RGBA', rgba.size, (128, 128, 128, 255))
    composite.alpha_composite(rgba)
    lum = composite.convert('RGB').convert('L')
    blurred = lum.filter(ImageFilter.GaussianBlur(radius=2))
    texture = ImageStat.Stat(ImageChops.difference(lum, blurred)).mean[0]

    # Umbral orientativo, no prueba de superioridad de un filtro.
    if texture >= 7.0:
        return FilterSuggestion('lanczos', 'Contiene bordes o detalles finos; se prioriza definición.', round(texture, 2))
    return FilterSuggestion('bicubic', 'Predominan zonas suaves; se priorizan transiciones discretas.', round(texture, 2))
