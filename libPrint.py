import sys,subprocess, pkg_resources

required  = {'rich'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing   = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
    
#-------------------------
from rich.console import Console
console = Console(record=True)

print=console.log

printColor=lambda msg,c,*a:print(f'[{c}] {msg} [/{c}]',*a ) 
printYellow=lambda msg,*a: printColor(msg,'yellow',*a)
printWarn=lambda msg,*a: printYellow(msg,*a)
printRed=lambda msg,*a: printColor(msg,'red',*a)
printErr=lambda msg,*a: printRed(msg,*a)
printGreen=lambda msg,*a: printColor(msg,'green',*a)
printInfo=lambda msg,*a: printGreen(msg,*a)
#printWarn('tset',{'test':'test'})
#-------------------------
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

file_handler = logging.FileHandler('logger.log', mode="a", encoding="utf-8")
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