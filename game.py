from tkinter import *
from tkinter.messagebox import askokcancel
from tkinter.ttk import OptionMenu, Style, Checkbutton
from os.path import exists
from json import dump, load
from datetime import datetime
from pygame import mixer
from webbrowser import open as w_open

import AliasTkFunctions
from AliasTkFunctions import fix_resolution_issue, resize_window, initiate_grid, grid, ScrollableFrame

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

resolutions = ["640x360", "960x540", "1280x720", "1600x900", "1920x1080"]

if "resolution" not in settings:
    settings.update({"resolution": StringVar(value=resolutions[0])})

size = [int(a) for a in settings["resolution"].get().split("x")]
resize_window(main, size[0], size[1])

if "fullscreen" not in settings:
    settings.update({"fullscreen": BooleanVar(value=False)})

main.attributes("-fullscreen", settings["fullscreen"].get())


class Show:
    @staticmethod
    def saves():
        global saves

        grid(1, 2)
        main.columnconfigure(0, weight=0)
        Show.show_tabs("saves", row=0, column=0, sticky="ns")

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

            Button(bf, text=f"{f["name"]}", command=lambda j=i: Saves.continue_save(j)).pack(fill="x", side="left",
                                                                                             expand=True)
            Button(bf, text="🗑", command=lambda j=i: Saves.delete_save([j]), width=3).pack(side="left", padx=(10, 0))

    @staticmethod
    def new_game():
        grid(2, 2)
        main.columnconfigure(0, weight=0)
        Show.show_tabs(row=0, rowspan=r_(), column=0, sticky="ns")

        player_name = StringVar(value="Player")

        def validate_input():p
            value = player_name.get()

            # noinspection SpellCheckingInspection
            allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
            filtered_value = "".join(c for c in value if c in allowed_chars)

            if len(filtered_value) > 16:
                filtered_value = filtered_value[:16]

            player_name.set(filtered_value)

        player_name.trace("w", lambda *_: validate_input())

        Entry(textvariable=player_name, justify="center", width=26).grid(row=0, column=1, columnspan=c_() - 1)

        def finalise_new_game():
            name = player_name.get().strip() if player_name.get().strip() else f"Save {len(saves) + 1}"

            true_name = name

            existing_names = [i["name"] for i in saves]

            if name in existing_names:
                counter = 2
                new_name = name
                while new_name in existing_names:
                    new_name = f"{name} ({counter})"
                    counter += 1
                name = new_name

            saves.append({"name": name, "last_opened": datetime.now(), "true_name": true_name})

            Saves.continue_save(len(saves) - 1)

        Button(text="Save character", command=finalise_new_game).grid(row=r_() - 1, column=1, columnspan=c_() - 1)

    @staticmethod
    def home():
        global saves

        grid(2, 2)
        main.columnconfigure(0, weight=0)
        Show.show_tabs("home", row=0, rowspan=r_(), column=0, sticky="ns")

        Label(text="Title", anchor="s", pady=5, font="TkDefaultFont 18", background="#e0e0e0").grid(row=0, column=1,
                                                                                                    sticky="nsew")

        Label(text="Subtitle", anchor="n", pady=5, font="TkDefaultFont 12", background="#e0e0e0").grid(row=1, column=1,
                                                                                                       sticky="nsew")

    @staticmethod
    def show_tabs(menu=None, **kwargs):
        option_frame = Frame(background="#d0d0d0", padx=5)
        option_frame.ignore_update_bg = True
        option_frame.grid(**kwargs)

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

        Button(option_frame, text="❌", width=3, command=lambda: (Saves.save(), main.destroy()), foreground="#ff0000",
               activeforeground="#ff0000").pack(side="bottom", pady=(0, 5))

        mixer.music.stop()

    @staticmethod
    def settings():
        grid(1, 2)
        main.columnconfigure(0, weight=0)
        Show.show_tabs("settings", row=0, column=0, sticky="ns")

        frame = ScrollableFrame(main, horizontal_scrollbar=False, row=0, column=1, sticky="nsew")
        frame.configure(pady=20, background="#e0e0e0")

        bf = Frame(frame, background=frame.cget("background"))
        bf.pack()

        Label(bf, text="When opening the game, go to:", background=frame.cget("background")).pack(side="left")
        OptionMenu(bf, settings["startup"], settings["startup"].get(), *["Home", "Saves", "Settings"]).pack(side="left")
        Style().configure("TMenubutton", background=frame.cget("background"))

        bf = Frame(frame, background=frame.cget("background"))
        bf.pack(pady=(10, 0))

        Label(bf, text="Resolution:", background=frame.cget("background")).pack(side="left")

        OptionMenu(bf, settings["resolution"], settings["resolution"].get(), *resolutions,
                   command=lambda _: resize_window(main, int(settings["resolution"].get().split("x")[0]),
                                                   int(settings["resolution"].get().split("x")[1]))).pack(side="left")
        Style().configure("TMenubutton", background=frame.cget("background"))

        bf = Frame(frame, background=frame.cget("background"))
        bf.pack(pady=(10, 0))

        Label(bf, text="Fullscreen:", background=frame.cget("background")).pack(side="left", padx=(0, 5))

        Checkbutton(bf, variable=settings["fullscreen"],
                    command=lambda: main.attributes("-fullscreen", settings["fullscreen"].get())).pack(side="left")
        Style().configure("TCheckbutton", background=frame.cget("background"))


class Saves:
    @staticmethod
    def delete_save(i):
        if len(i) > 1 and not askokcancel("", "Are you sure you want to delete all saves?"):
            return

        elif len(i) < 2 and not askokcancel("", "Are you sure you want to the delete this save?"):
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
        saves[i].update({"last_opened": datetime.now()})
        print(saves[i])
        Show.saves()


exec(f"Show.{settings["startup"].get().lower()}()")

main.mainloop()
