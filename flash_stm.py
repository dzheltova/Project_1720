import subprocess


class flash_stm:
    def flash_stm32(self, fw_name):
        command = f"program {fw_name} 0x08000000 verify reset exit"
        _proc = subprocess.Popen(
            ['openocd', '-f', 'interface/ftdi/um232h.cfg', '-c', 'transport select jtag', '-f', 'target/stm32f4x.cfg', '-c', 'init','-c', 'reset', '-c', 'halt','-c', command],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        #print(_proc.stdout.readline())
        res = ''
        for line in _proc.stdout:
            res = res + str(line, encoding='utf-8')
        if 'Verified OK' in res:
            return True
        else:
            return False