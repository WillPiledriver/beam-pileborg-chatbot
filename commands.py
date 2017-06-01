import random, markovify, glob, time, requests, json, datetime, config


class commands:
	
	def __init__(self, bothandle=None):
		self.bh = bothandle
		self.ch = bothandle.chat
		

	def send_message(self, msg):
		if(self.ch):
			self.ch.message(msg)
	
	def send_whisper(self, user, msg):
		if(self.ch):
			self.ch.whisper(user, msg)
		
	def markov(self):
		# Get raw text as string.
		files = glob.glob("./books/*.txt")
		text = ""
		if len(files) >= 5: numbers = random.sample(range(len(files)), 5)
		elif len(files) == 0:
			print("!markov command cannot be executed because there are no text files in books/")
			return
		else: numbers = range(len(files))
		for x in numbers:
			with open(files[x]) as f:
				text += f.read() + "\n"
		text_model = markovify.Text(text)
		text = None
		self.send_message(text_model.make_short_sentence(360))
		text_model = None
		f = None

	def d20(self):
		self.send_message("You rolled a " + str(random.randint(1, 20)))
		
	def eightball(self):
		
		reply = ["It is certain",
				 "Outlook good",
				 "You may rely on it",
				 "Ask again later",
				 "Concentrate and ask again",
				 "Reply hazy, try again",
				 "My reply is no",
				 "My sources say no"]
		self.send_message(reply[random.randint(0,7)])
		
	def suggest(self, sender, msg):
		if len(msg) > 5:
			with open("suggestions.txt", "a") as myfile:
				myfile.write("\n<{}> {}".format(sender, msg))
			self.send_message("{}: Your suggestion has been added to the list".format(sender))
		else:
			self.send_whisper(sender, "The length of your suggestion was not long enough.")
			
		
	def urban(self, sender, msg):
		response = requests.get("https://mashape-community-urban-dictionary.p.mashape.com/define?term={}".format(msg), headers={
								"X-Mashape-Key": "YOUR URBAN DICTIONARY API KEY",
								"Accept": "text/plain"})
		if response.status_code == 200:
			response = json.loads(response.content.decode('utf-8'))
			if len(response["list"]) > 0:
				response = response["list"][0]["definition"]
				self.send_message("@{}: {}".format(sender, response))
			else:
				self.send_message("No definitition found for {}".format(msg))
		elif response.status_code == 403:
			print("Forbidden response from urban API server. Most likely an incorrect API key. Check commands.py")
		else:
			print("Response was {}".format(response.status_code))
			
	def checktime(self, user):
		user = user.lower()
		if user in self.bh.userdata:
			return str(datetime.timedelta(seconds=(self.bh.userdata[user]["timeunits"]*config.MONEYUPDATE)))
		else:
			return 0
		
	def telltime(self, sender, message):
		if message not in self.bh.userdata:
			x = self.checktime(sender)
			user = sender
		else:
			x = self.checktime(message)
			user = message
		if x == 0:
			self.send_message("User data for {} was not found".format(user))
		else:
			self.send_message("{} has spent {} in this channel".format(user, x))

	def addMoney(self, sender, message):
		message = message.split(" ")
		if len(set(["Owner", "Mod"]) & set(self.bh.userdata[sender.lower()]["userRoles"])) > 0:
			if len(message) >= 2:
				rcv = message[0].lower()
				if rcv.lower() not in self.bh.userdata:
					self.send_whisper(sender, "You gave an invalid username.")
					return
				add = message[1]
				if add.isdigit():
					add = int(add)
				else:
					self.send_whisper(sender, "You gave an invalid number.")
					return

				self.bh.userdata[rcv][self.bh.moneyname] += add
				self.send_message("{} {} were gifted to {}".format(add, self.bh.moneyname, rcv))

			else:
				self.send_whisper(sender, "Command must be used like !gift <recipient> <money>")
		else:
			self.send_whisper(sender, "You do not have permission to use this command.")

	def shoutout(self, sender, msg):
		if len(set(["Owner", "Mod"]) & set(self.bh.userdata[sender.lower()]["userRoles"])) > 0:
			self.send_message("Shout out to @{}. Give them a follow http://mixer.com/{}".format(msg, msg))
		else:
			self.send_whisper(sender, "You do not have permission to use this command.")