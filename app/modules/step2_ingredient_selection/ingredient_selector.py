from PIL import Image
from typing import Tuple


class IngredientSelector:
    def __init__(self):
        pass

    def process_click_coordinates(self,
                                  image: Image.Image,
                                  click_coords: Tuple[int, int],
                                  selection_size: int = 100) -> Image.Image:
        """
        Extract a region around the clicked coordinates.
        Input image, click coordinates and selection size 
        Returns extracted image region 
        """
        x, y = click_coords
        half_size = selection_size // 2
        
        # Compute bounding
        # Ensure box does to go outside image bounds
        left = max(0, x - half_size)
        top = max(0, y - half_size)
        right = min(image.width, x + half_size) 
        bottom = min(image.height, y + half_size)
        
        # Extract the region
        extracted = image.crop((left, top, right, bottom))
        return extracted
