from typing import Callable

from gui.main_window import Ui_main_window
from gui.settings_window import Ui_settings_window
from gui.window_with_close_listener import WindowWithCloseListener


def _gui_init_setting_window(ui: Ui_settings_window,
                             get_sound_effect_volume: Callable[[], float],
                             get_music_volume: Callable[[], float],
                             set_sound_effect_volume: Callable[[float], None],
                             set_music_volume: Callable[[float], None]):
    sound_effect_volume_horizontal_slider = ui.sound_effect_volume_horizontal_slider
    music_volume_horizontal_slider = ui.music_volume_horizontal_slider

    sound_effect_volume_horizontal_slider.setValue(int(get_sound_effect_volume() * 100))
    music_volume_horizontal_slider.setValue(int(get_music_volume() * 100))

    def on_sound_effect_volume_changed():
        set_sound_effect_volume(sound_effect_volume_horizontal_slider.value() / 100.0)

    def on_music_volume_changed():
        set_music_volume(music_volume_horizontal_slider.value() / 100.0)

    sound_effect_volume_horizontal_slider.valueChanged.connect(on_sound_effect_volume_changed)
    music_volume_horizontal_slider.valueChanged.connect(on_music_volume_changed)


def gui_init_settings(ui: Ui_main_window,
                      get_sound_effect_volume: Callable[[], float],
                      get_music_volume: Callable[[], float],
                      set_sound_effect_volume: Callable[[float], None],
                      set_music_volume: Callable[[float], None]) -> Callable[[], None]:
    action_settings = ui.action_settings

    settings_window = None

    is_settings_window_open = False

    def on_settings_window_close():
        nonlocal is_settings_window_open
        is_settings_window_open = False
        action_settings.setEnabled(True)

    def on_action_settings_clicked():
        nonlocal is_settings_window_open, settings_window
        is_settings_window_open = True
        action_settings.setEnabled(False)

        settings_window = WindowWithCloseListener(on_settings_window_close)
        settings_ui = Ui_settings_window()
        settings_ui.setupUi(settings_window)

        _gui_init_setting_window(settings_ui,
                                 get_sound_effect_volume,
                                 get_music_volume,
                                 set_sound_effect_volume,
                                 set_music_volume)

        settings_window.show()

    def close_listener() -> None:
        if is_settings_window_open:
            # noinspection PyUnresolvedReferences
            settings_window.close()

    action_settings.triggered.connect(on_action_settings_clicked)

    return close_listener
