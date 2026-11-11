import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw
from iconos.auto_filter import recommend_filter


class AutomaticFilterTests(unittest.TestCase):
    def test_smooth_image_prefers_bicubic(self):
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / 'smooth.png'
            img = Image.new('RGB', (400, 400))
            for y in range(400):
                for x in range(400):
                    img.putpixel((x, y), (int(x / 2), int(y / 2), 120))
            img.save(file)
            self.assertEqual(recommend_filter(file).filter_name, 'bicubic')

    def test_detailed_checker_prefers_lanczos(self):
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / 'checker.png'
            img = Image.new('RGB', (320, 320), 'white')
            draw = ImageDraw.Draw(img)
            for y in range(0, 320, 16):
                for x in range(0, 320, 16):
                    if (x//16 + y//16) % 2:
                        draw.rectangle((x, y, x+15, y+15), fill='black')
            img.save(file)
            self.assertEqual(recommend_filter(file).filter_name, 'lanczos')


if __name__ == '__main__':
    unittest.main()
