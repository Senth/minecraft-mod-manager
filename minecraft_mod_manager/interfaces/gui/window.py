from kivy.app import App
from kivy.uix.button import Button


class Window(App):
    def build(self):
        return Button(text="Hello world")
