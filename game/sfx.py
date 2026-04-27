import pyxel

SFX_CH = 3  # channel reserved for one-shot SFX
BGM_CHANNELS = (0, 1, 2)

SFX_ATTACK = 0
SFX_HIT = 1
SFX_KILL = 2
SFX_CONFIRM = 3

BGM_PLAY = 0
BGM_BOSS = 1
BGM_ENDING = 2


def play_sfx(sound_id: int) -> None:
    pyxel.play(SFX_CH, sound_id)


def start_bgm(music_id: int = BGM_PLAY) -> None:
    pyxel.playm(music_id, loop=True)


def stop_bgm() -> None:
    for ch in BGM_CHANNELS:
        pyxel.stop(ch)
