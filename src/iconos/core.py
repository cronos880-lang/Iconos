"""Conversión de imágenes a ICO multirresolución sin dependencias de GUI."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from io import BytesIO
import os
import struct
import tempfile

from PIL import Image, ImageOps, UnidentifiedImageError

SIZES = (16, 24, 32, 48, 64, 128, 256)
EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}
MAX_PIXELS = 80_000_000
MODES = ('center', 'crop', 'stretch')


class ConversionError(Exception):
    """Error controlado de validación o procesamiento."""


@dataclass(frozen=True)
class ConversionOptions:
    mode: str = 'center'
    sizes: tuple[int, ...] = SIZES
    resample: str = 'lanczos'

    def validate(self) -> None:
        if self.mode not in MODES:
            raise ConversionError(f'Encuadre desconocido: {self.mode}')
        if self.resample not in ('lanczos', 'bicubic'):
            raise ConversionError(f'Filtro desconocido: {self.resample}')
        if not self.sizes or len(set(self.sizes)) != len(self.sizes):
            raise ConversionError('Elija resoluciones únicas y al menos una.')
        if any(x not in SIZES for x in self.sizes):
            raise ConversionError('La resolución no pertenece al perfil compatible.')


def _source_image(path: Path) -> Image.Image:
    if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
        raise ConversionError(f'Archivo de imagen no admitido: {path.name}')
    try:
        with Image.open(path) as loaded:
            if loaded.format not in ('PNG', 'JPEG', 'WEBP'):
                raise ConversionError('El contenido no coincide con un formato admitido (PNG, JPG, WebP).')
            w, h = loaded.size
            if not (w > 0 and h > 0 and w * h <= MAX_PIXELS):
                raise ConversionError(f'Dimensiones no admitidas: {w} × {h}.')
            if getattr(loaded, 'n_frames', 1) > 1:
                # V0.1.0: primer fotograma únicamente; se comunica explícitamente.
                loaded.seek(0)
            oriented = ImageOps.exif_transpose(loaded)
            return oriented.convert('RGBA')
    except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        raise ConversionError(f'No se pudo leer la imagen {path.name}: {exc}') from exc


def _resize_alpha(image: Image.Image, target: tuple[int, int], filt: int) -> Image.Image:
    """Remuestrea en alfa premultiplicado para evitar halos de RGB oculto."""
    return image.convert('RGBa').resize(target, resample=filt).convert('RGBA')


def _square(image: Image.Image, n: int, options: ConversionOptions) -> Image.Image:
    w, h = image.size
    filt = Image.Resampling.LANCZOS if options.resample == 'lanczos' else Image.Resampling.BICUBIC
    if options.mode == 'stretch':
        return _resize_alpha(image, (n, n), filt)
    if options.mode == 'center':
        factor = min(n / w, n / h)
        new_size = (max(1, min(n, round(w * factor))), max(1, min(n, round(h * factor))))
        small = _resize_alpha(image, new_size, filt)
        out = Image.new('RGBA', (n, n), (0, 0, 0, 0))
        out.paste(small, ((n - new_size[0]) // 2, (n - new_size[1]) // 2))
        return out
    # CROP: el área central cuadrada del original permite cubrir totalmente el destino.
    side = min(w, h)
    x = (w - side) // 2
    y = (h - side) // 2
    return _resize_alpha(image.crop((x, y, x + side, y + side)), (n, n), filt)


def _png_blob(image: Image.Image) -> bytes:
    data = BytesIO()
    image.save(data, format='PNG', optimize=True)
    return data.getvalue()


def _dib_blob(image: Image.Image) -> bytes:
    """DIB BGRA bottom-up + AND mask 1 bpp; cabecera biHeight = 2*alto."""
    w, h = image.size
    # Pillow BGRA raw devuelve bytes BGRA; no comprimir.
    bgra = image.tobytes('raw', 'BGRA')
    rows = b''.join(bgra[y * w * 4:(y + 1) * w * 4] for y in range(h - 1, -1, -1))
    stride = ((w + 31) // 32) * 4
    alpha = image.getchannel('A')
    mask_rows = []
    for y in range(h - 1, -1, -1):
        bits = bytearray(stride)
        for x in range(w):
            if alpha.getpixel((x, y)) == 0:
                bits[x // 8] |= 1 << (7 - (x % 8))
        mask_rows.append(bytes(bits))
    header = struct.pack('<IiiHHIIiiII', 40, w, h * 2, 1, 32, 0, len(rows), 0, 0, 0, 0)
    return header + rows + b''.join(mask_rows)


def build_ico(image: Image.Image, options: ConversionOptions = ConversionOptions()) -> bytes:
    options.validate()
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    images = []
    for size in sorted(options.sizes):
        target = _square(image, size, options)
        # PNG sólo para 256: compatibilidad alta con lectores clásicos.
        blob = _png_blob(target) if size == 256 else _dib_blob(target)
        images.append((size, blob))
    header = struct.pack('<HHH', 0, 1, len(images))
    entries = bytearray()
    data = bytearray()
    offset = 6 + 16 * len(images)
    for size, blob in images:
        encoded_size = 0 if size == 256 else size
        entries.extend(struct.pack('<BBBBHHII', encoded_size, encoded_size, 0, 0, 1, 32, len(blob), offset))
        data.extend(blob)
        offset += len(blob)
    raw = header + bytes(entries) + bytes(data)
    validate_ico(raw, expected_sizes=tuple(sorted(options.sizes)))
    return raw


def validate_ico(raw: bytes, expected_sizes: tuple[int, ...] | None = None) -> tuple[int, ...]:
    """Validador binario básico independiente de Pillow."""
    if len(raw) < 6:
        raise ConversionError('ICO incompleto.')
    reserved, kind, count = struct.unpack_from('<HHH', raw)
    if reserved != 0 or kind != 1 or not (1 <= count <= 256):
        raise ConversionError('Cabecera ICO inválida.')
    if len(raw) < 6 + 16 * count:
        raise ConversionError('Directorio ICO truncado.')
    sizes = []
    ranges = []
    for idx in range(count):
        w, h, _, _, planes, depth, length, offset = struct.unpack_from('<BBBBHHII', raw, 6 + idx * 16)
        w = w or 256
        h = h or 256
        if w != h or length < 40 or offset < 6 + count * 16 or offset + length > len(raw):
            raise ConversionError(f'Entrada ICO {idx} inválida.')
        if planes != 1 or depth != 32:
            raise ConversionError(f'Profundidad ICO {idx} no compatible con el perfil.')
        blob = raw[offset:offset + length]
        if blob.startswith(b'\x89PNG\r\n\x1a\n'):
            if len(blob) < 24 or blob[12:16] != b'IHDR':
                raise ConversionError('PNG interno inválido.')
            pw, ph = struct.unpack_from('>II', blob, 16)
            if (pw, ph) != (w, h):
                raise ConversionError('Dimensiones PNG inconsistentes.')
        else:
            if len(blob) < 40 or struct.unpack_from('<I', blob)[0] != 40:
                raise ConversionError('DIB interno inválido.')
            bw, bh = struct.unpack_from('<ii', blob, 4)
            if (bw, bh) != (w, h * 2):
                raise ConversionError('Dimensiones DIB inconsistentes.')
            needed = 40 + w * h * 4 + ((w + 31) // 32) * 4 * h
            if len(blob) != needed:
                raise ConversionError('Longitud DIB incorrecta.')
        sizes.append(w)
        ranges.append((offset, offset + length))
    for left, right in zip(sorted(ranges), sorted(ranges)[1:]):
        if left[1] > right[0]:
            raise ConversionError('Bloques ICO solapados.')
    if len(sizes) != len(set(sizes)):
        raise ConversionError('Resoluciones duplicadas.')
    if expected_sizes is not None and tuple(sizes) != tuple(expected_sizes):
        raise ConversionError('Resoluciones ICO incorrectas.')
    return tuple(sizes)


def convert_file(source: str | Path, destination: str | Path, options: ConversionOptions = ConversionOptions(), overwrite: bool = False) -> Path:
    """Guarda de forma atómica; por defecto nunca sobrescribe un archivo existente."""
    src, dst = Path(source), Path(destination)
    options.validate()
    if src.resolve() == dst.resolve():
        raise ConversionError('El destino no puede coincidir con el origen.')
    if dst.suffix.lower() != '.ico':
        raise ConversionError('El archivo de destino debe terminar en .ico.')
    if not dst.parent.is_dir():
        raise ConversionError('La carpeta de destino no existe.')
    if dst.exists() and not overwrite:
        raise ConversionError(f'Ya existe: {dst.name}. No se ha sobrescrito.')
    original = _source_image(src)
    payload = build_ico(original, options)
    tmp_name = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.tmp', prefix='.iconos_', dir=dst.parent, delete=False) as fp:
            tmp_name = fp.name
            fp.write(payload)
            fp.flush()
            os.fsync(fp.fileno())
        if dst.exists() and not overwrite:
            raise ConversionError(f'Ya existe: {dst.name}. No se ha sobrescrito.')
        # Alta seguridad: crear destino sin reemplazar, evita carreras al escribir.
        if not overwrite:
            created = False
            try:
                with open(dst, 'xb') as out:
                    created = True
                    with open(tmp_name, 'rb') as source_fp:
                        while part := source_fp.read(1024 * 1024):
                            out.write(part)
                    out.flush()
                    os.fsync(out.fileno())
            except Exception:
                if created:
                    try:
                        dst.unlink()
                    except OSError:
                        pass
                raise
        else:
            os.replace(tmp_name, dst)
            tmp_name = None
        return dst
    except FileExistsError as exc:
        raise ConversionError(f'Ya existe: {dst.name}. No se ha sobrescrito.') from exc
    except OSError as exc:
        raise ConversionError(f'Error escribiendo el destino: {exc}') from exc
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
