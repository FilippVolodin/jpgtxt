from PIL import Image
from numpy import asarray, dot
import sys

def write_jpeg_header(ba, w, h):

    # write SOI
    ba += bytearray.fromhex("FF D8")

    # write DQT
    ba += bytearray.fromhex("FF DB 00 43 00"
                            "FF FF FF FF FF FF FF FF"
                            "FF FF FF FF FF FF FF FF"
                            "FF FF FF FF FF FF FF FF"
                            "FF FF FF FF FF FF FF FF"
                            "FF FF FF FF FF FF FF FF"
                            "FF FF FF FF FF FF FF FF"
                            "FF FF FF FF FF FF FF FF"
                            "FF FF FF FF FF FF FF FF")

    # write SOF0
    ba += bytearray.fromhex("FF C0 00 0B 08")
    ba += h.to_bytes(length=2, byteorder='big')
    ba += w.to_bytes(length=2, byteorder='big')
    ba += bytearray.fromhex("01 01 11 00")

    # write DHT DC
    ba += bytearray.fromhex("FF C4 00 18 00 00 00 02 02 00 01 00 00 00 00 00 00 00 00 00 00 01 03 01 02 00")

    # write DHT AC
    ba += bytearray.fromhex("FF C4 00 17 10 00 02 01 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")

    # write SOS
    ba += bytearray.fromhex("FF DA 00 08 01 01 00 00 3F 00")

def write_jpeg_stream(ba, gray_data):
    d = {-6: 0x24, -5: 0x28, -4: 0x2C, -3: 0x50, -2: 0x54, -1: 0x44,
          0: 0x60, 1: 0x4C, 2: 0x58, 3: 0x5C, 4: 0x30, 5: 0x34, 6: 0x38 }

    prev_coef = 0
    coef = 0
    for row in gray_data:

        # write LF
        ba.append(0xA)

        # previous 0xA byte decreases DC coefficient by -1
        # so we need to write compensation byte
        # alternatively we could use RST markers
        ba.append(0x4C)

        for v in row:

            coef = v // 37 - 3
            diff = coef - prev_coef
            prev_coef = coef

            ba.append(d[diff])

def write_jpeg_footer(ba):
    # write EOI
    ba += bytearray.fromhex("FFD9")

def jpgtxt(input_file, output_file):
    img = Image.open(input_file).convert('L')
    w, h = img.size
    cols, rows = (w//8, h//8)
    img = img.resize((cols, rows))
    data = asarray(img)

    ba = bytearray()
    write_jpeg_header(ba, (cols + 2) * 8, rows * 8)
    write_jpeg_stream(ba, data)
    write_jpeg_footer(ba)
    with open(output_file, 'wb') as f:
        f.write(ba)

if __name__== "__main__":
    jpgtxt(sys.argv[1], sys.argv[2])
