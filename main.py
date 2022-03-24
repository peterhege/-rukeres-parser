import sys

from lib.arukereso_parser import parse

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else input('Árukereső lista url: ')
    parse(url)
