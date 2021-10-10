# Currently working; will be used as base file program
# Preferred to use PNG file format for now

import numpy as np
from PIL import Image
from numpy.typing import _128Bit
import textract
import sys

MAX_COLOR_VALVE = 255
MAX_NUM_BIT = 8

# Support Functions
def make_image(data, resolution):
    image = Image.new("RGB", resolution) # makes a new PIL.Image object.
    image.putdata(data) # puts the "data" matrix (pixels) onto the image.
    return image

# def remove_n_least_significant_bits(value, n):
def del_n_LSB(value, n):
    value = value >> n 
    return value << n

# def get_n_least_significant_bits(value, n):
def get_n_LSB(value, n):
    value = value << MAX_NUM_BIT - n
    value = value % MAX_COLOR_VALVE
    return value >> MAX_NUM_BIT - n

# def get_n_most_significant_bits(value, n):
def get_n_MSB(value, n):
    return value >> MAX_NUM_BIT - n

def shit_n_bits_to_8(value, n):
    return value << MAX_NUM_BIT - n



# Encoder Program
def encodeDocument(src, message, dest, n_bits):
    img = Image.open(src, 'r')
    width, height = img.size
    array = np.array(list(img.getdata()))

    if img.mode == 'RGB':
        n = 3
    elif img.mode == 'RGBA':
        n = 4

    total_pixels = array.size//n

    message += b"#####"
    message = str(message, 'utf-8')
    b_message = ''.join([format(ord(i), "08b") for i in message])
    req_pixels = len(b_message)

    if req_pixels > total_pixels:
        sys.exit("ERROR: Need larger file size")
    else:
        if req_pixels % n_bits == 0:
            index = 0
            for p in range(total_pixels):
                for q in range(0,3):
                    if n_bits == 1:
                            array[p][q] = int(bin(array[p][q])[2:10-n_bits] + b_message[index] , 2) #Take bit 2 to bit 9 of image binary
                            index += n_bits
                    elif n_bits == 2:
                        array[p][q] = int(bin(array[p][q])[2:10-n_bits] + b_message[index] + b_message[index+1], 2) #Take bit 2 to bit 9 of image binary
                        index += n_bits
                    elif n_bits == 3:
                        array[p][q] = int(bin(array[p][q])[2:10 - n_bits] + b_message[index] + b_message[index + 1]+ b_message[index + 2], 2)
                        index += n_bits
                    elif n_bits == 4:
                        array[p][q] = int(
                            bin(array[p][q])[2:10 - n_bits] + b_message[index] + b_message[index + 1] + b_message[
                                index + 2]+b_message[index +3], 2)
                        index += n_bits
                    elif n_bits == 5:
                        array[p][q] = int(
                        bin(array[p][q])[2:10 - n_bits] + b_message[index] + b_message[index + 1] + b_message[
                            index + 2] + b_message[index + 3]+b_message[index +4], 2)
                        index += n_bits
                    elif n_bits == 6:
                        array[p][q] = int(
                        bin(array[p][q])[2:10 - n_bits] + b_message[index] + b_message[index + 1] + b_message[
                            index + 2] + b_message[index + 3] + b_message[index + 4] + b_message[index + 5], 2)
                        index += n_bits
                    else:
                        sys.exit("ERROR: Invalid Bit Selection")
        else:
            print("ERROR: Number of LSB not suitable for message size, pick another number.")
            print("Message size = ",req_pixels)
            print("Select LSB that is divisible by message size.")
            sys.exit()

    array=array.reshape(height, width, n)
    enc_img = Image.fromarray(array.astype('uint8'), img.mode)
    enc_img.save(dest)
    print("Image Encoded Successfully")

def encodeImage(srcPath, payImagePath, dest, n_bits):
    # get payload width and height as well as pixel count to be fed into decode, possible to set it as header info
    src = Image.open(srcPath, 'r')
    payImage = Image.open(payImagePath, 'r')

    array_src = np.array(list(src.getdata()))
    if src.mode == 'RGB':
        n = 3
    elif src.mode == 'RGBA':
        n = 4
    total_pixels_src = array_src.size//n

    array_payImage = np.array(list(payImage.getdata()))
    if payImage.mode == 'RGB':
        n = 3
    elif payImage.mode == 'RGBA':
        n = 4
    total_pixels_payImage = array_payImage.size//n

    if total_pixels_payImage > total_pixels_src:
        sys.exit("ERROR: Need larger file size")

    payImage = payImage.resize(src.size)
    
    width, height = src.size

    payload = payImage.load()
    cover = src.load()

    data = []

    for y in range(height):
        for x in range(width):

            try:
                r_payload, g_payload, b_payload= payload[x,y]
                r_payload = get_n_MSB(r_payload, n_bits)
                g_payload = get_n_MSB(g_payload, n_bits)
                b_payload = get_n_MSB(b_payload, n_bits)

                r_cover, g_cover, b_cover= cover[x,y]
                r_cover = del_n_LSB(r_cover, n_bits)
                g_cover = del_n_LSB(g_cover, n_bits)
                b_cover = del_n_LSB(b_cover, n_bits)

                data.append((r_payload + r_cover,
                             g_payload + g_cover,
                             b_payload + b_cover))
                             
            except Exception as e:
                print(e)
    
    enc_image = make_image(data, payImage.size)
    enc_image.save(dest)

    print("Image Encoding Successfull")



# Decoder Program
def decodeDocument(src, n_bits):
    img = Image.open(src, 'r')
    
    array = np.array(list(img.getdata()))
    
    if img.mode == 'RGB':
        n = 3
    elif img.mode == 'RGBA':
        n = 4

    total_pixels = array.size//n

    hidden_bits = ""
    for p in range(total_pixels):
        for q in range(0,3):
            hidden_bits += (bin(array[p][q])[2:][-n_bits:])

    hidden_bits = [hidden_bits[i:i+8] for i in range(0, len(hidden_bits), 8)]

    message = ""

    for i in range(len(hidden_bits)):
        if message[-5:] == "#####":
            break
        else:
            message += chr(int(hidden_bits[i], 2))

    if "#####" in message:
        print("Hidden Message: ", message[:-5])
    else:
        print("No hidden message found")


def decodeImage(src, n_bits, dest):
    img = Image.open(src, 'r')
    width, height = img.size
    payload = img.load()

    data = []

    for y in range(height):
        for x in range(width):

            r_payload, g_payload, b_payload = payload[x,y]

            r_payload = get_n_LSB(r_payload, n_bits)
            g_payload = get_n_LSB(g_payload, n_bits)
            b_payload = get_n_LSB(b_payload, n_bits)

            r_payload = shit_n_bits_to_8(r_payload, n_bits)
            g_payload = shit_n_bits_to_8(g_payload, n_bits)
            b_payload = shit_n_bits_to_8(b_payload, n_bits)

            data.append((r_payload, g_payload, b_payload))

    dec_image = make_image(data, img.size)
    dec_image.save(dest)

    print("Image Decoded Successfully")

    

def main():
    print("Welcome to LSB Stego")
    print("1: Encode")
    print("2: Decode")

    func = input()

    if func == '1':
        print("Enter Cover Image Path")
        src = input()
        print("File Type of Secret File: \n 1: Text Documents \n 2: Images \n 3: Audio-Visual")
        payloadType = input()
        if payloadType == '1':
            print("Enter file name: ")
            fileName = input()
            message = textract.process(fileName)
        elif payloadType == '2':
            print("Enter file name: ")
            fileName = input()
            # print("Number of LSB to use: ")
            # n_bits = int(input())
            # img = Image.open(fileName, 'r')
            # message = np.array(list(img.getdata()))
        elif payloadType == '3':
            sys.exit()
        else:
            print("Invalid Option")

        print("Number of LSB to use: ")
        n_bits = int(input())
        print("Enter Destination Path")
        dest = input()
        print("Encoding...")
        if payloadType == '1':
            encodeDocument(src, message, dest, n_bits)
        elif payloadType == '2':
            encodeImage(src, fileName, dest, n_bits)
    
    elif func == '2':
        print("Enter Source Image Path")
        src = input()
        print("Payload File Type: \n 1: Text Document \n 2: Images \n 3: Audio-Visual")
        payloadType = input()
        print("No. of bits used to encode: ")
        n_bits = int(input())
        if payloadType == '1':
            print("Decoding...")
            decodeDocument(src, n_bits)
        elif payloadType == '2':
            print("Enter Destination Path: ")
            dest = input()
            print("Decoding...")
            decodeImage(src, n_bits, dest)
        elif payloadType == '3':
            sys.exit()

    else:
        print("Invalid option")

if __name__ == "__main__":
    main()