from tkinter import *
from tkinter.messagebox import askokcancel
from tkinter.ttk import OptionMenu, Style, Checkbutton
from os.path import exists
from json import dump, load
from datetime import datetime
from pygame import mixer
from webbrowser import open as w_open

import AliasTkFunctions
from AliasTkFunctions import fix_resolution_issue, resize_window, initiate_grid, grid, ScrollableFrame, ToolTip
from AliasGeneralFunctions import time_ago

fix_resolution_issue()

main = Tk()
resize_window(main, 3, 3, False)
main.resizable(False, False)
main.configure(background="#e0e0e0")

initiate_grid(main)

r_, c_ = AliasTkFunctions.rows_.get, AliasTkFunctions.columns_.get

if not exists("saves.json") or not open("saves.json").read().strip():
    dump([], open("saves.json", "w"))

sort_type = StringVar(value="Recent")

mixer.init()


def saves_parser(dct):
    for key, value in dct.items():
        if key in ["last_opened"]:
            try:
                dct[key] = datetime.fromisoformat(value)
            except (ValueError, TypeError):
                pass
    return dct


saves = load(open("saves.json"), object_hook=saves_parser)

saves = sorted(saves, key=lambda x: x["last_opened"], reverse=True)

main.protocol("WM_DELETE_WINDOW", lambda: (Saves.save(), main.destroy()))


def settings_parser(dct):
    for key, value in dct.items():
        if key in ["startup", "resolution"]:
            try:
                dct[key] = StringVar(value=value)
            except (ValueError, TypeError):
                pass

        if key in ["fullscreen"]:
            try:
                dct[key] = StringVar(value=value)
            except (ValueError, TypeError):
                pass
    return dct


if not exists("settings.json") or not open("settings.json").read().strip():
    dump({}, open("settings.json", "w"))

settings = load(open("settings.json"), object_hook=settings_parser)

if "startup" not in settings:
    settings.update({"startup": StringVar(value="Home")})

resolutions = [
    "640x360",
    "960x540",
    "1280x720",
    "1600x900",
    "1920x1080"
]

if "resolution" not in settings:
    settings.update({"resolution": StringVar(value=resolutions[0])})

if "fullscreen" not in settings:
    settings.update({"fullscreen": BooleanVar(value=False)})

main.attributes("-fullscreen", settings["fullscreen"].get())


class Show:
    @staticmethod
    def saves():
        global saves

        grid(1, 2)
        main.columnconfigure(0, weight=0)
        Show.tabs("saves", row=0, column=0, sticky="ns")

        frame = ScrollableFrame(main, horizontal_scrollbar=False, row=0, column=1, sticky="nsew")
        frame.configure(padx=100, pady=20, background="#e0e0e0")

        bf = Frame(frame, background=frame.cget("background"))  # Haha, bf, boyfriend
        bf.pack()

        Label(bf, text="Sort by", background=frame.cget("background")).pack(side="left", padx=(0, 5))
        OptionMenu(bf, sort_type, sort_type.get(), *["Recent", "Name"], command=lambda _: Show.saves()).pack(
            side="left")
        Style().configure("TMenubutton", background=frame.cget("background"))

        bf = Frame(frame, background=frame.cget("background"))
        bf.pack(fill="x", pady=(10, 0))

        Button(bf, text="New save", command=Show.new_game, foreground="#cc0000", activeforeground="#cc0000").pack(
            fill="x", side="left", expand=True)
        Button(bf, text="🗑", command=lambda: Saves.delete_save(range(len(saves))), width=3, foreground="#cc0000",
               activeforeground="#cc0000").pack(side="left", padx=(10, 0))

        saves = sorted(saves, key=lambda x: x["last_opened"], reverse=True) if sort_type.get() == "Recent" else \
            sorted(saves, key=lambda x: x["name"])

        for i, f in enumerate(saves):
            bf = Frame(frame, background=frame.cget("background"))
            bf.pack(fill="x", pady=(10, 0))

            button = Button(bf, text=f"{f["save_name"]}", command=lambda j=i: Saves.continue_save(j))
            button.pack(fill="x", side="left", expand=True)

            tooltip = f"Name: {f["name"]}\nDifficulty: {f["difficulty"]}\nLast opened: {
                      time_ago(f["last_opened"])}"
            ToolTip(button, tooltip, x_offset=0, y_offset=30, wait_time=150, wraplength=300, follow_once=True)

            Button(bf, text="🗑", command=lambda j=i: Saves.delete_save([j]), width=3).pack(side="left", padx=(10, 0))

    @staticmethod
    def new_game():
        grid(3, 2)
        main.columnconfigure(0, weight=0)
        Show.tabs(row=0, rowspan=r_(), column=0, sticky="ns")

        player_name = StringVar(value="Player")

        def validate_input():
            value = player_name.get().replace(" ", "-")

            # noinspection SpellCheckingInspection
            allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
            filtered_value = "".join(c for c in value if c in allowed_chars)

            if len(filtered_value) > 16:
                filtered_value = filtered_value[:16]

            player_name.set(filtered_value)

        player_name.trace("w", lambda *_: validate_input())

        name_entry = Entry(textvariable=player_name, justify="center", width=26)
        name_entry.grid(row=0, column=1, columnspan=c_() - 1)
        name_entry.bind("<Control-BackSpace>", lambda _: player_name.set(value=""))

        frame = Frame(background="#e0e0e0")
        frame.grid(row=1, column=1)
        Label(frame, text="Select a difficulty", background=frame.cget("background")).pack()

        difficulty_var = IntVar(value=3)
        Scale(frame, from_=1, to=9, orient="horizontal", background=frame.cget("background"),
              highlightbackground=frame.cget("background"), variable=difficulty_var, length=150, width=17).pack()

        def finalise_new_game():
            name = player_name.get().strip() if player_name.get().strip() else f"Save {len(saves) + 1}"
            unformatted_name = name

            existing_names = [i["save_name"] for i in saves]

            if name in existing_names:
                counter = 2
                new_name = name
                while new_name in existing_names:
                    new_name = f"{name} ({counter})"
                    counter += 1
                name = new_name

            saves.append({"save_name": name, "last_opened": datetime.now(), "name": unformatted_name,
                          "difficulty": difficulty_var.get()})

            Saves.continue_save(len(saves) - 1)

        Button(text="Save character", command=finalise_new_game).grid(row=r_() - 1, column=1, columnspan=c_() - 1)

    @staticmethod
    def home():
        global saves

        grid(2, 2)
        main.columnconfigure(0, weight=0)
        Show.tabs("home", row=0, rowspan=r_(), column=0, sticky="ns")

        Label(text="Title", anchor="s", pady=5, font="TkDefaultFont 18", background="#e0e0e0").grid(row=0, column=1,
                                                                                                    sticky="nsew")

        Label(text="Subtitle", anchor="n", pady=5, font="TkDefaultFont 12", background="#e0e0e0").grid(row=1, column=1,
                                                                                                       sticky="nsew")

    @staticmethod
    def tabs(menu=None, **kwargs):
        option_frame = Frame(background="#d0d0d0", padx=5)
        option_frame.ignore_update_bg = True
        option_frame.grid(**kwargs)

        if len(current_player_data) > 0:
            Button(option_frame, text="✨", width=3, command=Show.main_menu, foreground="#faca0c",
                   activeforeground="#faca0c", state="disabled" if menu == "main_menu" else "normal").pack(side="top",
                                                                                                           pady=(5, 0))

            Button(option_frame, text="🎴", width=3, command=Show.skill_tree, foreground="#b857d9",
                   activeforeground="#b857d9", state="disabled" if menu == "skill_tree" else "normal").pack(side="top",
                                                                                                            pady=(5, 0))

            Button(option_frame, text="⚙️", width=3, command=Show.settings, foreground="#202020",
                   state="disabled" if menu == "game_settings" else "normal",
                   activeforeground="#202020").pack(side="top", pady=(5, 0))

            # noinspection SpellCheckingInspection
            Button(option_frame, text="🌐", width=3, command=lambda:
                   w_open("https://www.github.com/AbnormalNormality/Wip-Roguelite/"), foreground="#83cbff",
                   activeforeground="#83cbff").pack(side="top", pady=(5, 0))

            def close_save():
                global current_player_data
                Saves.save()
                current_player_data = {}
                Show.saves()

            Button(option_frame, text="⬅", width=3, command=close_save, foreground="#ff0000",
                   activeforeground="#ff0000").pack(side="bottom", pady=(0, 5))

        else:
            Button(option_frame, text="🏠", width=3, command=Show.home, foreground="#cc0000",
                   state="disabled" if menu == "home" else "normal", activeforeground="#cc0000").pack(side="top",
                                                                                                      pady=(5, 0))

            Button(option_frame, text="💾", width=3, command=Show.saves, foreground="#1750eb",
                   state="disabled" if menu == "saves" else "normal", activeforeground="#1750eb").pack(side="top",
                                                                                                       pady=(5, 0))

            Button(option_frame, text="⚙️", width=3, command=Show.settings, foreground="#202020",
                   state="disabled" if menu == "settings" else "normal", activeforeground="#202020").pack(side="top",
                                                                                                          pady=(5, 0))

            # noinspection SpellCheckingInspection
            Button(option_frame, text="🌐", width=3, command=lambda:
                   w_open("https://www.github.com/AbnormalNormality/Wip-Roguelite/"), foreground="#83cbff",
                   activeforeground="#83cbff").pack(side="top", pady=(5, 0))

            Button(option_frame, text="❌", width=3, command=lambda: (Saves.save(), main.destroy()),
                   foreground="#ff0000", activeforeground="#ff0000").pack(side="bottom", pady=(0, 5))

    @staticmethod
    def settings():
        grid(1, 2)
        main.columnconfigure(0, weight=0)

        if len(current_player_data) > 0:
            Show.tabs("game_settings", row=0, rowspan=r_(), column=0, sticky="ns")
        else:
            Show.tabs("settings", row=0, column=0, sticky="ns")

        frame = ScrollableFrame(main, horizontal_scrollbar=False, row=0, column=1, sticky="nsew")
        frame.configure(pady=20, background="#e0e0e0", padx=20)

        bf = Frame(frame, background=frame.cget("background"))
        bf.pack(anchor="w")

        Label(bf, text="When opening the game, go to:", background=frame.cget("background")).pack(side="left")
        OptionMenu(bf, settings["startup"], settings["startup"].get(), *["Home", "Saves", "Settings",
                                                                         "Most Recent Game"]).pack(side="left")
        Style().configure("TMenubutton", background=frame.cget("background"))

        bf = Frame(frame, background=frame.cget("background"))
        bf.pack(pady=(10, 0), anchor="w")

        Label(bf, text="Resolution:", background=frame.cget("background")).pack(side="left")

        OptionMenu(bf, settings["resolution"], settings["resolution"].get(), *resolutions,
                   command=lambda _: update_resolution()).pack(side="left")
        Style().configure("TMenubutton", background=frame.cget("background"))

        bf = Frame(frame, background=frame.cget("background"))
        bf.pack(pady=(10, 0), anchor="w")

        Label(bf, text="Fullscreen:", background=frame.cget("background")).pack(side="left", padx=(0, 5))

        Checkbutton(bf, variable=settings["fullscreen"],
                    command=lambda: main.attributes("-fullscreen", settings["fullscreen"].get())).pack(side="left")
        Style().configure("TCheckbutton", background=frame.cget("background"))

    @staticmethod
    def main_menu():
        grid(2, 2)
        main.columnconfigure(0, weight=0)
        Show.tabs("main_menu", row=0, rowspan=r_(), column=0, sticky="ns")

        Label(text=current_player_data["name"], font="TkDefaultFont 14",
              background=main.cget("background")).grid(row=0, column=1)

        Button(text=" Set out ").grid(row=r_() - 1, column=1)

    @staticmethod
    def skill_tree():
        grid(1, 2)
        main.columnconfigure(0, weight=0)
        Show.tabs("skill_tree", row=0, rowspan=r_(), column=0, sticky="ns")

        frame = ScrollableFrame(main, horizontal_scrollbar=False, row=0, column=1, sticky="nsew")
        frame.configure(pady=20, background="#e0e0e0", padx=20)


class Saves:
    @staticmethod
    def delete_save(i):
        if len(i) > 1 and not askokcancel(f"{main.title()}", "Are you sure you want to delete all saves?"):
            return

        elif len(i) == 1 and not askokcancel(main.title(), "Are you sure you want to the delete this save?"):
            return

        for i in reversed(sorted(i)):
            saves.pop(i)
        Show.saves()

    @staticmethod
    def save():
        def saves_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError("Type not serializable")

        dump(saves, open("saves.json", "w"), default=saves_serializer)

        def settings_serializer(obj):
            if isinstance(obj, StringVar):
                return obj.get()

            if isinstance(obj, BooleanVar):
                return bool(obj.get())

            raise TypeError("Type not serializable")

        dump(settings, open("settings.json", "w"), default=settings_serializer)

    @staticmethod
    def continue_save(i):
        global current_player_data

        player_data = saves[i]
        player_data.update({"last_opened": datetime.now()})
        current_player_data = player_data

        Show.saves()
        Show.main_menu()


def update_resolution():
    w, h = map(int, settings["resolution"].get().split(" ")[0].split("x"))

    if w == main.winfo_screenwidth() and h == main.winfo_screenheight():
        main.state("zoomed")
    else:
        main.state("normal")

    resize_window(main, w, h)


current_player_data = {}

update_resolution()

if settings["startup"].get().lower() == "most recent game":
    if len(saves) > 0:
        saves = sorted(saves, key=lambda x: x["last_opened"], reverse=True)
        Saves.continue_save(0)
    else:
        Show.saves()
else:
    exec(f"Show.{settings["startup"].get().lower()}()")

main.mainloop()
