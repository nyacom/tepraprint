#!/bin/env python3
import io

import usb.core
import usb.util

from enum import Enum
from PIL import Image

## Bus 001 Device 005: ID 0d8a:0103 King Jim Co., Ltd SR920

DRY = False   # True: Dry run, False: Real print
DEBUG = True  # True: Debug mode, False: Normal mode

# ユニット単位 --> 1mm変換
UNIT_MM = 14.173  # 360 / 25.4

#------------------------------------------------------------
class Tape_cut_mode(Enum):
    # テープカットモードコマンド
    NONE = b'\x1b\x7b\x07\x43\x00\x00\x00\x00\x43\x7d'         # カットしない
    CUT = b'\x1b\x7b\x07\x43\x03\x01\x01\x01\x49\x7d'          # カットする
    HALF_CUT = b'\x1b\x7b\x07\x43\x02\x02\x01\x01\x49\x7d'     # カット + ハーフカット
    JOB_CUT = b'\x1b\x7b\x07\x43\x03\x00\x01\x01\x49\x7d'      # ジョブごとにカット
    JOB_HALF_CUT = b'\x1b\x7b\x07\x43\x02\x00\x01\x01\x49\x7d' # ジョブごとにカット + ハーフカット

class PyTepra:
    def __init__(self, idVendor=0x0d8a, idProduct=0x0103):
        self.idVendor = idVendor
        self.idProduct = idProduct
        self.dev = None

        self.tape_width_mm = 12      # Default tape width
        self.print_start_margin = 2  # Default print start margin
        self.print_contrast = 0      # Default print contrast level (-3 to 3)
        self.print_length = 0        # Default print length (0 = auto)
        self.tape_cut_mode = Tape_cut_mode.CUT  # Default tape cut mode
        self.print_dither = True     # Default dithering method

    def connect(self):
        # Connect to the USB device

        # Find the USB device
        self.dev = usb.core.find(idVendor=self.idVendor, idProduct=self.idProduct)
        if self.dev is None:
            raise ValueError("Device not found")

        # Detach kernel driver if necessary
        if self.dev.is_kernel_driver_active(0):
            try:
                self.dev.detach_kernel_driver(0)
            except usb.core.USBError as e:
                raise ValueError("Could not detach kernel driver: {}".format(e))

        self.dev.set_configuration()  # Set the configuration for the device

        self.cfg = self.dev.get_active_configuration()
        self.intf = self.cfg[(0, 0)]

        # find the endpoints
        self.ep_in = usb.util.find_descriptor(
            self.intf.endpoints(),
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
        )

        self.ep_out = usb.util.find_descriptor(
            self.intf.endpoints(),
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
        )

        if self.ep_in is None or self.ep_out is None:
            raise ValueError("Could not find IN or OUT endpoints.")

        #if DEBUG:
        #    print('INFO', self.ep_in)
        #    print('INFO', self.ep_out)

    def disconnect(self):
        if self.dev is not None:
            usb.util.dispose_resources(self.dev)
            self.dev = None

    def send_data(self, data: bytes):
        if self.dev is None:
            raise ValueError("Device not connected")

        if DEBUG:
            print("DEBUG: DATA:", data.hex())

        if DRY:
            return

        self.ep_out.write(data)

    def get_device_id(self) -> str:
        if self.dev is None:
            raise ValueError("Device not connected")

        # send GET_DEVICE_ID request
        device_id = self.dev.ctrl_transfer(
            bmRequestType=0xa1,
            bRequest=0x00,
            wValue=0x00,
            wIndex=0x00,
            data_or_wLength=0x400
        )

        # print("DEBUG: Device ID received:", device_id)
        return device_id.tobytes().decode('utf-8')

    def get_port_status(self) -> bytes:
        if self.dev is None:
            raise ValueError("Device not connected")

        # send GET_PORT_STATUS request
        status = self.dev.ctrl_transfer(
            bmRequestType=0xc1,
            bRequest=0x01,
            wValue=0x00,
            wIndex=0x00,
            data_or_wLength=0x08
        )

        # print("DEBUG: Port status received:", status)
        return status

    def cmd_tape_feed(self):
        # テープフィードコマンド (0x1b 0x7b 0x04 0x2b)
        self.send_data(b'\x1b\x7b\x04\x2b\x00\x2b\x7d')

    def cmd_tape_cut(self):
        # テープカットコマンド (0x1b 0x7b 0x04 0x2c)
        self.send_data(b'\x1b\x7b\x04\x2b\x01\x2c\x7d')

    def cmd_contrast(self):
        # 印刷濃度指定 (0x1b 0x7b 0x04 0x44)
        if -3 <= self.print_contrast <= 3:
            self.send_data(self.__cmd_validate(b'\x1b\x7b\x04\x44' + bytes([self.print_contrast + 3])))
        else:
            raise ValueError("Invalid contrast level. Must be between -3 and 3.")

    def cmd_tape_cut_mode(self):
        # テープカットモードの指定 (0x1b 0x7b 0x04 0x43)
        self.send_data(self.tape_cut_mode.value)

    def cmd_print_offset(self):
        # 印刷開始位置オフセットの指定 (0x1b 0x7b 0x05 0x54)
        offset = int(self.print_start_margin * UNIT_MM)
        self.send_data(self.__cmd_validate(b'\x1b\x7b\x05\x54' + offset.to_bytes(2, 'little')))

    def cmd_print_length(self):
        # 印刷データ長指定 (0x1b 0x7b 0x04 0x4c)
        length = int(self.print_length * UNIT_MM)
        self.send_data(self.__cmd_validate(b'\x1b\x7b\x07\x4c' + length.to_bytes(2, 'little') + b'\x00\x00'))

    def __cmd_validate(self, cmd: bytes) -> bytes:
        # コマンドのチェックサムを計算し、コマンドを閉じる
        if len(cmd) < 4:
            raise ValueError("Command must be at least 4 bytes long.")
        
        # Calculate checksum and close command
        checksum = sum(cmd[3:])

        return cmd + bytes([checksum & 0xff, 0x7d])

    def cmd_print_graphic(self, data: bytes):
        data_bits = self.tape_width_mm * 0x0c
        data_bytes = data_bits // 8

        if len(data) % data_bytes != 0:
            raise ValueError("Data length must be a multiple of data bytes.")

        for i in range(0, len(data), data_bytes):
            chunk = data[i:i + data_bytes]
            self.send_data(b'\x1b\x2e\x00\x0a\x0a\x01' + data_bits.to_bytes(1, 'little') + b'\x00' + chunk)

        self.send_data(b'\x0c') # FIXME: なんかデータ終端に0x0cを送信する必要があるらしい。

    def fit_image_to_tape(self, imgdata: bytes) -> tuple:
        # 画像ファイルを読み込みテープの幅にフィットさせ、img, height, widthを返す

        # 画像ファイルをバイトデータから読み込む
        img = Image.open(io.BytesIO(imgdata))

        # 画像をテープの幅にフィットさせる
        tape_height_pixels = int(self.tape_width_mm * 0x0c)

        resize_width = int(img.width * tape_height_pixels / img.height)
        resize_height = tape_height_pixels

        img = img.resize((resize_width, resize_height))

        return img, resize_height, resize_width

    def image2byte(self, img: Image) -> bytes:
        # 画像を1ビットのモノクロに変換し、ビット列をバイト列に変換する

        # 画像を1ビットのモノクロに変換
        if self.print_dither:
            img = img.convert('1', dither=Image.FLOYDSTEINBERG)
        else:
            img = img.convert('1', dither=Image.NONE)

        # 画像の座標をテープの向きに合わせて回転
        img = img.rotate(270, expand=True)

        if DEBUG:
            # img.show()
            img.save("/tmp/libpytepra-debug.png")

        # 画像データのピクセルデータをビット列として取得する
        bit_data = []
        for pixel in img.getdata():
            bit_data.append(0 if pixel == 255 else 1)

        # 4ビットごとにまとめて1バイトに変換する
        byte_data = bytearray()
        for i in range(0, len(bit_data), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bit_data):
                    byte |= (bit_data[i + j] << (7 - j))
            byte_data.append(byte)

        return byte_data

    def cmd_terminate(self):
        self.send_data(b'\x1b\x7b\x03\x40\x40\x7d')

    def print_graphic(self, data: bytes, copies: int = 1):
        # 印刷処理を実行する

        # テープカットモード指定
        self.cmd_tape_cut_mode()

        # 印刷濃度指定
        self.cmd_contrast()

        # 用途不明コマンド (印刷の全体設定を終了するコマンド？)
        self.send_data(b'\x1b\x7b\x03\x47\x47\x7d')

        # 印刷部数(ラベル数分)ループ
        for _ in range(copies):
            # 印刷長指定
            self.cmd_print_length()

            # 印刷開始位置オフセットの指定(mm)
            self.cmd_print_offset()

            # 印刷データ送信
            self.cmd_print_graphic(data)

            # コマンド終了
            self.cmd_terminate()

    def get_tape_width_mm(self):
        # テプラ本体に装着されているテープの幅を取得する
        status = self.get_port_status()
        tape_width = {
            0x00: 0,   # 装着されていない
            0x01: 6,   # 6mm
            0x02: 9,   # 9mm
            0x03: 12,  # 12mm
            0x04: 18,  # 18mm
            0x05: 24,  # 24mm
            0x06: 36,  # 36mm
            0x07: 48,  # 48mm
            0x0B: 4,   # 4mm
            0x21: 50,  # 50mm
            0x23: 100, # 100mm
            0xff: 255, # 不明
        }

        return tape_width.get(status[3], 0)
