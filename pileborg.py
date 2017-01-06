from chatty import create
import config, time
import functions as fun
from bot import bot as b
from tornado.ioloop import PeriodicCallback, IOLoop

def nowplaying():
	global np, t, tprev, npprev
	np = fun.now_playing()
	t = time.time()
	if(t-tprev)>15.0:
		if np:
			if not np == npprev:
				chat.message("Now Playing: " + fun.removeNonAscii(np))
				npprev = np
		tprev = time.time()
		
def addmoney():
	global chat, ph
	users = chat.get_users()
	
	##ADD MONEY
	ph.add_money_to_users(users)
	
def sendchat():
	global chats, chat
	if len(chats) == 0: 
		chats = config.CHATMESSAGES[:]
	chat.message(chats.pop(0))


if __name__ == "__main__":
	tprev = time.time()
	npprev = fun.now_playing()
	chats = config.CHATMESSAGES[:]
	print(npprev)
	
	chat = create(config)
	ph = b(chat)

	# Tell chat to authenticate with the beam server. It'll throw
	# a chatty.errors.NotAuthenticatedError if it fails.
	chat.authenticate(config.CHANNEL)

	# Listen for incoming messages.
	chat.on("message", ph.filtermessage)
	
	# Send Now playing to chat when song changes
	PeriodicCallback(
		lambda: nowplaying(),
		1000
	).start()
	
	
	# Add money to viewers after user defined seconds
	PeriodicCallback(
		lambda: addmoney(),
		ph.moneyupdate * 1000
	).start()
	
	# Send predetermined chat messages
	if (config.CHATTIMER > 0) and (len(config.CHATMESSAGES) > 0):
		PeriodicCallback(
			lambda: sendchat(),
			config.CHATTIMER * 1000
		).start()

# Start the tornado event loop.
	IOLoop.instance().start()
