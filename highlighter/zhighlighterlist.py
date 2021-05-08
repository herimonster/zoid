import sys
import os


def get_list():
	files = []
	path = os.path.dirname(os.path.realpath(__file__))
	for i in os.listdir(path):
		if i.endswith(".hl"):
			files.append(os.path.join(path, i))
	return files
