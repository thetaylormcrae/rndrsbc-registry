# Sample community widget — same contract as built-ins.
from widgets.base import BaseWidget, register_widget

@register_widget("sample_widget")
class SampleWidget(BaseWidget):
    def __init__(self, **cfg):
        super().__init__(**cfg)
        self.label = cfg.get("label", "community")
    def render(self, draw, width, height):
        draw.rounded_rectangle((8, 8, width - 8, height - 8),
                               radius=10, outline="black", width=2)
        draw.text((20, 20), f"sample: {self.label}", fill="black")
        return "sample", self.label
