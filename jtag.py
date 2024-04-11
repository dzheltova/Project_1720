#!/usr/bin/env python

import subprocess
import logging
import time
import fcntl
import os

JTAG_BINARY = "/usr/bin/jtag"


class jtag:
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE' #create object for test suite

    def __init__(self):
        self.log = logging.getLogger("jtag")
        self._proc = subprocess.Popen(
            [JTAG_BINARY, "-i"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        # устанавливаем неблокирующий режим чтения, чтобы при приеме данных от процесса скрипт не зависал
        # в ожидании данных, которых больше не будет
        self._set_nonblocking()

    def _set_nonblocking(self) -> None:
        assert self._proc
        assert self._proc.stdout
        flags = fcntl.fcntl(self._proc.stdout, fcntl.F_GETFL)
        fcntl.fcntl(self._proc.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def send(self, command: str) -> None:
        assert self._proc
        assert self._proc.stdin
        data = f"{command}\n"
        # просто отправляем команду, предварительно преобразовав строчку в байты
        self._proc.stdin.write(data.encode())
        # делаем flush, чтобы данные отправились в запущенный процесс
        self._proc.stdin.flush()

    def recv(self, timeout: float = 0.5) -> tuple[bool, str]:
        assert self._proc
        assert self._proc.stdout

        # более сложная функция для чтения =)

        line = ""

        try:
            # нужно подождать, пока процесс не исполнит команду и не начнет отправлять нам данные
            # для этого устанавливаем дедлайн получения первой порции данных
            # deadline = указывает на время в будущем, когда истечет timeout
            deadline = time.time() + timeout

            # пытаемся прочитать, вдруг что уже есть. nextline будет пустой, если ничего еще нет
            nextline = self._proc.stdout.readline().decode().strip()

            # пытаемся читать, пока не получим первую порцию данных, но не дольше timeout
            while not line and time.time() < deadline:
                # в line сохраняем что прочитали
                line += nextline

                # пытаемся прочитать, вдруг что-то появилось
                nextline = self._proc.stdout.readline().decode().strip()

                # даем еще 25 миллисекунд процессу, чтобы он успел нам отправить какие-нибудь данные
                time.sleep(0.025)

            # после получения первой порции данных даем еще 250мс, чтобы прочитать оставшиеся строчки
            deadline = time.time() + 0.250
            nextline = self._proc.stdout.readline().decode().strip()
            while time.time() < deadline:
                line += nextline
                nextline = self._proc.stdout.readline().decode().strip()

        except IOError as e:
            self.log.info(f"ioerror: {e}")

        # процесс jtag отправляет ошибки с префиксом "error:", поэтому смотрим, есть ли он
        if line.startswith("error:"):
            # если есть, то первый элемент кортежа будет False
            return False, line[6:]

        # если все успешно, то первый элемент будет True
        return True, line

    # пример реализации - команда cable
    def cable(self, device: str, vid: int, pid: int) -> tuple[bool, str]:
        command = f"cable {device} vid=0x{vid:04x} pid=0x{pid:04x}"
        self.send(command)
        return self.recv()

    # пример реализации - команда bsdl
    def bsdl(self, path: str) -> tuple[bool, str]:
        command = f"bsdl path {path}"
        self.send(command)
        return self.recv(0.1)
    
    # метод класса - вызывает extest (перевод чипа в режим тестирования GPIO)
    def set_extest(self):
        command = f"instruction EXTEST"
        self.send(command)
        command = f"shift IR"
        self.send(command)
        
     # устанавливает пин в значение value
    def set_signal(self, pin, value):
        command = f"set signal {pin} out {value}"
        self.send(command)
        self.send('shift DR')

    # проверка, что устройство с заданным id поключено
    def detect_id(self, id):
        command = f"detect"
        self.send(command)
        ok, data = self.recv()
        if id in data:
            return True
        else:
            return False
        

    # отправить команду quit и дождаться завершения процесса jtag
    def quit(self) -> None:
        assert self._proc
        self.send("quit")

        # даем 1 секунду процессе на завершение после отправки команды
        try:
            x = self._proc.wait(1.0)
            self.log.debug("process exited with status %s", x)
        except Exception:
            # если процесс не завершился, то насильно убиваем его
            self._proc.kill()
            # и ждем завершения
            _ = self._proc.wait()

        self._proc = None

    
        

#if __name__ == "__main__":
#    logging.basicConfig(
#        level=logging.DEBUG,
#        format="%(asctime)s %(name)s: %(message)s",
#    )

#    jtag = jtag()

    #ok, data = jtag.cable("FT2232", 0x0403, 0x6014)
    #if not ok:
    #    jtag.log.error("failed to connect: %s", data)
    #print(data)
    #ok, data = jtag.cable("FT2232", 0x0403, 0x6014)
    #if not ok:
    #    jtag.log.error("failed to connect: %s", data)

    #ok, data = jtag.bsdl("/home/daria/bsdl")
    #if not ok:
    #    jtag.log.error("failed to load bsdl: %s", data)
    #print (data)
    #jtag.send('detect')
    #ok, data = jtag.recv()
    #print (ok, data)
    #ok = jtag.detect_id('0x4BA00477')
    #print (ok)
    #jtag.send('instruction EXTEST')
    #jtag.send('shift IR')
    #jtag.set_extest()
    #jtag.send('set signal PA5 out 1')
    #jtag.send('shift DR')
    #jtag.set_signal('PA5', 1)
    #jtag.quit()
    #jtag.flash_stm32('blink.bin')