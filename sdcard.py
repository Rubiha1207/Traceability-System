from micropython import const
import time

_CMD_TIMEOUT = const(100)
_R1_IDLE_STATE = const(1 << 0)
_TOKEN_START_BLOCK = const(0xFE)
_TOKEN_DATA_ACCEPTED = const(0x05)

class SDCard:
    def __init__(self, spi, cs, baudrate=13000000):
        self.spi = spi
        self.cs = cs
        self.cmdbuf = bytearray(6)
        self.dummybuf = bytearray(512)
        self.tokenbuf = bytearray(1)
        for i in range(512):
            self.dummybuf[i] = 0xFF
        self.dummybuf_mv = memoryview(self.dummybuf)

        self.cs.init(self.cs.OUT, value=1)
        self.init_card(baudrate)

    def init_card(self, baudrate):
        self.spi.init(baudrate=100000)

        for _ in range(16):
            self.spi.write(b"\xff")

        for _ in range(_CMD_TIMEOUT):
            if self.cmd(0, 0, 0x95) == _R1_IDLE_STATE:
                break
        else:
            raise OSError("no SD card encountered")

        r = self.cmd(8, 0x000001AA, 0x87, 4)
        if r == _R1_IDLE_STATE:
            self.init_card_v2()
        else:
            raise OSError("could not determine SD card version")

        self.spi.init(baudrate=baudrate)

    def init_card_v2(self):
        for _ in range(_CMD_TIMEOUT):
            time.sleep_ms(50)
            self.cmd(55, 0, 0)
            if self.cmd(41, 0x40000000, 0) == 0:
                self.cmd(58, 0, 0, 4)
                return
        raise OSError("timeout waiting for v2 card")

    def cmd(self, cmd, arg, crc, final=0):
        self.cs(0)
        buf = self.cmdbuf
        buf[0] = 0x40 | cmd
        buf[1] = arg >> 24
        buf[2] = arg >> 16
        buf[3] = arg >> 8
        buf[4] = arg
        buf[5] = crc
        self.spi.write(buf)

        for _ in range(_CMD_TIMEOUT):
            self.spi.readinto(self.tokenbuf, 0xFF)
            if not (self.tokenbuf[0] & 0x80):
                if final:
                    self.spi.readinto(self.dummybuf_mv[:final], 0xFF)
                self.cs(1)
                self.spi.write(b"\xff")
                return self.tokenbuf[0]

        self.cs(1)
        self.spi.write(b"\xff")
        return -1

    def readblocks(self, block_num, buf):
        nblocks = len(buf) // 512
        assert nblocks > 0, "Buffer size must be multiple of 512 bytes"

        if nblocks == 1:
            if self.cmd(17, block_num, 0) != 0:
                return -1
            self.read_into(buf)
        else:
            if self.cmd(18, block_num, 0) != 0:
                return -1
            offset = 0
            while nblocks > 0:
                self.read_into(memoryview(buf)[offset : offset + 512])
                offset += 512
                nblocks -= 1
            self.cmd(12, 0, 0)
        return 0

    def read_into(self, buf):
        self.cs(0)
        for _ in range(_CMD_TIMEOUT):
            self.spi.readinto(self.tokenbuf, 0xFF)
            if self.tokenbuf[0] == _TOKEN_START_BLOCK:
                break
        else:
            self.cs(1)
            raise OSError("timeout waiting for response")

        self.spi.readinto(buf, 0xFF)
        self.spi.readinto(self.tokenbuf, 0xFF)
        self.spi.readinto(self.tokenbuf, 0xFF)
        self.cs(1)

    def writeblocks(self, block_num, buf):
        nblocks = len(buf) // 512
        assert nblocks > 0, "Buffer size must be multiple of 512 bytes"

        if nblocks == 1:
            if self.cmd(24, block_num, 0) != 0:
                return -1
            self.write(self.tokenbuf, _TOKEN_START_BLOCK, buf)
        else:
            if self.cmd(25, block_num, 0) != 0:
                return -1
            offset = 0
            while nblocks > 0:
                self.write(self.tokenbuf, 0xFC, memoryview(buf)[offset : offset + 512])
                offset += 512
                nblocks -= 1
            self.write_token(0xFD)
        return 0

    def write(self, tokenbuf, token, buf):
        self.cs(0)
        tokenbuf[0] = token
        self.spi.write(tokenbuf)
        self.spi.write(buf)
        tokenbuf[0] = 0xFF
        self.spi.write(tokenbuf)
        self.spi.write(tokenbuf)
        self.spi.readinto(tokenbuf, 0xFF)
        if (tokenbuf[0] & 0x1F) != _TOKEN_DATA_ACCEPTED:
            self.cs(1)
            return -1
        while True:
            self.spi.readinto(tokenbuf, 0xFF)
            if tokenbuf[0] != 0:
                break
        self.cs(1)

    def write_token(self, token):
        self.cs(0)
        self.tokenbuf[0] = token
        self.spi.write(self.tokenbuf)
        self.cs(1)

    def ioctl(self, op, arg):
        if op == 4:
            return 0
        if op == 5:
            return 512
        return 0