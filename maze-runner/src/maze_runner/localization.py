# Localization / Bilingual Support
# English and Persian (Farsi) translations

TRANSLATIONS = {
    "en": {
        "title": "Maze Runner",
        "menu_move": "Move with Arrow Keys or WASD",
        "menu_find_exit": "Find the hidden exit in the maze",
        "current_level": "Current Level",
        "total_play_time": "Total Play Time",
        "levels_completed": "Levels Completed",
        "press_enter": "Press ENTER to continue",
        "press_clear": "Press C to clear progress",
        "press_quit": "Press ESC to quit",
        "press_menu": "Press Q to quit to menu",
        "level": "Level",
        "moves": "Moves",
        "time": "Time",
        "best": "Best",
        "rank": "Rank",
        "quit_menu": "[Q] Menu  [ESC] Quit",
        "level_complete": "Level Complete!",
        "next_replay_menu": "ENTER for next level   |   R to replay   |   Q to menu",
        "toggle_theme": "[T] Toggle Theme",
        "toggle_lang": "[L] Language",
    },
    "fa": {
        "title": "دونده هزارتو",
        "menu_move": "حرکت با کلیدهای جهت‌دار یا WASD",
        "menu_find_exit": "خروج مخفی را در هزارتو پیدا کنید",
        "current_level": "مرحله فعلی",
        "total_play_time": "زمان کل بازی",
        "levels_completed": "مراحل تکمیل شده",
        "press_enter": "ENTER را برای ادامه فشار دهید",
        "press_clear": "C را برای پاک کردن پیشرفت فشار دهید",
        "press_quit": "ESC را برای خروج فشار دهید",
        "press_menu": "Q را برای بازگشت به منو فشار دهید",
        "level": "مرحله",
        "moves": "حرکات",
        "time": "زمان",
        "best": "بهترین",
        "rank": "رتبه",
        "quit_menu": "[Q] منو  [ESC] خروج",
        "level_complete": "مرحله تکمیل شد!",
        "next_replay_menu": "ENTER برای مرحله بعد   |   R برای تکرار   |   Q برای منو",
        "toggle_theme": "[T] تغییر تم",
        "toggle_lang": "[L] زبان",
    }
}

def get_text(key, lang="en"):
    """Get translated text for a key"""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
