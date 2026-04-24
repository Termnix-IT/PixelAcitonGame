import pyxel

from ..config import COL_BG, COL_TEXT, COL_TEXT_DIM, SCREEN_W
from ..input_handler import InputHandler
from ..scene import Scene
from ..sfx import SFX_CONFIRM, play_sfx, stop_bgm


class GameOverScene(Scene):
    _OPTIONS: tuple[tuple[str, str], ...] = (
        ("RETRY", "retry"),
        ("TITLE", "title"),
    )

    def __init__(self) -> None:
        self._index = 0

    def on_enter(self, manager) -> None:
        super().on_enter(manager)
        stop_bgm()

    def update(self, inp: InputHandler) -> None:
        if inp.is_pressed("move_up"):
            self._index = (self._index - 1) % len(self._OPTIONS)
        elif inp.is_pressed("move_down"):
            self._index = (self._index + 1) % len(self._OPTIONS)
        if inp.is_pressed("confirm"):
            play_sfx(SFX_CONFIRM)
            choice = self._OPTIONS[self._index][1]
            if choice == "retry":
                from .play_scene import PlayScene
                self._manager.replace(PlayScene())
            else:
                from .title_scene import TitleScene
                self._manager.replace(TitleScene())

    def draw(self) -> None:
        pyxel.cls(COL_BG)

        title = "GAME OVER"
        tx = (SCREEN_W - len(title) * 4) // 2
        pyxel.text(tx, 40, title, COL_TEXT)

        for i, (label, _) in enumerate(self._OPTIONS):
            col = COL_TEXT if i == self._index else COL_TEXT_DIM
            prefix = "> " if i == self._index else "  "
            display = prefix + label
            px = (SCREEN_W - len(display) * 4) // 2
            pyxel.text(px, 62 + i * 10, display, col)
