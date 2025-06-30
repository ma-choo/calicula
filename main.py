# main.py - main loop

import curses
from utils import init_current_time # TODO: is this doing anything?
from ui import UI
from subcalendar import Subcalendar

def main(stdscr):
    init_current_time() # TODO: is this doing anything?
    ui = UI(stdscr)
    stdscr.refresh()

    subcalendars = Subcalendar.read_all()

    running = True
    update_view = True

    while running:
        if update_view:
            ui.draw_calendar_base()
            for cal in subcalendars:
                ui.draw_assignments(cal)
            update_view = False

        ui.draw_cursor()

        running, update_view = ui.prompt(subcalendars)

if __name__ == "__main__":
    curses.wrapper(main)
