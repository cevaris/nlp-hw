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

	def store(self):
		return self.store

	def __repr__(self):
		output = []
		for key in self.store.keys():
			output.append( "%s:%d" % (key, self.count(key)))
		return "\n".join(output)
			
