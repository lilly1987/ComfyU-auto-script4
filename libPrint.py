import os
import sys,subprocess, pkg_resources

required  = {'rich'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing   = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
    
#-------------------------
import time
tm=time.strftime('%Y%m%d-%H%M%S')
#-------------------------
import logging
#import logging.handlers
from rich.logging import RichHandler

# logging.basicConfig(
#     level=logging.NOTSET,
#     #format="%(message)s",
#     #datefmt="[%H:%M:%S]",
#     #handlers=[RichHandler(rich_tracebacks=True)] # 콘솔 화면에 보여줌
# )
logger = logging.getLogger("rich")
logger.setLevel(logging.NOTSET)


os.makedirs('log', exist_ok=True)

file_handler = logging.FileHandler(f'log/logger.{tm}.log', mode="a", encoding="utf-8")
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)-8s %(filename)s:%(funcName)s:%(lineno)4s %(message)s"
))
logger.addHandler(file_handler)
#-------------------------
import atexit
from rich.console import Console
#-------------------------
# 콘솔 화면용
console_screen = Console(record=True)
# console_screen.reset()
console_screen.print("\033[0m")

# 파일 기록용
os.makedirs('log', exist_ok=True)
console_log_file = open(f"log/console.{tm}.log", "a", encoding="utf-8")
console_log = Console(record=True,file=console_log_file)
# console_log.reset()
console_log.print("\033[0m")

atexit.register(console_log_file.close)  # 프로그램 종료 시 파일 자동 닫기

#-------------------------
class PrintHelper:
        
    def __init__(self, console_screen,console_log):
        self.console_screen = console_screen
        self.console_log = console_log

        self.Debug= self.Blue
        self.Info = self.Green
        self.Warn = self.Yellow
        self.Err = self.Red

        self.Value = self.Cyan
        self.Config = self.Magenta

        self._stack_offset_Color = 4
    
    def __call__(self, *args, **kwds):
        kwds.setdefault('_stack_offset', 2)
        self.console_screen.log(*args, **kwds)
        self.console_log.log(*args, **kwds)

    def exception(self,  *args, **kwds):
        self.console_screen.print_exception(*args, **kwds)
        self.console_log.print_exception(*args, **kwds)

    def Color(self, c, msg, *a, _stack_offset=3):
        self(f'[{c}]{msg}[/{c}]', *a, _stack_offset=_stack_offset)

    def Blue(self, msg, *a):
        self.Color('blue', msg, *a, _stack_offset=self._stack_offset_Color)

    def Yellow(self, msg, *a):
        self.Color('yellow', msg, *a, _stack_offset=self._stack_offset_Color)

    def Red(self, msg, *a):
        self.Color('red', msg, *a, _stack_offset=self._stack_offset_Color)

    def Green(self, msg, *a):
        self.Color('green', msg, *a, _stack_offset=self._stack_offset_Color)

    def Cyan(self, msg, *a):
        self.Color('cyan', msg, *a, _stack_offset=self._stack_offset_Color)

    def Magenta(self, msg, *a):
        self.Color('magenta', msg, *a, _stack_offset=self._stack_offset_Color)

    def White(self, msg, *a):
        self.Color('white', msg, *a, _stack_offset=self._stack_offset_Color)

print = PrintHelper(console_screen,console_log)

# print.Blue('printBlue test')
# print.Red('printRed test')  
# print.Green('printGreen test')
# print.Yellow('printYellow test') 
# print.Magenta('printMagenta test')
# print.Cyan('printCyan test')
# print.White('printWhite test')
