# beam-pileborg-chatbot
### A Python chat bot for Beam.pro
Designed for Python 3.5

This is an early version, and a bit sloppy. There are a lot of dependencies. Glance over the code for a while to see how it works, then strip all the unwanted functions.
I modified beam.pro's chatty bot to better suit my needs. I will include the licences and make a more detailed readme later, but for now this is a project that is currently in development.


### Feel free to make a pull request


# How it works

I started this project with customizability in mind. If you have skill in Python, you could build a function, attach a command to it, and deploy it in minutes. It's based on ProbablePrime's [beam client](https://github.com/WatchBeam/beam-client-python).

* pileborg.py is the script that needs to be executed.
* Make sure you have the correct details in config.py.
* pileborg.py uses bot.py to communicate with beam. All packets are handled through bot.py.
* init of bot.py esentially contains the UI of the chat bot. Commands are defined and assigned to functions by use of a dictionary type.
* Any packet that is a whisper or a message is filtered and parsed so arguments can be passed to functions through user input.
* User data is stored in userdata.dat. This file contains the amount of currency the user has and how much time they have spent in the channel. User roles are also stored in this file.
* the chat handle is passed to commands.py so you can develop most of your functions seperately from the rest of the code. Organization makes thinking about code easier.
* If you can think of anything to add, please contribute to this code.

## Dependencies

For the example commands, there are a few unnecessary dependencies such as PyKeyboard (keyboard simulation on windows), espeak (Text to speech on windows), markovify (markov-chain algorithm for generating pseudo-random sentences).

###Required dependencies

[Tornado](https://pypi.python.org/pypi/tornado "Pypi Tornado") is needed for this program.
threading, datetime, re, socket, requests are also needed.