import curses
import curses.ascii
import re
import subprocess

controls = list(range(0,9)) + list(range(11,32)) + list(range(127,160))
control_chars = ''.join(map(chr, controls))

control_char_re = re.compile('[%s]' % re.escape(control_chars))

def remove_control_chars(s):
	return control_char_re.sub('', s)
   
def is_printable(s):
	return control_char_re.sub('', s) == s

def is_control(key):
	return (key in controls or key > 255)

def debug(txt):
	with open("/tmp/status", "a") as f:
		f.write(txt+"\n")


def load_clipboard():
	global __zutils_has_cp
	global __zutils_clipboard
	global __zutils_cp
	
	__zutils_has_cp = 0
	__zutils_cp = ""
	try:
		#exec(s)
		
		mod_pygtk = __import__("pygtk")
		mod_pygtk.require('2.0')
		mod_gtk = __import__("gtk")
		__zutils_clipboard = gtk.clipboard_get()
		__zutils_has_cp = 1
	except Exception as e:
		debug(":( "+str(e))
		debug("Let's try xsel instead!")
		try:
			subprocess.check_call(["xsel"])
			__zutils_has_cp = 2
		except Exception as e:
			debug("Nope: "+str(e))
		

def get_cp():
	global __zutils_has_cp
	global __zutils_clipboard
	global __zutils_cp
	if __zutils_has_cp == 0:
		return __zutils_cp
	elif __zutils_has_cp == 1:
		return __zutils_clipboard.wait_for_text()
	elif __zutils_has_cp == 2:
		a = subprocess.check_output(["xsel", "-ob"])
		#debug("PASTE: "+str(a))
		return a.decode("utf-8", "replace")
	
def copy_cp(s):
	global __zutils_has_cp
	global __zutils_clipboard
	global __zutils_cp
	if __zutils_has_cp == 0:
		__zutils_cp = s
	elif __zutils_has_cp == 1:
		__zutils_clipboard.set_text(s)
		__zutils_clipboard.store()
	elif __zutils_has_cp == 2:
		p = subprocess.Popen(['xsel', '-ib'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
		p.communicate(input=bytearray(s, encoding="utf-8"))


debug("--- starting ---")

#KEY_VT		= curses.ascii.VT
#KEY_HT 		= curses.ascii.HT
#KEY_SHT		= 353
#KEY_LEFT	= curses.KEY_LEFT
#KEY_CLEFT	= 540
#KEY_RIGHT	= curses.KEY_RIGHT
#KEY_CRIGHT	= 555
#KEY_UP		= curses.KEY_UP
#KEY_CUP		= 561
#KEY_CSUP	= 562
#KEY_DOWN	= curses.KEY_DOWN
#KEY_CDOWN	= 520
#KEY_CSDOWN	= 521
#KEY_DEL		= curses.KEY_DC
#KEY_SDEL	= 383
#KEY_CDEL	= 514
#KEY_HOME	= curses.KEY_HOME
#KEY_SHOME	= 391
#KEY_CHOME	= 530
#KEY_END		= curses.KEY_END
#KEY_SEND	= 386
#KEY_CEND	= 525
#KEY_BACKSPACE	= curses.ascii.DEL
#KEY_RETURN	= curses.ascii.LF
#KEY_SRETURN	= 343
#KEY_PAGEDOWN	= 338
#KEY_PAGEUP	= 339
#KEY_CPAGEDOWN	= 545
#KEY_CPAGEUP	= 550
#KEY_CW		= 23
#KEY_CD		= 4
#KEY_CN		= 14
#KEY_CX		= 24
#KEY_CV		= 22
#KEY_CA		= 1
#KEY_CF		= 6
#KEY_ESC		= curses.ascii.ESC
#KEY_SPACE	= 32

KEY_VT		= curses.ascii.VT
KEY_HT 		= curses.ascii.HT
KEY_SHT		= 353
KEY_LEFT	= curses.KEY_LEFT
KEY_SLEFT	= 393 
KEY_CLEFT	= 546
KEY_RIGHT	= curses.KEY_RIGHT
KEY_SRIGHT	= 402
KEY_CRIGHT	= 561
KEY_UP		= curses.KEY_UP
KEY_SUP		= 337
KEY_CUP		= 567
KEY_CSUP	= 568
KEY_DOWN	= curses.KEY_DOWN
KEY_SDOWN	= 336
KEY_CDOWN	= 526
KEY_CSDOWN	= 527
KEY_DEL		= curses.KEY_DC
KEY_SDEL	= 383
KEY_CDEL	= 520
KEY_HOME	= curses.KEY_HOME
KEY_SHOME	= 391
KEY_CHOME	= 536
KEY_END		= curses.KEY_END
KEY_SEND	= 386
KEY_CEND	= 531
KEY_BACKSPACE	= 263
KEY_RETURN	= curses.ascii.LF
KEY_SRETURN	= 343
KEY_PAGEDOWN	= 338
KEY_PAGEUP	= 339
KEY_SPAGEDOWN	= 396
KEY_SPAGEUP	= 398
KEY_CPAGEDOWN	= 551
KEY_CPAGEUP	= 556
KEY_CW		= 23
KEY_CD		= 4
KEY_CN		= 14
KEY_CX		= 24
KEY_CV		= 22
KEY_CA		= 1
KEY_CF		= 6
KEY_CR		= 18
KEY_CO		= 15
KEY_ESC		= curses.ascii.ESC
KEY_SPACE	= 32

KEY_F1 = 265
KEY_F2 = 266
KEY_F3 = 267
KEY_F4 = 268
KEY_F5 = 269
KEY_F6 = 270
KEY_F7 = 271
KEY_F8 = 272
KEY_F9 = 273
KEY_F10 = 274
KEY_F11 = 275
KEY_F12 = 276



CL_BLACK   = curses.COLOR_BLACK
CL_BLUE    = curses.COLOR_BLUE
CL_CYAN    = curses.COLOR_CYAN
CL_GREEN   = curses.COLOR_GREEN
CL_MAGENTA = curses.COLOR_MAGENTA
CL_RED     = curses.COLOR_RED
CL_WHITE   = curses.COLOR_WHITE
CL_YELLOW  = curses.COLOR_YELLOW
CL_GREY    = 7
CL_FG      = curses.COLOR_WHITE
CL_BG      = curses.COLOR_BLACK


AT_BLINK     = curses.A_BLINK
AT_BOLD	     = curses.A_BOLD
AT_DIM       = curses.A_DIM
AT_NORMAL    = curses.A_NORMAL
AT_REVERSE   = curses.A_REVERSE
AT_STANDOUT  = curses.A_STANDOUT
AT_UNDERLINE = curses.A_UNDERLINE
