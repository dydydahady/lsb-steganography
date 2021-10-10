import wave
from PIL import Image
import math
import numpy as np


def getBit(bytes, bitno):
    byte = bytes[math.floor(bitno/8)]
    mask = 1 << (bitno % 8)
    if (byte & mask) == 0:
        return 254
    else:
        return 255


def setBit(bytes, bitno, val):
    if val == 1:
        bytes[math.floor(bitno/8)] |= (0b00000001 << (bitno % 8))
    else:
        bytes[math.floor(bitno/8)] &= ~(0b00000001 << (bitno % 8))

def encode(coverfile, payloadfile, encryptedfile, lsb):
    cover = Image.open(coverfile, 'r')
    # cover = cover.convert('RGB')
    width, height = cover.size
    array = np.array(list(cover.getdata()))

    if cover.mode == 'RGB':
        n = 3
    elif cover.mode == 'RGBA':
        n = 4

    total_pixels = array.size//n

    payload = wave.open(payloadfile, mode='rb')
    print(payload.getparams())
    payload_bytes = bytearray(list(payload.readframes(payload.getnframes())))
    # payload_bytes = list(payload.readframes(payload.getnframes()))
    # payload_bits = ''.join(format(byte, '08b')[::-1] for byte in payload_bytes)
    payload_bits = ''.join([format(byte, '08b') for byte in payload_bytes])
    req_pixels = len(payload_bits)
    print(req_pixels)
    

    if req_pixels > total_pixels:
        print("Audio payload too large.")
        return

    index = 0

    data = []

    for p in range(total_pixels):
        for q in range(0,3):
            if index < req_pixels:
                array[p][q] = int(bin(array[p][q])[2:9] + payload_bits[index], 2)
                index += 1
            
    array=array.reshape(height, width, n)
    enc_img = Image.fromarray(array.astype('uint8'), cover.mode)
    enc_img.save(encryptedfile)
    print("Image Encoded Successfully")


    # encrypted = Image.new("RGB", cover.size)
    # encrypted.putdata(data)
    # encrypted.save(encryptedfile)


def decode(encryptedfile, decryptedfile, lsb, pixel):
    encrypted = Image.open(encryptedfile, 'r')
    array = np.array(list(encrypted.getdata()))
    width, height = encrypted.size

    if encrypted.mode == 'RGB':
        n = 3
    elif encrypted.mode == 'RGBA':
        n = 4

    total_pixels = array.size//n

    hidden_bits = ""
    for p in range(pixel // 3):
    # for p in range(total_pixels):
        for q in range(0,3):
            hidden_bits += (bin(array[p][q])[2:][-1])
            # print(bin(array[p][q]))
    # print(hidden_bits)


    hidden_bits = bytearray([int(hidden_bits[i:i+8],2) for i in range(0, len(hidden_bits), 8)])
    # print(hidden_bits)

    # message = []
    # message.append(byte())
    # hidden_bits = bytearray(int(hidden_bits[i : i + 8], 2) for i in range(0, len(hidden_bits), 8))

    wavfile = wave.open(decryptedfile, "wb")
    wavfile.setparams((2, 2, 16000, 80000, "NONE", "not compressed"))
    wavfile.writeframes(hidden_bits)
    wavfile.close()

    testfile = wave.open(decryptedfile, "rb")
    print(testfile.getparams())


    # data = bytearray(math.floor(width * height / 8))

    # for y in range(height):
    #     for x in range(width):
    #         r, g, b = encrypted.getpixel((x, y))
            
    #         setBit(data, i, b & 1)

    #         i+= 1

    # wavfile = wave.open(decryptedfile, "w")
    # # wavfile.setparams((1, 2, 44100, math.floor(len(data)/4), "NONE", "not compressed"))
    # wavfile.setparams((2, 2, 16000, 480000, "NONE", "not compressed"))

    # wavfile.writeframesraw(data)
    # wavfile.close()


def main():
    print("Welcome to LSB Stego")
    print("1: Encode")
    print("2: Decode")

    func = input()

    if func == '1':
        print("Enter cover image file name: ")
        coverfile = input()
        print("Enter audio payload file name: ")
        payloadfile = input()
        print("Enter encrypted image output file name: ")
        encryptedfile = input()
        print("Enter number of LSBs to use: ")
        lsb = input()

        encode(coverfile, payloadfile, encryptedfile, lsb)

    if func == '2':
        print("Enter encrypted image file name: ")
        encryptedfile = input()
        print("Enter decrypted file name: ")
        decryptedfile = input()
        print("Enter number of LSBs to use: ")
        lsb = input()
        print("Enter number of pixels")
        pixel = int(input())

        decode(encryptedfile, decryptedfile, lsb, pixel)

if __name__ == "__main__":
    main()