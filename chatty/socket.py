from .evented import Evented
from tornado.websocket import websocket_connect
from tornado.ioloop import IOLoop

from random import randint
from json import loads, dumps


class Socket(Evented):

	packet_id = 0

	def __init__(self, addresses):
		super(Socket, self).__init__()

		self.connected = False
		self.ws = None

		self.address_offset = randint(0, len(addresses)-1)
		self.addresses = addresses

		self._connect()

	def _get_address(self):
		self.address_offset += 1
		self.address_offset %= len(self.addresses)

		return self.addresses[self.address_offset]

	def _connect(self):
		address = self._get_address()
		print("Connecting to {}...".format(address))

		websocket_connect(
			address,
			callback=self._on_open,
			on_message_callback=self._parse_packet
		)

	def _parse_packet(self, packet_str):
		if packet_str is None:
			self._on_close(1)
		else:
			packet = loads(packet_str)
			#self.emit("message", packet["data"])
			self.emit("message", packet)

			
	def _on_open(self, future):
		if future.exception() is None:
			self.ws = future.result()
			self.connected = True
			self.emit("opened")
		else:
			print("Unable to connect to the socket.")
			print("Retrying in 1 second.")

			self.connected = False

			IOLoop.instance().call_later(1, self._connect)

	def _on_close(self, code, reason=None):
		print("Socket closed.")
		print("Reestablishing the socket in 1 second.")
		self.connected = False
		self.emit("closed")

		IOLoop.instance().call_later(1, self._connect)

	def send(self, type, *args, **kwargs):
		if not self.connected:
			return

		packet = {
			"type": type,
			"arguments": args,
			"id": self.packet_id
		}

		packet.update(kwargs)
		if "method" in kwargs:
			if kwargs["method"] is "msg":
				print("Sent Message: " + args[0])
			elif kwargs["method"] is "whisper":
				print("Whisper to {}: {}".format(args[0], args[1]))
		else:
			print("SEND:", packet)
		self.ws.write_message(dumps(packet))
		self.packet_id += 1
