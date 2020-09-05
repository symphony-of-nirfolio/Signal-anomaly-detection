import _thread
import random
from typing import Callable

import pygame

from handle_data.data_management import get_audio_info_from_json, write_audio_info_to_json


_audio_source_path = "audio/source/"


def audio_manager() -> (Callable[[], None],
                        Callable[[], float],
                        Callable[[], float],
                        Callable[[float], None],
                        Callable[[float], None]):
    pygame.init()
    pygame.display.init()
    pygame.mixer.init()

    music_name = "background_music_{}.mp3"

    musics_count = 5
    last_music_index = -1

    audio_info = get_audio_info_from_json()

    pygame.mixer.pre_init(44100, 16, 2, 4096)
    pygame.init()

    music_ended = pygame.USEREVENT + 1
    # noinspection PyArgumentList
    pygame.mixer.music.set_endevent(music_ended)

    def get_random_music_file_name() -> str:
        nonlocal last_music_index

        current_music_index = last_music_index
        while current_music_index == last_music_index:
            current_music_index = random.randint(0, musics_count - 1)

        last_music_index = current_music_index

        file_name = _audio_source_path + music_name.format(str(current_music_index))
        return file_name

    def play_random_music() -> None:
        file_name = get_random_music_file_name()

        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play()

    def add_random_music_to_queue() -> None:
        file_name = get_random_music_file_name()

        pygame.mixer.music.queue(file_name)

    def music_switcher():
        is_music_switcher_running = True
        while is_music_switcher_running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_music_switcher_running = False

                if event.type == music_ended and is_music_switcher_running:
                    add_random_music_to_queue()

    def play_finish_notification() -> None:
        pygame.mixer.Channel(1).play(pygame.mixer.Sound(_audio_source_path + "finish_notification.wav"))

    def play_error_notification() -> None:
        pygame.mixer.Channel(2).play(pygame.mixer.Sound(_audio_source_path + "error_notification.wav"))

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

    _thread.start_new_thread(music_switcher, ())

    play_random_music()
    add_random_music_to_queue()

    pygame.mixer.music.set_volume(get_music_volume())
    pygame.mixer.Channel(1).set_volume(get_sound_effect_volume())
    pygame.mixer.Channel(2).set_volume(get_sound_effect_volume())

    return play_finish_notification, play_error_notification, get_sound_effect_volume, get_music_volume,\
        set_sound_effect_volume, set_music_volume
