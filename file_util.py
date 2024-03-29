import pickle
import gzip


def save(object, filename, bin = 1):
	"""Saves a compressed object to disk
	"""
	file = gzip.GzipFile(filename, 'wb')
	file.write(pickle.dumps(object, bin))
	file.close()


def load(filename):
	"""Loads a compressed object from disk
	"""
	file = gzip.GzipFile(filename, 'rb')
	object = pickle.loads(file.read())
	file.close()
	return object