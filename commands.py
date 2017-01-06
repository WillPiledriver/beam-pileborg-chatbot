import random, markovify, glob, time, requests, json


class commands:
	
	def __init__(self, chathandle=None):
		self.ch = chathandle
		

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
		r = random.randint(1,8)
		
		
		if r == 1:
			answer = "It is certain"
		elif r == 2:
			answer = "Outlook good"
		elif r == 3:
			answer = "You may rely on it"
		elif r == 4:
			answer = "Ask again later"
		elif r == 5:
			answer = "Concentrate and ask again"
		elif r == 6:
			answer = "Reply hazy, try again"
		elif r == 7:
			answer = "My reply is no"
		else:
			answer = "My sources say no"
			
		self.send_message(answer)
		
	def suggest(self, sender, msg):
		if len(msg) > 5:
			with open("suggestions.txt", "a") as myfile:
				myfile.write("\n<{}> {}".format(sender, msg))
			self.send_message("{}: Your suggestion has been added to the list".format(sender))
		else:
			self.send_whisper(sender, "The length of your suggestion was not long enough.")
			
		
	def urban(self, sender, msg):
		response = requests.get("https://mashape-community-urban-dictionary.p.mashape.com/define?term={}".format(msg), headers={
								"X-Mashape-Key": "YOUR API KEY FROM MASHAPES URBAN API",
								"Accept": "text/plain"})
		if response.status_code == 200:
			response = json.loads(response.content.decode('utf-8'))
			if len(response["list"]) > 0:
				response = response["list"][0]["definition"]
				self.send_message("{}: {}".format(sender, response))
			else:
				self.send_message("No definitition found for {}".format(msg))
		elif response.status_code == 403:
			print("Forbidden response from urban API server. Most likely an incorrect API key. Check commands.py")
		else:
			print("Response was {}".format(response.status_code))
