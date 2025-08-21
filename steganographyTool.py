from PIL import Image
import math

EOF = "1111111111111110"  

def file_to_binary(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
    binary_data = ''.join(format(byte, '08b') for byte in content)
    return binary_data + EOF

def binary_to_file(binary_data, output_path):
    bytes_list = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    data_bytes = bytearray([int(b, 2) for b in bytes_list])
    with open(output_path, 'wb') as f:
        f.write(data_bytes)

def resize_cover_image(cover_image_path, secret_file_path):
    img = Image.open(cover_image_path).convert('RGB')
    with open(secret_file_path, 'rb') as f:
        file_size_bits = len(f.read()) * 8 + len(EOF)  # البتات المطلوبة + EOF
    
    required_pixels = math.ceil(file_size_bits / 3)
    current_pixels = img.width * img.height
    
    if current_pixels < required_pixels:
        scale_factor = math.sqrt(required_pixels / current_pixels)
        new_width = math.ceil(img.width * scale_factor)
        new_height = math.ceil(img.height * scale_factor)
        print(f"Resizing cover image from ({img.width},{img.height}) to ({new_width},{new_height})")
        img = img.resize((new_width, new_height))
    
    return img

def encode_file_in_image(cover_image_path, secret_file_path, output_image_path):
    img = resize_cover_image(cover_image_path, secret_file_path)
    pixels = img.load()
    binary_data = file_to_binary(secret_file_path)
    
    if len(binary_data) > img.width * img.height * 3:
        raise ValueError("File too large even after resizing the cover image.")
    
    data_index = 0
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            if data_index < len(binary_data):
                r = (r & ~1) | int(binary_data[data_index])
                data_index += 1
            if data_index < len(binary_data):
                g = (g & ~1) | int(binary_data[data_index])
                data_index += 1
            if data_index < len(binary_data):
                b = (b & ~1) | int(binary_data[data_index])
                data_index += 1
            pixels[x, y] = (r, g, b)

    img.save(output_image_path)
    print(f"File hidden in {output_image_path}")
    print(f"New cover image size: {img.width}x{img.height}")

def decode_file_from_image(stego_image_path, output_file_path):
    img = Image.open(stego_image_path).convert('RGB')
    pixels = img.load()
    binary_data = ''

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)

    binary_data = binary_data.split(EOF)[0]
    binary_to_file(binary_data, output_file_path)
    print(f"Hidden file extracted to {output_file_path}")

# Example: 
if __name__ == "__main__":
    cover_image = 'Capture.PNG'
    secret_file = 'Coursera K9ZVWEOUKOH8.pdf'
    stego_image = 'stego_capture.png'
    recovered_file = 'recovered.pdf'

    encode_file_in_image(cover_image, secret_file, stego_image)
    decode_file_from_image(stego_image, recovered_file)
