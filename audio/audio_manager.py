from typing import Callable

import pygame

from handle_data.data_management import get_audio_info_from_json, write_audio_info_to_json


def audio_manager() -> (Callable[[], None],
                        Callable[[], float],
                        Callable[[], float],
                        Callable[[float], None],
                        Callable[[float], None]):
    pygame.mixer.init()

    audio_info = get_audio_info_from_json()

    pygame.mixer.pre_init(44100, 16, 2, 4096)
    pygame.init()

    pygame.mixer.music.load('audio/source/background_music.mp3')
    pygame.mixer.music.play(loops=-1)

    def play_finish_notification() -> None:
        pygame.mixer.Channel(1).play(pygame.mixer.Sound('audio/source/finish_notification.wav'))

    def play_error_notification() -> None:
        pygame.mixer.Channel(2).play(pygame.mixer.Sound('audio/source/error_notification.wav'))

    def get_sound_effect_volume() -> float:
        return audio_info["sound_effect_volume"]

    def get_music_volume() -> float:
        return audio_info["music_volume"]

    def set_sound_effect_volume(volume: float) -> None:
        if volume < 0.0:
            volume = 0.0
        if volume > 1.0:
            volume = 1.0

        pygame.mixer.Channel(1).set_volume(volume)
        pygame.mixer.Channel(2).set_volume(volume)

        audio_info["sound_effect_volume"] = volume
        write_audio_info_to_json(audio_info)

    def set_music_volume(volume: float) -> None:
        if volume < 0.0:
            volume = 0.0
        if volume > 1.0:
            volume = 1.0

        pygame.mixer.music.set_volume(volume)

        audio_info["music_volume"] = volume
        write_audio_info_to_json(audio_info)

    pygame.mixer.music.set_volume(get_music_volume())
    pygame.mixer.Channel(1).set_volume(get_sound_effect_volume())
    pygame.mixer.Channel(2).set_volume(get_sound_effect_volume())

    return play_finish_notification, play_error_notification, get_sound_effect_volume, get_music_volume,\
        set_sound_effect_volume, set_music_volume
