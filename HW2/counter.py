class Counter:

	def __init__(self):
		self.store = {}

	def put(self, key):
		if (key in self.store):
			self.store[key] +=1 
		else:
			self.store[key] = 1

	def count(self, key):
		if (key in self.store):
			return self.store[key]
		else:
			return 0
