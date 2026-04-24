import pyxel

from .assets import load_assets
from .config import FPS, KEYBINDS, SCREEN_H, SCREEN_W, TITLE
from .input_handler import InputHandler
from .scene import SceneManager
from .scenes.title_scene import TitleScene


class Game:
    def __init__(self) -> None:
        pyxel.init(SCREEN_W, SCREEN_H, title=TITLE, fps=FPS)
        load_assets()
        self._input = InputHandler(KEYBINDS)
        self._scenes = SceneManager(TitleScene())
        pyxel.run(self._update, self._draw)

    def _update(self) -> None:
        self._scenes.update(self._input)

    def _draw(self) -> None:
        self._scenes.draw()
