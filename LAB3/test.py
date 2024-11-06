from PIL import Image
import os
import matplotlib.pyplot as plt

def split_image(image_path, rows, cols):
    # Wczytanie obrazu
    image = Image.open(image_path)
    width, height = image.size

    # Obliczanie szerokości i wysokości fragmentów
    tile_width = width // cols
    tile_height = height // rows

    # Tworzenie folderu na zapisywane fragmenty
    output_dir = 'image_tiles'
    os.makedirs(output_dir, exist_ok=True)

    # Lista do przechowywania fragmentów
    tiles = []

    # Dzielenie obrazu na fragmenty
    for i in range(rows):
        for j in range(cols):
            # Wyznaczanie współrzędnych fragmentu
            left = j * tile_width
            upper = i * tile_height
            right = (j + 1) * tile_width
            lower = (i + 1) * tile_height

            # Wyodrębnienie fragmentu
            tile = image.crop((left, upper, right, lower))
            tiles.append(tile)

            # Zapisywanie fragmentu jako osobny plik
            tile.save(f'{output_dir}/tile_{i}_{j}.jpg')

    return tiles

image_path = "strus.jpg"
rows, cols = 3,3

tiles = split_image(image_path, rows, cols)

plt.figure(figsize=(10, 10))
for index, tile in enumerate(tiles):
    plt.subplot(rows, cols, index + 1)
    plt.imshow(tile)  # PIL obrazy mogą być bezpośrednio wyświetlane przez matplotlib
    plt.axis('off')
plt.tight_layout()
plt.savefig("image_tiles_grid.png") 