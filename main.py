# main.py

import curses
from ui import UI
from storage import get_backend
from subcalendar import Subcalendar

def main(stdscr):
    storage = get_backend()
    ui = UI(stdscr, storage)

    subcalendars = storage.read_all()
    if not subcalendars:
        default = Subcalendar("default", 1)
        subcalendars.append(default)
        storage.write(default)

    running = True
    update_view = True

    stdscr.refresh()

    while running:
        if update_view:
            ui.draw_calendar_base()
            ui.draw_assignments(subcalendars)
            ui.mainwin.refresh()
            ui.update_counter += 1
            update_view = False

        ui.draw_cursor()

        running, update_view = ui.prompt(subcalendars)

    # save on exit (temporary)
    for cal in subcalendars:
        storage.write(cal)

if __name__ == "__main__":
    curses.set_escdelay(1)
    curses.wrapper(main)
