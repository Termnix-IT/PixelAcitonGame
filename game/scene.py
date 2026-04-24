from __future__ import annotations

from typing import Optional

from .input_handler import InputHandler


class Scene:
    _manager: "SceneManager"
    # When True, SceneManager draws the scene(s) beneath this one before drawing us.
    transparent_draw: bool = False

    def on_enter(self, manager: "SceneManager") -> None:
        self._manager = manager

    def on_exit(self) -> None:
        pass

    def update(self, inp: InputHandler) -> None:
        pass

    def draw(self) -> None:
        pass


class _Transition:
    __slots__ = ("kind", "scene")

    def __init__(self, kind: str, scene: Optional[Scene] = None) -> None:
        self.kind = kind
        self.scene = scene


class SceneManager:
    def __init__(self, initial: Scene) -> None:
        self._stack: list[Scene] = []
        self._pending: list[_Transition] = []
        self._do_push(initial)

    @property
    def current(self) -> Scene:
        return self._stack[-1]

    def push(self, scene: Scene) -> None:
        self._pending.append(_Transition("push", scene))

    def pop(self) -> None:
        self._pending.append(_Transition("pop"))

    def replace(self, scene: Scene) -> None:
        self._pending.append(_Transition("replace", scene))

    def update(self, inp: InputHandler) -> None:
        self._apply_pending()
        if self._stack:
            self.current.update(inp)
        self._apply_pending()

    def draw(self) -> None:
        if not self._stack:
            return
        # Walk down until we hit an opaque scene, then draw bottom-up.
        start = len(self._stack) - 1
        while start > 0 and self._stack[start].transparent_draw:
            start -= 1
        for i in range(start, len(self._stack)):
            self._stack[i].draw()

    def _do_push(self, scene: Scene) -> None:
        self._stack.append(scene)
        scene.on_enter(self)

    def _do_pop(self) -> None:
        if self._stack:
            self._stack.pop().on_exit()

    def _apply_pending(self) -> None:
        while self._pending:
            t = self._pending.pop(0)
            if t.kind == "push" and t.scene is not None:
                self._do_push(t.scene)
            elif t.kind == "pop":
                self._do_pop()
            elif t.kind == "replace" and t.scene is not None:
                self._do_pop()
                self._do_push(t.scene)
