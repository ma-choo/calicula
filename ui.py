# ui.py - input and visual calendar interface handling

"""
TODO:
functionality:
- allow assignments to span multiple dates
- implement a visual mode to create these types of assignments
- visual mode will also allow to select multiple dates in the day_popup function
- move assignment to a different date
- paste assignments?
- cw to rename assignments and subcalendars

optimization/refactoring:
- rename working month and year to selected month and year
"""

import curses

from utils import (
    contains_bad_chars,
    get_current_day, get_current_month, get_current_year,
    get_day_name, get_day_date_name, get_month_name, get_mon_name,
    get_days_in_month, zeller
)
from subcalendar import Assignment, Subcalendar
from datetime import date, datetime, timedelta

class UI:
    def __init__(self, stdscr, storage):
        self.stdscr = stdscr
        self.storage = storage

        # TODO: recalculate window sizes on terminal resize
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
        self.selected_subcal = 0 # NOTE: this is only an index, not a subcalendar object
        self.saved = True
        self.count = 1
        self.count_buffer = ""
        self.delta = 1
        self.operator = ''
        self.clipboard = [] # TODO: implement different registers like vim
        self.msg = "calicula 0.01 - type :help for help or :q for quit"

        self.update_counter = 0

        self.init_color_pairs()
        self.init_windows()

        self.HELP = """ HELP
------

Navigation
----------
h/←        Left (back one day)
j/↓        Down (forward one week)
k/↑        Up (backward one week)
l/→        Right (forward one day)
<Enter>    Show day popup for selected date

Set jump with number keys

Subcalendars
------------
[ ]        Cycle subcalendar selection
z          Toggle visibility of currently selected subcalendar
:nc        Create new subcalendar
:w         Write and save all subcalendars

Assignments
-----------
:A         Create new assignment on selected date within currently selected subcalendar
<Space>    Mark assignment as completed (within day popup)
d          Mark assignment for deletion (within day popup)
y          Yank assignment
p          Paste assignment

Quit
----
:q         Quit
:wq        Write and quit
:q!        Force quit
        """

    def reset_date_to_today(self):
        self.selected_date = type('Date', (), {})() # TODO: convert this to a proper datetime object?
        self.selected_date.day = get_current_day()
        self.selected_date.month = get_current_month()
        self.selected_date.year = get_current_year()
        self.first_day_offset = zeller(self.selected_date.month, self.selected_date.year)

    # getters and setters
    @property
    def selected_day(self):
        return self.selected_date.day

    @selected_day.setter
    def selected_day(self, val):
        self.selected_date.day = val

    @property
    def working_month(self):
        return self.selected_date.month

    @property
    def previous_month(self):
        return (self.selected_date.month - 1) % 12

    @property
    def next_month(self):
        return (self.selected_date.month + 1) % 12

    @working_month.setter
    def working_month(self, val):
        self.selected_date.month = val

    @property
    def working_year(self):
        return self.selected_date.year

    @working_year.setter
    def working_year(self, val):
        self.selected_date.year = val

    # TODO: add ability to implement custom color schemes from a config file
    def init_color_pairs(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_MAGENTA, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)
        curses.init_pair(3, curses.COLOR_CYAN, -1)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)
        curses.init_pair(5, curses.COLOR_GREEN, -1)
        curses.init_pair(6, curses.COLOR_BLUE, -1) # dim
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLUE) # current day highlight

    def init_windows(self):
        self.mainwin = curses.newwin(self.mainwin_h, self.mainwin_w, self.mainwin_y, self.mainwin_x)
        self.promptwin = curses.newwin(self.promptwin_h, self.promptwin_w, self.promptwin_y, self.promptwin_x)

    def draw_calendar_base(self):
        self.mainwin.erase()
        # 5 horizontal lines (6 columns of days)
        for y in range(1, 6):
            self.mainwin.hline(self.mainwin_hfactor * y, 0, curses.ACS_HLINE, self.mainwin_w)
        # 6 vertical lines (7 columns of weeks)
        for x in range(1, 7):
            self.mainwin.vline(0, self.mainwin_wfactor * x, curses.ACS_VLINE, self.mainwin_h)
        # border and day headers
        self.mainwin.box()
        for x in range(7):
            self.mainwin.addstr(0, x * self.mainwin_wfactor + 1, get_day_name(x))

        # day numbers for previous month
        if self.first_day_offset > 0:
            self.mainwin.attron(curses.color_pair(6))  # blue for dim # TODO add proper dim and use blue as a fallback

            prev_month = self.previous_month
            prev_year = self.working_year if self.working_month > 0 else self.working_year - 1
            last_day_prev_month = get_days_in_month(prev_month, prev_year)

            for i in range(self.first_day_offset - 1, -1, -1):
                day = last_day_prev_month - (self.first_day_offset - 1 - i)
                y = 1
                x = i * self.mainwin_wfactor + 1
                self.mainwin.addstr(y, x, f"{day:>{self.mainwin_wfactor - 1}}")

            self.mainwin.attroff(curses.color_pair(6))

        # day numbers for selected month
        d, y, x = 1, 1, self.first_day_offset
        while d <= get_days_in_month(self.working_month):
            self.mainwin.addstr(y, 1 + x * self.mainwin_wfactor, f"{d:>{self.mainwin_wfactor - 1}}")
            d += 1
            x += 1
            if x > 6:
                y += self.mainwin_hfactor
                x = 0

        # TODO: day numbers for following month
        
        # month and year on bottom right
        month_name = get_month_name(self.working_month)
        self.mainwin.addstr(self.mainwin_h - 1, self.mainwin_w - 6 - len(month_name), f"{month_name}-{self.working_year}")

    def draw_cursor_old(self):
        if self.last_cursor_pos:
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

    # draw selection cursor and highlight current date TODO: maybe make this two separate functions?
    def draw_cursor(self):
        today = date.today()
        today_is_visible = (
            today.year == self.working_year and
            today.month == self.working_month + 1
        )

        # redraw the cell where the cursor used to be
        if self.last_cursor_pos:
            prev_y, prev_x, prev_day = self.last_cursor_pos
            is_today = (
                today_is_visible and
                today.day == prev_day
            )

            if is_today:
                self.mainwin.attron(curses.color_pair(7))
            self.mainwin.addstr(prev_y, prev_x, f"{prev_day:>{self.mainwin_wfactor - 1}}")
            if is_today:
                self.mainwin.attroff(curses.color_pair(7))

        # highlight today's date (unless it's the selected one)
        if today_is_visible and today.day != self.selected_day:
            day_pos = today.day - 1 + self.first_day_offset
            y = (day_pos // 7) * self.mainwin_hfactor + 1
            x = (day_pos % 7) * self.mainwin_wfactor + 1
            self.mainwin.attron(curses.color_pair(7))
            self.mainwin.addstr(y, x, f"{today.day:>{self.mainwin_wfactor - 1}}")
            self.mainwin.attroff(curses.color_pair(7))

        # draw the current cursor
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
    - optimize it by instead of iterating through every assignment start from the working month and year
    - need to add insert functionality to subcalendar class
    - show assignments from day cells outside of the selected month
    - month caching?
    """
    def draw_assignments(self, subcalendars: list[Subcalendar]):
        max_per_day = self.mainwin_hfactor - 2  # dynamic limit per cell height
        day_map = {}

        # group assignments by (year, month, day)
        for cal in subcalendars:
            if cal.hidden:
                continue
            for a in cal.assignments:
                if a.year == self.working_year and a.month - 1 == self.working_month:
                    key = a.day
                    day_map.setdefault(key, []).append((cal, a))
                elif a.year > self.working_year or \
                    (a.year == self.working_year and a.month - 1 > self.working_month):
                    break  # Assignments are sorted

        for day, assignments in day_map.items():
            day_pos = day - 1 + self.first_day_offset
            base_y = (day_pos // 7) * self.mainwin_hfactor + 2
            x = (day_pos % 7) * self.mainwin_wfactor + 1

            limit = max_per_day
            if len(assignments) > max_per_day:
                limit -= 1  # reserve space for "+N more"

            for i, (cal, a) in enumerate(assignments[:limit]):
                y = base_y + i
                try:
                    self.mainwin.attron(curses.color_pair(cal.color))
                    if a.completed:
                        self.mainwin.addstr(y, x, "✓ " + a.name[:self.mainwin_wfactor - 3])
                    else:
                        self.mainwin.addstr(y, x, a.name[:self.mainwin_wfactor - 1])
                    self.mainwin.attroff(curses.color_pair(cal.color))
                except:
                    pass  # prevent drawing errors

            if len(assignments) > limit:
                y = base_y + limit
                more = len(assignments) - limit
                self.mainwin.addstr(y, x, f"+{more} more")

        self.mainwin.refresh()

    """
    TODO:
    - cw to rename assignments
    - fix divide by zero error on scrolling in date with no assignments
    - gg and G go to top and bottom of list
    - fix screen flicker on close
    - y and d add assignments to clipboard_buffer
    - should also be able to cycle subcalendars from this view
    """
    def show_day_popup(self, subcalendars: list[Subcalendar]):
        popup_h = min(10, self.mainwin_hfactor + 1)
        popup_w = self.mainwin_w
        popup_x = self.mainwin_x

        # compute popup_y based on selected day's screen position
        day_pos = self.selected_day - 1 + self.first_day_offset
        cursor_y = (day_pos // 7) * self.mainwin_hfactor + 1
        popup_y = min(self.screen_h - popup_h, self.mainwin_y + cursor_y - 1)

        popup = curses.newwin(popup_h, popup_w, popup_y, popup_x)
        popup.keypad(True)

        self.promptwin.erase()
        self.promptwin.addstr(0, 0, "<Space>: mark complete    d: delete    y: yank")
        self.promptwin.refresh()

        # gather assignments for the selected day
        assignments = []
        for cal in subcalendars:
            if cal.hidden:
                continue
            for a in cal.assignments:
                if a.day == self.selected_day and a.month == self.working_month + 1 and a.year == self.working_year:
                    assignments.append((cal, a))
        """
        TODO: this avoids the divide by zero issues on scroll,
        but intuitively i still want to see the day popup on an empty day and add assignments from there.
        """
        if not assignments: 
            return

        selected = 0
        top = 0
        to_delete = set()
        clipboard_buffer = []

        # get the day name to show in the header
        day_date = datetime(self.working_year, self.working_month + 1, self.selected_day)
        day_name = get_day_date_name(day_date)

        while True:
            popup.erase()
            popup.border()
            popup.addstr(0, 2, f" {day_name}-{self.working_month + 1}-{self.selected_day}-{self.working_year} ")

            view_limit = popup_h - 2
            bottom = min(top + view_limit, len(assignments))

            # scroll indicators
            if top > 0:
                popup.addstr(1, popup_w - 3, "▲")
            if bottom < len(assignments):
                popup.addstr(popup_h - 2, popup_w - 3, "▼")

            # draw assignments
            for i in range(top, bottom):
                y = i - top + 1
                cal, assignment = assignments[i]

                # TODO: yank and delete markers should be after the check mark
                prefix = "✓ " if assignment.completed else "  "
                if assignment in clipboard_buffer:
                    prefix = "y "
                if assignment in to_delete:
                    prefix = "✗ "

                try:
                    popup.attron(curses.color_pair(cal.color))
                    if i == selected:
                        popup.attron(curses.A_REVERSE)
                    popup.addstr(y, 2, f"{prefix}{assignment.name[:popup_w - 4]}")
                    if i == selected:
                        popup.attroff(curses.A_REVERSE)
                    popup.attroff(curses.color_pair(cal.color))
                except:
                    pass

            popup.refresh()
            key = popup.getch()

            if key in (ord('j'), curses.KEY_DOWN):
                if selected < len(assignments) - 1:
                    selected += 1
                    if selected >= top + view_limit:
                        top += 1
            elif key in (ord('k'), curses.KEY_UP):
                if selected > 0:
                    selected -= 1
                    if selected < top:
                        top -= 1

            elif key == ord(' '):  # toggle completion
                assignments[selected][1].toggle_completion()
                self.saved = False

            elif key == ord('A'):
                added = self.new_assignment(subcalendars, self.selected_day, self.working_month + 1, self.working_year)
                if added:
                    assignments = []
                    for cal in subcalendars:
                        if cal.hidden:
                            continue
                        for a in cal.assignments:
                            if a.day == self.selected_day and a.month == self.working_month + 1 and a.year == self.working_year:
                                assignments.append((cal, a))
                    selected = 0
                    top = 0

            elif key == ord('d'):  # mark/unmark for deletion
                a = assignments[selected][1]
                if a in to_delete:
                    to_delete.remove(a)
                else:
                    to_delete.add(a)

            elif key == ord('y'):  # yank (toggle in clipboard)
                a = assignments[selected][1]
                if a in clipboard_buffer:
                    clipboard_buffer.remove(a)
                else:
                    clipboard_buffer.append(a)

            elif key == ord('p'):  # paste assignment(s) TODO modularize this into a function so that it can be accessed from the prompt
                if not self.clipboard:
                    self.msg = "Clipboard is empty"
                    continue

                subcalendar = subcalendars[self.selected_subcal]
                count = 0

                for original in self.clipboard:
                    # clone the assignment
                    try:
                        cloned_date = f"{self.working_year}{self.working_month + 1:02d}{self.selected_day:02d}"
                        cloned = Assignment(original.name, cloned_date, original.completed)

                        subcalendar.insert_assignment(cloned)
                        count += 1
                    except Exception as e:
                        self.msg = f"Paste error: {e}"
                        continue

                if count > 0:
                    self.msg = f"Pasted {count} assignments to {subcalendar.name}"
                    self.saved = False

                # refresh assignment list after paste
                assignments = []
                for cal in subcalendars:
                    if cal.hidden:
                        continue
                    for a in cal.assignments:
                        if a.day == self.selected_day and a.month == self.working_month + 1 and a.year == self.working_year:
                            assignments.append((cal, a))
                # selected = 0
                # top = 0

            elif key in (10, 13):  # enter – confirm deletion and set clipboard
                if to_delete:
                    popup.addstr(popup_h - 2, 2, "Delete marked assignments? (y/n) ")
                    popup.clrtoeol()
                    popup.refresh()
                    confirm = popup.getch()
                    if confirm == ord('y'):
                        # add to_delete to clipboard_buffer if not already in
                        for a in to_delete:
                            if a not in clipboard_buffer:
                                clipboard_buffer.append(a)
                        for cal in subcalendars:
                            cal.assignments = [a for a in cal.assignments if a not in to_delete]
                        self.saved = False

                # update main clipboard
                self.clipboard = clipboard_buffer.copy()
                break

            elif key == 27:  # ESC
                self.clipboard = clipboard_buffer.copy()
                break

        del popup
        self.stdscr.touchwin()

    def new_assignment(self, subcalendars, day, month, year) -> bool:
        subcalendar = subcalendars[self.selected_subcal]

        curses.curs_set(1)
        self.promptwin.erase()
        self.promptwin.addstr(0, 0, "New assignment: ")
        curses.echo()
        try:
            name = self.promptwin.getstr(0, 16, 50).decode('utf-8').strip()
        finally:
            curses.noecho()
            curses.curs_set(0)

        if not name: # TODO: this doesn't seem to work
            self.msg = "Error: assignment name cannot be blank"
            return False

        if contains_bad_chars(name): # TODO: don't need to do this necessarily for assignments. implement proper csv handling so assignment names are wrapped in quotation marks
            self.msg = "Error: assignment name contains forbidden characters"
            return False

        self.promptwin.erase()
        self.promptwin.addstr(0, 0, "Study time: ")
        curses.echo()
        try:
            input_str = self.promptwin.getstr(0, 30, 10).decode('utf-8').strip()
        finally:
            curses.noecho()
            curses.curs_set(0)

        try:
            studytime = int(input_str) if input_str else 0
        except ValueError:
            studytime = 0

        date_str = f"{year}{month:02d}{day:02d}"

        try:
            subcalendar.insert_assignment(Assignment(name, date_str, 0, studytime))
        except Exception as e:
            self.msg = f"Failed to create new assignment: {e}"
            return False
        else:
            self.msg = f"Created new assignment '{name}' in {subcalendar.name}"
            self.saved = False
            return True

    def change_date(self, delta: int) -> bool: # TODO: rename to move_date, to compliment a new set_date fuction
        self.delta = delta
        current = date(self.working_year, self.working_month + 1, self.selected_day)
        new_date = current + timedelta(days=delta)

        month_changed = (new_date.month - 1) != self.working_month or new_date.year != self.working_year

        self.selected_day = new_date.day
        self.working_month = new_date.month - 1  # zero-based
        self.working_year = new_date.year
        if month_changed:
            self.first_day_offset = zeller(self.working_month, self.working_year)
            self.last_cursor_pos = None

        return month_changed  # redraw only if month or year changed

    from datetime import timedelta

    # TODO: optimize this by only calling this when the week changes
    def get_selected_week_start(self) -> date:
        selected = date(self.working_year, self.working_month + 1, self.selected_day)
        return selected - timedelta(days=selected.weekday())  # monday?

    def sum_studytime_for_week(self, subcalendars, selected_week_start):
        week_end = selected_week_start + timedelta(days=6)
        total_minutes = 0

        for subcal in subcalendars:
            if subcal.hidden:
                continue
            for a in subcal.assignments:
                if selected_week_start <= a.date <= week_end:
                    total_minutes += a.studytime

        return total_minutes


    # prompt - handles input and returns two booleans to redraw the main window and continue the main loop
    def prompt(self, subcalendars: list[Subcalendar]) -> tuple[bool, bool]:
        curses.curs_set(0)
        subcalendar = subcalendars[self.selected_subcal]

        selected_week_start = self.get_selected_week_start()
        study_minutes = self.sum_studytime_for_week(subcalendars, selected_week_start)

        status = f"{'[+]' if not self.saved else ''}{f"  {self.operator} " if self.operator else ' '} {self.storage.name}  study time: {study_minutes}  {self.update_counter}  {self.count_buffer if self.count_buffer else self.delta}  {'[H]' if subcalendar.hidden else ''}{subcalendar.name}"

        self.promptwin.erase()
        try:
            self.promptwin.addstr(0, 0, self.msg)
            self.promptwin.attron(curses.color_pair(subcalendar.color))
            self.promptwin.addstr(0, self.mainwin_w - len(status), status)
            self.promptwin.attroff(curses.color_pair(subcalendar.color))
        except Exception as e:
            self.promptwin.addstr(0, 0, f"Error: {e}")
        self.promptwin.clrtoeol()
        self.promptwin.refresh()

        update_view = False
        running = True

        key = self.stdscr.getch()

        # enter command mode
        if key == ord(':'):
            curses.curs_set(1)
            command = ":"
            cursor_x = 1
            self.promptwin.erase()
            self.promptwin.addstr(0, 0, command)
            self.promptwin.refresh()

            while True:
                k = self.promptwin.getch()
                if k == 27:  # esc
                    break
                elif k in (10, 13):  # enter
                    if command == ":q": # quit
                        if not self.saved:
                            self.msg = "Error: no write since last change. Use :q! to force quit"
                        else:
                            running = False

                    elif command == ":q!": # force quit
                        running = False

                    elif command == ":help": # help
                        curses.curs_set(0)
                        self.mainwin.erase()
                        self.mainwin.addstr(self.HELP)
                        self.promptwin.erase()
                        self.promptwin.addstr(0, 0, "Help - press any key to continue")
                        self.promptwin.refresh()
                        self.mainwin.refresh()
                        self.stdscr.getch()

                    elif command == ":w": # write
                        for cal in subcalendars:
                            self.storage.write(cal)
                        self.msg = "Changes saved"
                        self.saved = True

                    elif command == ":wq": # write quit
                        for cal in subcalendars:
                            self.storage.write(cal)
                        self.msg = "Changes saved"
                        self.saved = True
                        running = False

                    elif command == ":nc":  # new subcalendar
                        self.promptwin.erase()
                        self.promptwin.addstr(0, 0, "New subcalendar name: ")
                        curses.echo()
                        name = self.promptwin.getstr(0, 22, 50).decode('utf-8').strip()
                        curses.noecho()

                        if name:
                            if contains_bad_chars(name):
                                self.msg = "Error: subcalendar name contains forbidden characters"
                            elif any(c.name == name for c in subcalendars):
                                self.msg = f"Error: Subcalendar '{name}' already exists"
                            else:
                                # ask for color index (1–5)
                                self.promptwin.erase()
                                self.promptwin.addstr(0, 0, "Choose color: ")
                                for c in range(1, 6):
                                    self.promptwin.attron(curses.color_pair(c))
                                    self.promptwin.addstr(f"{c} ")
                                    self.promptwin.attroff(curses.color_pair(c))
                                self.promptwin.refresh()
                                while True:
                                    key = self.promptwin.getch()
                                    if ord('1') <= key <= ord('5'):
                                        color = key - ord('0')
                                        break
                                    elif key == 27:  # esc to cancel
                                        self.msg = "Subcalendar creation canceled"
                                        return True, True

                                new_cal = Subcalendar(name, color)
                                subcalendars.append(new_cal)
                                self.selected_subcal = len(subcalendars) - 1
                                self.msg = f"Created Subcalendar '{name}'"
                                self.saved = False
                        else:
                            self.msg = f"Error: invalid name: {name}"

                    elif command == ":color":
                        self.promptwin.erase()
                        self.promptwin.addstr(0, 0, f"Choose color for '{subcalendar.name}': ")
                        for c in range(1, 6):
                            self.promptwin.attron(curses.color_pair(c))
                            self.promptwin.addstr(f"{c} ")
                            self.promptwin.attroff(curses.color_pair(c))
                        self.promptwin.refresh()

                        while True:
                            key = self.promptwin.getch()
                            if ord('1') <= key <= ord('5'):
                                color = key - ord('0')
                                subcalendar.change_color(color)
                                self.promptwin.erase()
                                self.msg = f"Color changed for {subcalendar.name}"
                                return True, True
                            elif key == 27:  # ESC to cancel
                                break

                    else:
                        self.msg = f"Unknown command: {command}"
                    break

                elif k in (curses.KEY_BACKSPACE, 127, 8):
                    if len(command) > 1:
                        command = command[:-1]
                        cursor_x -= 1
                elif 32 <= k <= 126: # TODO: what is this?
                    command += chr(k)
                    cursor_x += 1

                self.promptwin.erase()
                self.promptwin.addstr(0, 0, command)
                self.promptwin.refresh()

            return running, True

        # cycle subcalendars
        elif key == ord('['):
            self.selected_subcal = (self.selected_subcal - 1) % len(subcalendars)
            self.promptwin.refresh()
        elif key == ord(']'):
            self.selected_subcal = (self.selected_subcal + 1) % len(subcalendars)
            self.promptwin.refresh()

        # TODO: if operator = 'd' remove selected subcalendar

        # change operator
        elif key == ord('c'):
            if not self.operator == 'c':
                self.operator = 'c'
        
        # TODO: this duplicates subcalendars on write
        elif key == ord('w'):
            if self.operator == 'c':
                self.promptwin.erase()
                self.promptwin.addstr(0, 0, "Rename subcalendar: ")
                curses.echo()
                name = self.promptwin.getstr(0, 22, 50).decode('utf-8').strip()
                curses.noecho()

                if name:
                    if contains_bad_chars(name):
                        self.msg = "Error: subcalendar name contains forbidden characters"
                    elif any(c.name == name for c in subcalendars):
                        self.msg = f"Error: Subcalendar '{name}' already exists"
                    else:
                        self.promptwin.erase()

                        old_name = subcalendar.name
                        subcalendar.rename(name)

                        if old_name != name:
                            self.storage.rename(old_name, name)

                        self.msg = f"Renamed Subcalendar '{name}'"
                        self.saved = False


        # toggle calendar visibility
        elif key == ord('z'):
            subcalendar.toggle_hidden()
            self.msg = f"{subcalendar.name} {'hidden' if subcalendar.hidden else 'unhidden'}"
            update_view = True

        elif key in (10, 13): # enter
            self.show_day_popup(subcalendars)
            self.stdscr.touchwin()
            self.stdscr.refresh()
            update_view = True

        # new assignment
        elif key == ord('A'):
            added = self.new_assignment(subcalendars, self.selected_day, self.working_month + 1, self.working_year)
            if added:
                update_view = True

        # navigation
        elif key in (ord('l'), curses.KEY_RIGHT):
            self.count = int(self.count_buffer) if self.count_buffer else 1
            update_view = self.change_date(1 * self.count)
            self.count_buffer = ""
        elif key in (ord('h'), curses.KEY_LEFT):
            self.count = int(self.count_buffer) if self.count_buffer else 1
            update_view = self.change_date(-1 * self.count)
            self.count_buffer = ""
        elif key in (ord('j'), curses.KEY_DOWN):
            self.count = int(self.count_buffer) if self.count_buffer else 1
            update_view = self.change_date(7 * self.count)
            self.count_buffer = ""
        elif key in (ord('k'), curses.KEY_UP):
            self.count = int(self.count_buffer) if self.count_buffer else 1
            update_view = self.change_date(-7 * self.count)
            self.count_buffer = ""

        elif ord('0') <= key <= ord('9'):
            self.count_buffer += chr(key)

        # TODO: build commands here and pass them to a command function?

        elif key == ord('g'): # TODO: modularize this to a set_date() function that takes a date string to make this section less messy
            if not self.operator == 'g': # first g press
                self.operator = 'g'
            elif self.operator == 'g': # second g press (gg)
                # <date> + gg - jump to specified date
                if len(self.count_buffer) == 8: # 8 digits: jump to MMDDYYYY
                    try:
                        month = int(self.count_buffer[:2])
                        day = int(self.count_buffer[2:4])
                        year = int(self.count_buffer[4:])
                        new_date = date(year, month, day)

                        self.selected_day = new_date.day
                        self.working_month = new_date.month - 1
                        self.working_year = new_date.year
                        self.first_day_offset = zeller(self.working_month, self.working_year)
                        self.last_cursor_pos = None
                        
                        self.msg = f"jumped to {month:02d}-{day:02d}-{year}"
                        update_view = True
                    except ValueError:
                        self.msg = f"error: invalid date {self.count_buffer}"
                    self.count_buffer = ""
                elif len(self.count_buffer) == 6: # 6 digits: jump to MMYYYY
                    try:
                        month = int(self.count_buffer[:2])
                        day = 1
                        year = int(self.count_buffer[2:6])
                        new_date = date(year, month, day)

                        self.selected_day = new_date.day
                        self.working_month = new_date.month - 1
                        self.working_year = new_date.year
                        self.first_day_offset = zeller(self.working_month, self.working_year)
                        self.last_cursor_pos = None
                        
                        self.msg = f"jumped to {month:02d}-{day:02d}-{year}"
                        update_view = True
                    except ValueError:
                        self.msg = f"error: invalid date {self.count_buffer}"
                    self.count_buffer = ""
                elif len(self.count_buffer) == 4: # 4 digits: jump to MMDD
                    try:
                        month = int(self.count_buffer[:2])
                        day = int(self.count_buffer[2:4])
                        year = self.working_year # assume working year
                        new_date = date(year, month, day)

                        self.selected_day = new_date.day
                        self.working_month = new_date.month - 1
                        self.working_year = new_date.year
                        self.first_day_offset = zeller(self.working_month, self.working_year)
                        self.last_cursor_pos = None
                        
                        self.msg = f"jumped to {month:02d}-{day:02d}-{year}"
                        update_view = True
                    except ValueError:
                        self.msg = f"error: invalid date {self.count_buffer}"
                    self.count_buffer = ""
                elif len(self.count_buffer) in (1, 2): # 1 or 2 digits: jump to M or MM
                    try:
                        month = int(self.count_buffer)
                        day = 1
                        year = self.working_year # assume working year
                        new_date = date(year, month, day)

                        self.selected_day = new_date.day
                        self.working_month = new_date.month - 1
                        self.working_year = new_date.year
                        self.first_day_offset = zeller(self.working_month, self.working_year)
                        self.last_cursor_pos = None
                        
                        self.msg = f"jumped to {month:02d}-{day:02d}-{year}"
                        update_view = True
                    except ValueError:
                        self.msg = f"error: invalid date {self.count_buffer}"
                    self.count_buffer = ""
                else:
                    self.reset_date_to_today()
                    self.first_day_offset = zeller(self.working_month, self.working_year)
                    self.last_cursor_pos = None
                    update_view = True
                    self.msg = "jumped to today"
                self.operator = ''

        elif key == 27: # esc
            self.operator = ''
            self.count_buffer = ""

        else:
            self.operator = ''
            self.count_buffer = ""
            update_view = False

        return running, update_view
