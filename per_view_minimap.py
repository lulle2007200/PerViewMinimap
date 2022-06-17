import sublime
import sublime_plugin

import enum
from typing import Optional

prev_minimap_state = {}

class Mode(enum.Enum):
	MINIMAP_YES = 1
	MINIMAP_NO = 2
	MINIMAP_ANY = 3

def plugin_loaded() -> None:
	for window in sublime.windows():
		prev_minimap_state[window.id()] = window.is_minimap_visible()

def get_active_view() -> Optional[sublime.View]:
	return sublime.active_window().active_view()

def set_minimap_mode(view: sublime.View, mode: Mode) -> None:
	view.settings().set("minimap_mode", mode.value)

def get_minimap_mode(view: sublime.View) -> Mode:
	return Mode(view.settings().setdefault("minimap_mode", Mode.MINIMAP_ANY.value))

def update_mode(view: sublime.View) -> None:
	mode = get_minimap_mode(view)
	window = view.window()
	if mode != Mode.MINIMAP_ANY:
		if view.id() == get_active_view().id():
			if mode == Mode.MINIMAP_YES:
				window.set_minimap_visible(True)
			else:
				window.set_minimap_visible(False)
	else:
		window.set_minimap_visible(prev_minimap_state[window.id()])


class MinimapNoneCommand(sublime_plugin.ApplicationCommand):
	def run(self) -> None:
		pass

class MinimapDisableForViewCommand(sublime_plugin.TextCommand):
	def is_checked(self) -> bool:
		return get_minimap_mode(self.view) == Mode.MINIMAP_NO
	def run(self, edit: sublime.Edit) -> None:
		mode = get_minimap_mode(self.view)
		if mode == Mode.MINIMAP_NO:
			set_minimap_mode(self.view, Mode.MINIMAP_ANY)
		else:
			set_minimap_mode(self.view, Mode.MINIMAP_NO)
		update_mode(self.view)

class MinimapEnableForViewCommand(sublime_plugin.TextCommand):
	def is_checked(self) -> bool:
		return get_minimap_mode(self.view) == Mode.MINIMAP_YES
	def run(self, edit: sublime.Edit) -> None:
		mode = get_minimap_mode(self.view)
		if mode == Mode.MINIMAP_YES:
			set_minimap_mode(self.view, Mode.MINIMAP_ANY)
		else:
			set_minimap_mode(self.view, Mode.MINIMAP_YES)
		update_mode(self.view)

class PreviewMinimapEventListener(sublime_plugin.EventListener):
	def on_new_window(self, window: sublime.Window) -> None:
		prev_minimap_state[window.id()] = window.is_minimap_visible()
	def on_activated(self, view: sublime.View) -> None:
		mode = get_minimap_mode(view) 
		if(mode != Mode.MINIMAP_ANY):
			window = view.window()
			prev_minimap_state[window.id()] = window.is_minimap_visible()
			if mode == Mode.MINIMAP_YES:
				window.set_minimap_visible(True)
			else:
				window.set_minimap_visible(False)

	def on_deactivated(self, view: sublime.View) -> None:
		window = view.window()
		window.set_minimap_visible(prev_minimap_state[window.id()])

	def on_window_command(self, window: sublime.Window, command_name: str, args):
		if command_name == "toggle_minimap":
			if get_minimap_mode(window.active_view()) != Mode.MINIMAP_ANY:
				return ("minimap_none", None)
		return None

	def on_post_window_command(self, window: sublime.Window, command_name: str, args) -> None:
		if command_name == "toggle_minimap":
			prev_minimap_state[window.id()] = window.is_minimap_visible()