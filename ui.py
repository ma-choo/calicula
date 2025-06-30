# ui.py - input and visual calendar interface handling

"""
TODO:
functionality: 
implement functionality for navigating and selecting assignments
add support for toggling selected assignment completion
modify draw_assignments to draw completed assignments differently
show a pop-up assignment list for the selected day
hide/unhide subcalendars

optimization/refactoring:
add error handling when the subcalendars list is empty
refactor this and utils.py to optimize and get rid of unneeded functions. perhaps some things could be replaced with standard functions in date and datetime.
"""

import curses

from utils import (
    get_current_day, get_current_month, get_current_year,
    get_day_name, get_month_name, get_mon_name,
    get_days_in_month, zeller
)
from subcalendar import Assignment, Subcalendar

class UI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.screen_h, self.screen_w = self.stdscr.getmaxyx()

        self.mainwin_hfactor = (self.screen_h - 2) // 6
        self.mainwin_wfactor = (self.screen_w - 2) // 7
        self.mainwin_h = self.mainwin_hfactor * 6 + 1
        self.mainwin_w = self.mainwin_wfactor * 7 + 1
        self.mainwin_y = 0
        self.mainwin_x = 0

        self.promptwin_h = 1
        self.promptwin_w = self.screen_w
        self.promptwin_y = self.mainwin_h
        self.promptwin_x = 0

        self.reset_date_to_today()

        self.last_cursor_pos = None
        self.selected_subcal = 0
        self.msg = "calicula 0.01 - type :help for help"

        self.init_color_pairs()
        self.init_windows()

        self.HELP = """ Help
------

Navigation:
  h - left
  j - up
  k - down
  l - right

Subcalendars:
  c/C - cycle subcalendar selection
  v - toggle visibility of currently selected subcalendar
  :w - write and save all subcalendars

Assignments:
  :na - create new assignment within currently selected subcalendar
        """

    def reset_date_to_today(self):
        self.selected_date = type('Date', (), {})()  # lightweight object for day, month, year
        self.selected_date.day = get_current_day()
        self.selected_date.month = get_current_month()
        self.selected_date.year = get_current_year()
        self.first_day_offset = zeller(self.selected_date.month, self.selected_date.year)

    @property
    def selected_day(self):
        return self.selected_date.day

    @selected_day.setter
    def selected_day(self, val):
        self.selected_date.day = val

    @property
    def working_month(self):
        return self.selected_date.month

    @working_month.setter
    def working_month(self, val):
        self.selected_date.month = val

    @property
    def working_year(self):
        return self.selected_date.year

    @working_year.setter
    def working_year(self, val):
        self.selected_date.year = val

    def init_color_pairs(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_MAGENTA, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)
        curses.init_pair(3, curses.COLOR_CYAN, -1)
        curses.init_pair(4, curses.COLOR_BLUE, -1)
        curses.init_pair(5, curses.COLOR_YELLOW, -1)
        curses.init_pair(6, curses.COLOR_GREEN, -1)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLUE)

    def init_windows(self):
        self.mainwin = curses.newwin(self.mainwin_h, self.mainwin_w, self.mainwin_y, self.mainwin_x)
        self.promptwin = curses.newwin(self.promptwin_h, self.promptwin_w, self.promptwin_y, self.promptwin_x)

    def draw_calendar_base(self):
        self.mainwin.clear()
        for y in range(1, 6):
            self.mainwin.hline(self.mainwin_hfactor * y, 0, curses.ACS_HLINE, self.mainwin_w)
        for x in range(1, 7):
            self.mainwin.vline(0, self.mainwin_wfactor * x, curses.ACS_VLINE, self.mainwin_h)
        self.mainwin.box()
        for x in range(7):
            self.mainwin.addstr(0, x * self.mainwin_wfactor + 1, get_day_name(x))

        d, y, x = 1, 1, self.first_day_offset
        while d <= get_days_in_month(self.working_month):
            self.mainwin.addstr(y, 1 + x * self.mainwin_wfactor, f"{d:>{self.mainwin_wfactor - 1}}")
            if d == 1:
                self.mainwin.addstr(y, x * self.mainwin_wfactor + 1, get_mon_name(self.working_month))
            d += 1
            x += 1
            if x > 6:
                y += self.mainwin_hfactor
                x = 0
        
        month_name = get_month_name(self.working_month)
        self.mainwin.addstr(self.mainwin_h - 1, self.mainwin_w - 6 - len(month_name), f"{month_name}-{self.working_year}")
        self.mainwin.refresh()

    def draw_cursor(self):
        if self.last_cursor_pos: # TODO: this causes a bug when switching month where the date is left printed on the blank offset days
            prev_y, prev_x, prev_day = self.last_cursor_pos
            self.mainwin.addstr(prev_y, prev_x, f"{prev_day:>{self.mainwin_wfactor - 1}}")

        day_pos = self.selected_day - 1 + self.first_day_offset
        y = (day_pos // 7) * self.mainwin_hfactor + 1
        x = (day_pos % 7) * self.mainwin_wfactor + 1
        self.mainwin.attron(curses.A_REVERSE)
        self.mainwin.addstr(y, x, f"{self.selected_day:>{self.mainwin_wfactor - 1}}")
        self.mainwin.attroff(curses.A_REVERSE)
        self.mainwin.refresh()

        self.last_cursor_pos = (y, x, self.selected_day)

    """
    TODO:
    this function should take a LIST of subcalendars instead of the main function iterating through each subcalendar
    optimize it by instead of iterating through every assignment start from the working month and year
    need to add insert functionality to subcalendar class
    """
    def draw_assignments(self, calendar: Subcalendar):
        if calendar.hidden: return
        for assignment in calendar.assignments:
            if assignment.month - 1 == self.working_month:
                day_pos = assignment.day - 1 + self.first_day_offset
                y = (day_pos // 7) * self.mainwin_hfactor + 2
                x = (day_pos % 7) * self.mainwin_wfactor + 1

                while chr(self.mainwin.inch(y, x) & 0xFF) != ' ':
                    y += 1

                self.mainwin.attron(curses.color_pair(calendar.color))
                if assignment.completed:
                    self.mainwin.addstr(y, x, "✓ " + assignment.name[:self.mainwin_wfactor - 3])
                else:
                    self.mainwin.addstr(y, x, assignment.name[:self.mainwin_wfactor - 1])
                self.mainwin.attroff(curses.color_pair(calendar.color))
        self.mainwin.refresh()

    def change_date(self, delta: int) -> bool:
        self.selected_day += delta
        month_days = get_days_in_month(self.working_month)

        # forward one month
        if self.selected_day > month_days:
            self.selected_day -= month_days
            self.working_month += 1
            # forward one year
            if self.working_month > 11:
                self.working_month = 0
                self.working_year += 1
            self.first_day_offset = zeller(self.working_month, self.working_year)
            self.last_cursor_pos = None
            return True
        # backward one month
        elif self.selected_day < 1:
            self.working_month -= 1
            # backward one year
            if self.working_month < 0:
                self.working_month = 11
                self.working_year -= 1
            self.selected_day += get_days_in_month(self.working_month)
            self.first_day_offset = zeller(self.working_month, self.working_year)
            self.last_cursor_pos = None
            return True

        return False

    # prompt - handles input and whether to redraw the main window
    def prompt(self, subcalendars: list[Subcalendar]) -> tuple[bool, bool]:
        curses.curs_set(0)

        subcalendar = subcalendars[self.selected_subcal]

        self.promptwin.clear()
        try:
            self.promptwin.addstr(0, 0, self.msg)
            self.promptwin.attron(curses.color_pair(subcalendar.color))
            self.promptwin.addstr(0, self.mainwin_w - len(subcalendar.name), subcalendar.name)
            self.promptwin.attroff(curses.color_pair(subcalendar.color))
        except:
            self.promptwin.addstr(0, 0, "error")
        self.promptwin.clrtoeol()
        self.promptwin.refresh()

        update_view = False
        jump = 1
        running = True

        key = self.stdscr.getch()

        if key == ord(':'):
            curses.curs_set(1)
            command = ":"
            cursor_x = 1
            self.promptwin.clear()
            self.promptwin.addstr(0, 0, command)
            self.promptwin.refresh()

            while True:
                k = self.promptwin.getch()
                if k == 27:  # ESC
                    break
                elif k in (10, 13):  # Enter
                    if command == ":q": # quit
                        running = False
                    elif command == ":help": # help
                        self.mainwin.clear()
                        self.mainwin.addstr(self.HELP)
                        self.promptwin.clear()
                        self.promptwin.addstr(0, 0, "help - press any key to continue")
                        self.promptwin.refresh()
                        self.mainwin.refresh()
                        self.stdscr.getch()
                    elif command == ":w": # write
                        for cal in subcalendars:
                            cal.write()
                    elif command == ":na": # new assigment
                        self.promptwin.clear()
                        self.promptwin.addstr(0, 0, "new assignment: ")
                        curses.echo()
                        name = self.promptwin.getstr(0, 16, 50).decode('utf-8')
                        curses.noecho()

                        month = self.working_month + 1
                        day = self.selected_day
                        year = self.working_year
                        date = f"{month:02d}{day:02d}{year}"
                        try:
                            subcalendar.add_assignment(Assignment(name, date, 0))
                        except:
                            self.msg = "failed to create new assignment"
                        else:
                            self.promptwin.clear()
                            self.msg = f"added new assignment \"{name}\" in {subcalendar.name}"
                    else:
                        self.msg = f"unknown command {command}"
                    break
                elif k in (curses.KEY_BACKSPACE, 127, 8):
                    if len(command) > 1:
                        command = command[:-1]
                        cursor_x -= 1
                elif 32 <= k <= 126:
                    command += chr(k)
                    cursor_x += 1

                self.promptwin.clear()
                self.promptwin.addstr(0, 0, command)
                self.promptwin.refresh()

            return running, True

        # cycle subcalendars
        if key == ord('c'):
            self.selected_subcal = (self.selected_subcal + 1) % len(subcalendars)
            update_view = True
        elif key == ord('C'):
            self.selected_subcal = (self.selected_subcal - 1) % len(subcalendars)
            update_view = True

        if key == ord('v'):
            subcalendar.toggle_hidden()
            self.msg = f"{subcalendar.name} hidden = {subcalendar.hidden}"
            update_view = True

        # movement
        elif key in range(50, 59):  # 2–9 keys - TODO: jump doesn't seem to be working
            jump = key - 48
        elif key == ord('l'):
            update_view = self.change_date(1 * jump)
            jump = 1
        elif key == ord('h'):
            update_view = self.change_date(-1 * jump)
            jump = 1
        elif key == ord('j'):
            update_view = self.change_date(7 * jump)
            jump = 1
        elif key == ord('k'):
            update_view = self.change_date(-7 * jump)
            jump = 1
        else:
            update_view = False

        return running, update_view
