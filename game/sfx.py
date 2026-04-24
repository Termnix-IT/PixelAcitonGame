import pyxel

SFX_CH = 3  # channel reserved for one-shot SFX
BGM_CHANNELS = (0, 1, 2)

SFX_ATTACK = 0
SFX_HIT = 1
SFX_KILL = 2
SFX_CONFIRM = 3

BGM_PLAY = 0


def play_sfx(sound_id: int) -> None:
    pyxel.play(SFX_CH, sound_id)


def start_bgm() -> None:
    pyxel.playm(BGM_PLAY, loop=True)


def stop_bgm() -> None:
    for ch in BGM_CHANNELS:
        pyxel.stop(ch)
