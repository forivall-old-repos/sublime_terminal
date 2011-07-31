import sublime
import sublime_plugin
import os
import sys
import subprocess
import stat


class TerminalSelector():
	default = None

	@staticmethod
	def get():
		settings = sublime.load_settings('Terminal.sublime-settings')

		if settings.get('terminal'):
			return settings.get('terminal')
		
		if TerminalSelector.default:
			return TerminalSelector.default
		
		if os.name == 'nt':
			powershell = os.environ['SYSTEMROOT'] + '\\System32\\WindowsPowerShell\\v1.0\\powershell.exe'
			if os.path.exists(powershell):
				default = powershell
			else :
				default = os.environ['SYSTEMROOT'] + '\\System32\\cmd.exe'
		
		elif sys.platform == 'darwin':
			default = os.path.join(sublime.packages_path(), __name__, 'Terminal.sh')
			os.chmod(default, 0755)
		
		else:
			wm = [x.replace("\n", '') for x in os.popen('ps -eo comm | grep -E "gnome-session|ksmserver|xfce4-session" | grep -v grep')]
			if wm:
				if wm[0] == 'gnome-session':
					default = 'gnome-terminal'
				elif wm[0] == 'xfce4-session':
					default = 'xfce4-terminal'
				elif wm[0] == 'ksmserver':
					default = 'konsole'
			if not default:
				default = 'xterm'
		
		TerminalSelector.default = default
		return default
	

class TerminalCommand():
	def run_terminal(self, dir):
		try:
			if not dir:
				raise NotFoundError('The file open in the selected view has not yet been saved')
			ForkGui(TerminalSelector.get(), dir)
		except (OSError) as (exception):
			print str(exception)
			sublime.error_message('Terminal: The terminal ' + TerminalSelector.get() + ' was not found')
		except (Exception) as (exception):
			sublime.error_message('Terminal: ' + str(exception))


class OpenTerminalCommand(sublime_plugin.WindowCommand, TerminalCommand):
	def run(self, paths=[]):
		path = paths[0] if paths else self.window.active_view().file_name()
		if not path:
			return
		if os.path.isfile(path):
			path = os.path.dirname(path)
		self.run_terminal(path)


class OpenTerminalProjectFolderCommand(sublime_plugin.WindowCommand, TerminalCommand):
	def run(self, paths=[]):
		path = paths[0] if paths else self.window.active_view().file_name()
		if path:
			folder_names = [x for x in self.window.folders() if path.find(x) == 0]
			if folder_names:
				path = folder_names[0]
		
		command = OpenTerminalCommand(self.window)
		command.run([path])


class ForkGui():
	def __init__(self, *args):
		self.args = args
		self.run()

	def run(self):
		proc = subprocess.Popen(self.args[0], stdin=subprocess.PIPE,
			stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.args[1])


class NotFoundError(Exception):
	pass