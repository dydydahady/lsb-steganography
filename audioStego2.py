import wave
from PIL import Image
import math


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
    cover = cover.convert('RGB')
    width, height = cover.size

    payload = wave.open(payloadfile, mode='rb')
    print(payload.getparams())
    payload_bytes = bytearray(list(payload.readframes(payload.getnframes())))

    if len(payload_bytes) > (width * height * 8):
        print("Audio payload too large.")
        return

    i = 0

    data = []

    for y in range(height):
        for x in range(width):
            
            r, g, b = cover.getpixel((x, y)) 

            if i < len(payload_bytes) * 8: 
                b = b & getBit(payload_bytes, i)
                i += 1
            else:
                b = b & 254

            data.append((r, g, b))


    encrypted = Image.new("RGB", cover.size)
    encrypted.putdata(data)
    encrypted.save(encryptedfile)


def decode(encryptedfile, decryptedfile, lsb):
    encrypted = Image.open(encryptedfile, 'r')
    encrypted = encrypted.convert('RGB')
    width, height = encrypted.size

    i = 0

    data = bytearray(math.floor(width * height / 8))

    for y in range(height):
        for x in range(width):
            r, g, b = encrypted.getpixel((x, y))
            
            setBit(data, i, b & 1)

            i+= 1

    wavfile = wave.open(decryptedfile, "w")
    wavfile.setparams((1, 2, 44100, math.floor(len(data)/4), "NONE", "not compressed"))
    wavfile.writeframesraw(data)
    wavfile.close()


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

        decode(encryptedfile, decryptedfile, lsb)

if __name__ == "__main__":
    main()