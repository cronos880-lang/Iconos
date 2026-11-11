import io
import struct
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from iconos.core import ConversionOptions, ConversionError, SIZES, build_ico, convert_file, validate_ico


class IconosTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.png = self.directory / 'prueba.png'
        image = Image.new('RGBA', (400, 250), (0, 0, 0, 0))
        for y in range(40, 210):
            for x in range(65, 330):
                image.putpixel((x, y), (40, 135, 225, min(255, max(0, (x - 65) * 3))))
        image.save(self.png)

    def test_seven_sizes_mixed_encoding(self):
        raw = build_ico(Image.open(self.png).convert('RGBA'))
        self.assertEqual(validate_ico(raw), SIZES)
        self.assertEqual(struct.unpack_from('<H', raw, 4)[0], 7)
        for i, expected in enumerate(SIZES):
            _, _, _, _, _, _, length, offset = struct.unpack_from('<BBBBHHII', raw, 6 + 16 * i)
            if expected == 256:
                self.assertTrue(raw[offset:offset + 8].startswith(b'\x89PNG'))
            else:
                self.assertEqual(struct.unpack_from('<I', raw, offset)[0], 40)
            self.assertGreater(length, 40)

    def test_all_fit_modes_decodable_with_pillow(self):
        for mode in ('center', 'crop', 'stretch'):
            raw = build_ico(Image.open(self.png).convert('RGBA'), ConversionOptions(mode=mode))
            with Image.open(io.BytesIO(raw)) as ico:
                self.assertEqual(ico.format, 'ICO')
                self.assertEqual(ico.ico.sizes(), set((n, n) for n in SIZES))
                for n in SIZES:
                    sub = ico.ico.getimage((n, n))
                    self.assertEqual(sub.size, (n, n))

    def test_no_overwrite(self):
        target = self.directory / 'salida.ico'
        convert_file(self.png, target)
        first = target.read_bytes()
        with self.assertRaises(ConversionError):
            convert_file(self.png, target)
        self.assertEqual(first, target.read_bytes())

    def test_invalid_sizes(self):
        with self.assertRaises(ConversionError):
            ConversionOptions(sizes=(512,)).validate()
        with self.assertRaises(ConversionError):
            ConversionOptions(sizes=()).validate()

    def test_corrupted_file(self):
        raw = build_ico(Image.open(self.png).convert('RGBA'))
        with self.assertRaises(ConversionError):
            validate_ico(raw[:-20])

    def test_jpeg_and_webp(self):
        with Image.open(self.png) as source:
            source.convert('RGB').save(self.directory / 'imagen.jpg')
            source.save(self.directory / 'imagen.webp')
        for ext in ('jpg', 'webp'):
            dst = self.directory / f'out_{ext}.ico'
            convert_file(self.directory / f'imagen.{ext}', dst)
            self.assertEqual(validate_ico(dst.read_bytes()), SIZES)


if __name__ == '__main__':
    unittest.main()
