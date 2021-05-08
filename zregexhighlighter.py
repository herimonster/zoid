import zutils
import zhighlighter
import re
import shlex

class zregexhighlighter(zhighlighter.zhighlighter):
	def __init__(self):
		self.rules = []
		self.extensions = []
		
		#self.add_rule("\"[^\"]*\"", zutils.CL_BLACK, zutils.CL_WHITE, zutils.AT_BOLD)
		
	def add_rule(self, regex, fg, bg, attr):
		ex = re.compile(regex)
		self.rules.append({"expression": regex, "r": ex, "attr": (fg,  bg, attr)})
	
	def load_rules(self, filename):
		with open(filename, "r") as f:
			first = True
			for line in f:
				if first:
					l = shlex.split(line, ",")
					for ext in l:
						self.extensions.append(ext.strip())
					first = False
					continue
				
				l = shlex.split(line, ",")
				if len(l) < 4:
					zutils.debug("SKIPPING RULE "+line)
					continue
				r = l[0].strip()
				fg = getattr(zutils, l[1].strip(), zutils.CL_BLACK)
				bg = getattr(zutils, l[2].strip(), zutils.CL_WHITE)
				at = getattr(zutils, l[3].strip(), zutils.AT_NORMAL)
				zutils.debug("ADDING RULE "+r)
				self.add_rule(r, fg, bg, at)
				
				#print(self.rules)
				
	
	def highlight(self, text):
		
		attr =  [(zutils.CL_FG, zutils.CL_BG, zutils.AT_NORMAL) for i in range(len(text))]
		for r in self.rules:
			reg = r["r"]
			at = r["attr"]
			for match in reg.finditer(text):
				j = len(match.groups())
				for j in range(match.start(j), match.end(j)):
					attr[j] = at
		return attr
	
	def __str__(self):
		s = "zregexhighlighter, "+str(len(self.rules))+" rules:\n"
		for rule in self.rules:
			s+= "  "+rule["expression"] + "\n"
		return s
