import os, sys
# chèn thư mục libs vào front của sys.path
ROOT = os.path.dirname(os.path.dirname(__file__))
SYS_LIBS = os.path.join(ROOT, 'libs')
sys.path.insert(0, SYS_LIBS)
state = {
    'credit': 0,
    'event': '0x00',
    'address': '',
    'last_updated': None
}