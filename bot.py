import re, socket, time, json, math, config, inputsim, datetime, threading, espeak
import functions as fun
from commands import commands
from pykeyboard import PyKeyboard

class bot():
	def __init__(self, chathandle=None):
		
		self.k = PyKeyboard()
		self.es = espeak.ESpeak(speed= 100, word_gap = 5, pitch = 25, amplitude=200)
		self.moneyname = config.MONEYNAME
		self.moneystep = config.MONEYSTEP
		self.moneyupdate = config.MONEYUPDATE
		self.read_userdata()
		
		
		self.chat = chathandle
		com = commands(chathandle)
		
		# self.options is a dict with keys being all available commands and
		# the value being the def to call when command is received
		
		self.options = {"!markov": com.markov, "!d20" : com.d20, ("!" + self.moneyname): self.tellmoney, "!8ball": com.eightball, "!skipsong": self.skipsong,
		"!suggest": com.suggest, "!time":self.telltime, "!urban": com.urban, "!tts": self.text2speech,
		"!commands": self.sendcommands, "!testmod": self.testmod}
		
		# self.cooldowns is a list of tuples with the keys being the name of the command and the tuple being (cooldown, lasttimeactivated)
		self.cooldowns = {"!tts": (30, time.time()),
						"!skipsong": (30, 0),
						"!markov": (5, 0)}
						
		# self.modcommands is an array of commands that only mods can use
		self.modcommands = ["!testmod"]
		
		# populate self.legal with the keys from self.options	
		self.legal = []
		for s in self.options.keys(): self.legal.append(s)
			
		# self.iterated is an array of commands that can be entered like <command>x5 or x4 ... x2.
		self.iterated = []
		
		# self.sendercommands is an array of commands that need a sender to be passed
		self.sendercommands = [("!" + self.moneyname), "!skipsong", "!tts", "!commands", "!testmod"]
		
		# self.immediate is an array of commands the bot will always act on immediately
		self.immediate = ["!markov", "!d20", "!8ball", "!joke", "!commands", "!testmod"]
		
		# self.argumented is an array of commands that have one or more arguments
		self.argumented = ["!suggest", "!time", "!urban", "!tts"]
		
		for s in self.sendercommands: self.immediate.append(s)
		for s in self.argumented: self.immediate.append(s)
		

		
		
		for it in self.iterated:
			for i in range(2, 6):
				self.legal.append(it + "x" + str(i))		
	
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-TEXT PARSING AND COMMAND STUFF=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-##


	def send_message(self, msg, user=None, whisper=False):
		if(self.chat):
			if whisper == False:
				self.chat.message(msg)
			else:
				self.send_whisper(user, msg)

	def send_whisper(self, user, msg):
		if(self.chat):
			self.chat.whisper(user, msg)
			
	def parse_message(self, sender, msg, whisper=False):
		if len(msg) >= 1:
			s = msg.split(" ")[0].lower()
			if s in self.legal:
				
				# if cooldowns have been activated on this command
				if s in self.cooldowns:
					t = time.time()
					cooldown = self.cooldowns[s]
					if t-cooldown[1] > cooldown[0]:
						self.cooldowns[s] = (cooldown[0], time.time())
					else:
						self.send_whisper(sender, "There is a {} second cooldown on using {}. {} seconds left in the cooldown.".format(cooldown[0], s, int(cooldown[0] - (t-cooldown[1]))))
						return
						
				# if the command is a mod only command, check if sender has permission		
				isMod = False
				if s in self.modcommands:
					for acceptedroles in ["Mod", "Owner"]:
						if acceptedroles in self.userdata[sender.lower()]["userRoles"]:
							isMod = True
							break
					if not isMod:
						print("{} tried to use command {} without correct permissions.".format(sender, s))
						return
							
				# if command should be processed immediately
				if s in self.immediate:
					itsplit = s.split("x")
					
					
					if itsplit[0] in self.iterated:
						## If command can be iterated
						
						
						if len(itsplit)>1:
							it = int(itsplit[1])
							for i in range(0,it):
								self.options[itsplit[0]]()
						else:
							self.options[s]()
					
					# if the command is argumented
					elif s in self.argumented:
						# if the command is argumented and uses money
						if s in self.sendercommands:
							self.options[s](sender, msg[len(s):].lstrip())
						else:
							self.options[s](sender, msg[len(s):].lstrip())
					
					# if the command is only a command with money functions (only need to know the sender)
					elif(s in self.sendercommands):
						if whisper:
							self.options[s](sender, whisper=whisper)
						else:
							self.options[s](sender)
					
					# No arguments to be passed to function
					else:
						self.options[s]()
						
				# If command should be added to the queue [This function may be added later]
				else:
					print("Not sure what to do with command {}. Make sure it's added to self.immediate or another".format(s))
					
	def filtermessage(self, packet):
		if "data" in packet:
			data = packet["data"]
		# other packets

		if "type" in packet:
		
			# if there's an event
			if packet["type"] == "event":
				if "event" in packet:
					event = packet["event"]
					# If Chat Message is received
					if event == "ChatMessage":
						if "message" in data:
							# Whisper
							if("meta" in data["message"]) and ("whisper" in data["message"]["meta"]):
								if data["message"]["meta"]["whisper"]:
									text = data["message"]["message"][0]["data"]
									sender = data["user_name"]
									print("Whisper from {}: {}".format(sender, text))
									if sender.lower() != config.USERNAME.lower():
										self.parse_message(sender, text, whisper=True)
								
							# Regular message
							else:
								d = data["message"]["message"][0]
								sender = data["user_name"]
								
								#Try to parse a command out of the received string
								if sender.lower() != config.USERNAME.lower():
									text = d["data"]
									print("<" + sender + "> " + text)
									self.parse_message(sender, text)
									
					# if UserJoin
					elif event == "UserJoin":
						ud = (data["username"], {"roles": data["roles"], "id": data["id"]})
						print("User {} joined the channel".format(ud[0]))
						
					# if WelcomeEvent
					elif event == "WelcomeEvent":
						self.server = data["server"]
						
					# if UserLeave
					elif event == "UserLeave":
						ud = (data["username"], {"roles": data["roles"], "id": data["id"]})
						print("User {} left the channel".format(ud[0]))
						
					else:
						print("There is a {} event packet".format(event))
						print(packet)
		else:
			print("**********Unknown Message**********")
			print(packet)


##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=USER STUFF=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=##
	def add_money_to_users(self, users):
		for u in users.keys():
			if u in self.userdata:
				self.userdata[u][self.moneyname] += self.moneystep
				self.userdata[u]["timeunits"] += 1
				self.userdata[u]["userRoles"] = users[u]
			else:
				self.userdata.update(
					{u.lower():{
					self.moneyname : self.moneystep,
					"timeunits": 1,
					"userRoles": users[u]
					}}
				)
		self.write_userdata()
		
	def write_userdata(self):
		for s in self.userdata:
			self.userdata[s.lower()] = self.userdata.pop(s)
		with open("./userdata.dat", 'w') as outfile:
			json.dump(self.userdata, outfile)
		
	def read_userdata(self):
		try:
			f = open("./userdata.dat", "r")
			self.userdata = json.loads(f.read())
			f.close()
		except:
			self.userdata = {}
			
	def sendcommands(self, sender, whisper=True):
		self.send_whisper(sender, ", ".join(self.legal))
		
	def testmod(self, sender):
		if sender.lower() in self.userdata:
			self.send_message("{} has user roles {}".format(sender, self.userdata[sender.lower()]["userRoles"]))
			
		
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=MONEY COMMANDS=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=##
	
	def dothread(self, t, a=None, k=None):
		if a:
			if k:
				t = threading.Thread(target=t, args=a, kwargs=k)
				t.start()
			else:
				t = threading.Thread(target=t, args=a)
				t.start()
		else:
			t = threading.Thread(target=t)
			t.start()
			
	def tellmoney(self, user, whisper=False):
		self.send_message(user + ": You have " + str(self.checkmoney(user)) + " " + self.moneyname, user=user, whisper=whisper)
	
	def checkmoney(self, user):
		user = user.lower()
		if user in self.userdata:
			return self.userdata[user][self.moneyname]
		else:
			return 0
	
	def checktime(self, user):
		user = user.lower()
		if user in self.userdata:
			return str(datetime.timedelta(seconds=(self.userdata[user]["timeunits"]*config.MONEYUPDATE)))
		else:
			return 0
		
	def telltime(self, sender, message):
		if message not in self.userdata:
			x = self.checktime(sender)
			user = sender
		else:
			x = self.checktime(message)
			user = message
		if x == 0:
			self.chat.message("User data for {} was not found".format(user))
		else:
			self.chat.message("{} has spent {} in this channel".format(user, x))
		
	def skipsong(self, user, whisper=False):
		if(self.chat):
			cost = 100
		else:
			cost = 0
			
		if (self.checkmoney(user) - cost) >= 0:
			self.k.press_key(17)
			time.sleep(.2)
			inputsim.pressKey(0.2, 'n')
			time.sleep(.2)
			self.k.release_key(17)
			
			self.send_message(user + " Skipped the current song", user=user, whisper=whisper)
				
			self.userdata[user][self.moneyname] -= cost
		else:
			self.send_message(user + ": You don't have enough {} to skip the song (need {}).".format(self.moneyname, cost), user=user, whisper=whisper)
			

	def text2speech(self, user, msg):
		self.dothread(self.t2s, (user, msg))

		
	def t2s(self, user, msg):
		if len(msg) > 5:
				
			if(self.chat):
				cost = 300
			else:
				cost = 0
			
			if (self.checkmoney(user) - cost) >= 0:
				print("TTS: {} said {}".format(user, msg))
				self.es.say("{} said {}".format(user, msg))
				self.userdata[user][self.moneyname] -= cost
			else:
				self.send_whisper(user, "You don't have enough {} to skip the song (need {}).".format(self.moneyname, cost))
		else:
			self.send_whisper(user, "Your message was not long enough")

