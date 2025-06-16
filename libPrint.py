import sys,subprocess, pkg_resources

required  = {'rich'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing   = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
    
#-------------------------
import inspect
from rich.console import Console
console = Console(record=True)
print=console.log
from rich.console import Console

console = Console(record=True)
print = console.log

def printColor(msg, c, *a, _stack_offset=2):
    print(f'[{c}]{msg}[/{c}]', *a, _stack_offset=_stack_offset)
printYellow=lambda msg,*a: printColor(msg,'yellow',*a, _stack_offset=3)
printWarn=printYellow
printRed=lambda msg,*a: printColor(msg,'red',*a, _stack_offset=3)
printErr=printRed
printGreen=lambda msg,*a: printColor(msg,'green',*a, _stack_offset=3)
printInfo=printGreen
#printWarn('tset',{'test':'test'})

# def printColor(msg, color, *args):
#     frame = inspect.stack()[1]
#     filename = frame.filename
#     lineno = frame.lineno
#     console.log(f"[{color}]{msg} [/{color}]  (line {lineno} in {filename})", *args)
#-------------------------
import time
import logging
import logging.handlers
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.NOTSET,
    format="%(message)s",
    datefmt="[%H:%M:%S]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("rich")

tm=time.strftime('%Y%m%d-%H%M%S')
file_handler = logging.FileHandler(f'logger.{tm}.log', mode="a", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(filename)s:%(funcName)s:%(lineno)4s %(message)s"
))
logger.addHandler(file_handler)
#-------------------------
#print('print test')
#console.log('console log test')
#logger.log( logging.NOTSET,'logger log test')
#logger.log( logging.DEBUG,'logger log test')
#logger.log( logging.INFO,'logger log test')
#logger.log( logging.WARN,'logger log test')
#logger.log( logging.WARNING,'logger log test')
#logger.log( logging.ERROR,'logger log test')
#logger.log( logging.CRITICAL,'logger log test')
#logger.log( logging.FATAL,'logger log test')