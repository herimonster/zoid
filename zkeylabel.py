import zlabel
import zutils

class zkeylabel(zlabel.zlabel):
	def on_key(self, key, char):
		#self._caption = "Key {0:08b} ({1})".format(key, char)
		self._caption = "Key {0} ({1})".format(str(key), char)
	