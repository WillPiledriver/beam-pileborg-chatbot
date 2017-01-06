import time
from pykeyboard import PyKeyboard
k = PyKeyboard()

def pressKey(t, key=None):
	k.press_key(key)
	time.sleep(t)
	k.release_key(key)
