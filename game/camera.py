from .config import SCREEN_H, SCREEN_W, TILE_SIZE


class Camera:
    def __init__(self) -> None:
        self.x: float = 0.0
        self.y: float = 0.0

    def follow(self, target_x: float, target_y: float, world_w: int, world_h: int) -> None:
        self.x = target_x - SCREEN_W / 2
        self.y = target_y - SCREEN_H / 2
        max_x = max(0.0, world_w * TILE_SIZE - SCREEN_W)
        max_y = max(0.0, world_h * TILE_SIZE - SCREEN_H)
        if self.x < 0:
            self.x = 0.0
        elif self.x > max_x:
            self.x = max_x
        if self.y < 0:
            self.y = 0.0
        elif self.y > max_y:
            self.y = max_y
