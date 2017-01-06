import time


def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def now_playing():
	try:
		f = open("np.txt", 'r')
		npp = removeNonAscii(f.read())
	except:
		return "???? shit broke d00d"
	f.close()
	return None if npp=="0" else npp

