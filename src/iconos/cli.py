"""Interfaz de línea de comandos; llama al mismo Core que la GUI."""
import argparse
from pathlib import Path
import sys
from .core import ConversionError, ConversionOptions, SIZES, EXTENSIONS, convert_file


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog='iconos', description='Iconos V0.1.0 - conversión ICO multirresolución')
    parser.add_argument('sources', nargs='+', type=Path, help='Imágenes PNG, JPG, WebP')
    parser.add_argument('-d', '--destino', type=Path, required=True, help='Carpeta de salida existente')
    parser.add_argument('--modo', choices=('center', 'crop', 'stretch'), default='center')
    parser.add_argument('--filtro', choices=('lanczos', 'bicubic'), default='lanczos')
    parser.add_argument('--resoluciones', default=','.join(map(str, SIZES)), help='Ejemplo: 16,32,48,256')
    args = parser.parse_args(argv)
    try:
        sizes = tuple(int(s.strip()) for s in args.resoluciones.split(','))
        options = ConversionOptions(mode=args.modo, sizes=sizes, resample=args.filtro)
        options.validate()
    except (ValueError, ConversionError) as exc:
        parser.error(str(exc))
    if not args.destino.is_dir():
        parser.error('La carpeta de destino no existe.')
    failures = 0
    for src in args.sources:
        try:
            if src.suffix.lower() not in EXTENSIONS:
                raise ConversionError('Formato no admitido')
            dst = args.destino / (src.stem + '.ico')
            convert_file(src, dst, options)
            print(f'OK: {src} -> {dst}')
        except (ConversionError, OSError) as exc:
            failures += 1
            print(f'ERROR: {src}: {exc}', file=sys.stderr)
    return 1 if failures else 0

if __name__ == '__main__':
    raise SystemExit(main())
