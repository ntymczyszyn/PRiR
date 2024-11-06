import os
import numpy as np
from PIL import Image
from multiprocessing import Pool

def replicate_edges(image_array):
    height, width = image_array.shape
    replicated_image = np.zeros((height + 2, width + 2), dtype=image_array.dtype)

    # Środek
    replicated_image[1:-1, 1:-1] = image_array  

    # Górna i dolna krawędź
    replicated_image[0, 1:-1] = image_array[0, :]
    replicated_image[-1, 1:-1] = image_array[-1, :]

    # Lewa i prawa krawędź
    replicated_image[1:-1, 0] = image_array[:, 0]
    replicated_image[1:-1, -1] = image_array[:, -1]

    # Rogi
    replicated_image[0, 0] = image_array[0, 0]
    replicated_image[0, -1] = image_array[0, -1]
    replicated_image[-1, 0] = image_array[-1, 0]
    replicated_image[-1, -1] = image_array[-1, -1]

    return replicated_image

def edge_filter(image):
    sobel_x = np.array([[-1, 0, 1],
                         [-2, 0, 2],
                         [-1, 0, 1]])

    sobel_y = np.array([[1, 2, 1],
                         [0, 0, 0],
                         [-1, -2, -1]])

    image_array = np.array(image)
    height, width = image_array.shape
    output_x = np.zeros_like(image_array, dtype=float)
    output_y = np.zeros_like(image_array, dtype=float)

    padded_image = replicate_edges(image_array)

    for i in range(height):
        for j in range(width):
            region = padded_image[i:i+3, j:j+3]
            
            output_x[i, j] = np.sum(sobel_x * region)
            output_y[i, j] = np.sum(sobel_y * region)

    gradient = np.sqrt(output_x**2 + output_y**2)

    # normalizacja do 0-255
    gradient = np.clip(gradient, 0, 255).astype(np.uint8)

    output_image = Image.fromarray(gradient)

    return output_image

def determine_split_type(n_clients): # możaby też na takie pionowe paski po prostu podzielić
    if n_clients < 1:
        return 1, 1

    rows = int(np.sqrt(n_clients))
    cols = n_clients // rows

    if rows * cols != n_clients:
        return 1, n_clients
    
    return rows, cols

def split_image(image, n_clients):
    rows, cols = determine_split_type(n_clients)
    width, height = image.size
    fragment_width = width // cols
    fragment_height = height // rows
    fragments = []
    coords = []
    output_dir = 'image_fragments'
    os.makedirs(output_dir, exist_ok=True)

    for i in range(rows):
        for j in range(cols):
            left = j * fragment_width
            top = i * fragment_height
            right = (j + 1) * fragment_width
            down = (i + 1) * fragment_height
            fragment = image.crop((left, top, right, down))
            fragments.append(fragment)
            coords.append((left, top, right, down))
            fragment.save(f'{output_dir}/fragment_{i}_{j}.jpg')
    
    return fragments, coords

def merge_image(fragments, coords, image_size):
    output_image = Image.new("L", image_size)

    for fragment, (left, top, right, down) in zip(fragments, coords):
        output_image.paste(fragment, (left, top, right, down))
    
    return output_image

def process_image(image_path, n_clients):
    image = Image.open(image_path).convert("L")  # obraz w skali szarosci
    fragments, coords = split_image(image, n_clients)
    
    with Pool(n_clients) as pool:
        processed_fragments = pool.map(edge_filter, fragments)
    
    output_image = merge_image(processed_fragments, coords, image.size)

    return output_image


if __name__ == "__main__":
    image1 = "strus.jpg"
    image2 = "Leopard-1.jpg"
    num = 4

    output_image = process_image(image2, n_clients=num)
    output_image.save(f'2result_{image2}')
        
