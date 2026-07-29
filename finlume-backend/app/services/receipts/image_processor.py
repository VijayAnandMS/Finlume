from PIL import Image, ExifTags
import os

class ImageProcessor:
    @staticmethod
    def process_for_storage(input_path: str, output_path: str):
        try:
            with Image.open(input_path) as img:
                try:
                    for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation] == 'Orientation':
                            break
                    exif = img._getexif()
                    if exif is not None:
                        if orientation in exif:
                            if exif[orientation] == 3: img = img.rotate(180, expand=True)
                            elif exif[orientation] == 6: img = img.rotate(270, expand=True)
                            elif exif[orientation] == 8: img = img.rotate(90, expand=True)
                except Exception:
                    pass

                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                    
                img.save(output_path, 'JPEG', quality=85)
        except Exception as e:
            from .exceptions import CorruptedImageException
            raise CorruptedImageException("Failed to decode standard image headers natively.")
