from PIL import Image
from numpy import asarray, dot
import sys

def write_jpeg_header(ba, w, h):
    SOI = "FF D8"
    DQT = """FF DB 00 43 00
             FF 20 20 20 20 20 20 20
             20 20 20 20 20 20 20 20
             20 20 20 20 20 20 20 20
             20 20 20 20 20 20 20 20
             20 20 20 20 20 20 20 20
             20 20 20 20 20 20 20 20
             20 20 20 20 20 20 20 20
             20 20 20 20 20 20 20 20"""
    SOF0_START = "FF C0 00 0B 08"
    SOF0_OTHER = "01 01 11 00"
    DHT_DC = "FF C4 00 18 00 00 00 02 02 00 01 00 00 00 00 00 00 00 00 00 00 01 03 01 02 00"
    DHT_AC = "FF C4 00 17 10 00 02 01 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
    SOS = "FF DA 00 08 01 01 00 00 3F 00"
    
    ba += bytearray.fromhex(SOI)
    ba += bytearray.fromhex(DQT)
    ba += bytearray.fromhex(SOF0_START)
    ba += h.to_bytes(length=2, byteorder='big') + w.to_bytes(length=2, byteorder='big')
    ba += bytearray.fromhex(SOF0_OTHER)
    ba += bytearray.fromhex(DHT_DC)
    ba += bytearray.fromhex(DHT_AC)
    ba += bytearray.fromhex(SOS)

def write_jpeg_stream(ba, gray_data):
    D = {-7: 0x21, -6: 0x24, -5: 0x28, -4: 0x2C, -3: 0x50, -2: 0x54, -1: 0x44,
          0: 0x60, 1: 0x4C, 2: 0x58, 3: 0x5C, 4: 0x30, 5: 0x34, 6: 0x38, 7: 0x3C }

    LF = 0xA
    COMPENSATION = 0x4C
    QCOEF = 32
    OFFSET = 3

    prev_coef = 0
    coef = 0
    for row in gray_data:

        ba.append(LF)

        # previous 0xA byte decreases DC coefficient by -1
        # so we need to write compensation byte
        # alternatively we could use RST markers
        ba.append(COMPENSATION)

        for v in row:
            coef = v // QCOEF - OFFSET
            diff = coef - prev_coef
            prev_coef = coef

            ba.append(D[diff])

def write_jpeg_footer(ba):
    EOI = "FF D9"
    ba += bytearray.fromhex(EOI)

def jpgtxt(input_file, output_file):
    NUM_EXTRA_COLUMNS = 2
    BLOCK_SIZE = 8

    img = Image.open(input_file).convert('L')
    w, h = img.size
    cols, rows = (w//BLOCK_SIZE, h//BLOCK_SIZE)
    img = img.resize((cols, rows))
    data = asarray(img)

    ba = bytearray()
   
    write_jpeg_header(ba, (cols + NUM_EXTRA_COLUMNS) * BLOCK_SIZE, rows * BLOCK_SIZE)
    write_jpeg_stream(ba, data)
    write_jpeg_footer(ba)
    with open(output_file, 'wb') as f:
        f.write(ba)

if __name__== "__main__":
    jpgtxt(sys.argv[1], sys.argv[2])
