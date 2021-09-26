# From Prof slides; NOT WORKING; DEBUGGING REQUIRED

import cv2
import numpy as np

def make_bin(data):
    # Covert data to binary format as string
    if isinstance(data, str):
        return ''.join([ format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        return [ format(i, "08b") for i in data ]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported.")

def encode(image_name, payload_data):
    image = cv2.imread(image_name) # Read the image
    n_bytes = image.shape[0] * image.shape[1] * 3 // 8 # Maximum bytes to encode
    print("[*] Maximum bytes to encode: ", n_bytes)
    payload_data += "=====" # Add stopping criteria
    if len(payload_data) > n_bytes:
        raise ValueError("[!] Insufficient bytes, need bigger image or less data.")
    print("[*] Encoding data... ")

    data_index = 0
    binary_payload_data = make_bin(payload_data) # Convert data to binary
    data_len = len(binary_payload_data) # Size of data to hide
    for row in image:
        for pixel in row:
            r, g, b = make_bin(pixel) # Convert RGB values to binary format
            if data_index < data_len: # Modify the least significant bit only if ther is still data to store
                pixel[0] = int(r[:-1] + binary_payload_data[data_index], 2) # Least significant RED pixel bit
                data_index += 1
            if data_index < data_len:
                pixel[1] = int(g[:-1] + binary_payload_data[data_index], 2) # Least significant GREEN pixel bit
                data_index += 1
            if data_index < data_len:
                pixel[2] = int(b[:-1] + binary_payload_data[data_index], 2) # Least significant BLUE pixel bit
                data_index += 1
            if data_index >= data_len: # If data is encoded, just break out of the loop
                break
    
    return image

def decode(image_name):
    print("[+] Decoding...")
    # Read the image
    image = cv2.imread(image_name)
    binary_data = ""
    for row in image:
        for pixel in row:
            r, g, b = make_bin(pixel)
            binary_data += r[-1]
            binary_data += g[-1]
            binary_data += b[-1]
    # Split by 8-bits
    # print(binary_data)
    all_bytes = [ binary_data[i: i+8] for i in range(0, len(binary_data), 8) ]
    # Convert from bits to characters
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "=====":
            break
    
    return decoded_data[:-5]

def main():
    print("LSB Steganography for Image")
    image_name = input("Enter file name of cover image: ")
    payload_data = input("Enter secret text message: ")
    encode(image_name, payload_data)
    print(decode(image_name))
    

if __name__ == "__main__":
    main()