from kivy.app import App
from kivy.uix.widget import Widget

from kivy.graphics import Color, Ellipse, Rectangle, Line


class PainterWidget(Widget):
    def __init__(self, **kwargs):
        super(PainterWidget, self).__init__(**kwargs)

        with self.canvas:
            Color(0, 1, 0, 1)
            self.line = Line(points=(), width=2)

    def on_touch_down(self, touch):
        self.line.points += (touch.x, touch.y)


class PaintApp(App):
    def build(self):
        return PainterWidget()


if __name__ == '__main__':
    PaintApp().run()
