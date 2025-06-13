## Project Purpose
The purpose of this project is to address the challenge of time management and academic workload organization among students. Many students struggle with tracking assignments, prioritizing tasks, and maintaining a balanced academic schedule. These challenges can lead to last-minute cramming, missed deadlines, lower academic performance, and increased stress.

This project introduces a terminal-based student calendar application. This application will enable students to:
- Organize assignments by class
- Estimate weekly study time based on assignment type
- Visualize their workload more clearly
- Focus on specific classes
- Mark tasks as complete

The application's design emphasizes simplicity, intuitive design, class-focused planning, and time estimation to give students better control over their schedules.

## Technology Stack
The application will be developed using Python as the core programming language, as it is well-suited for managing data structures, expandable arrays, and handling input/output operations. The language also offers standard libraries for date and time logic.

The project will utilize the ncurses library for the user interface, which will be used to create a text-based graphical interface that can render the calendar interface and interactive dialogs in the terminal.

Development will mainly be done in Visual Studio Code, which provides support for Python development as well as Azure and Git integration.

Data persistence will be handled locally using plain text. Class sub-calendars will be stored in the following format, with each line designating an assignment name, due date, and completion status:
```
cop4504.cal
"Week 2 Deliverables", 06152025, true
"Week 3 Deliverables", 06212025, false
...
```

These values will be read and parsed at runtime and stored in an assignment struct list, which will then be stored in a calendar struct. The class sub-calendar title will be read from the filename and stored in the calendar struct.

## Design Overview
### Core Features
The application will feature an interactive Gregorian calendar interface that displays upcoming assignments separated by class. It will also offer functionality for new assignments by selecting specific dates with the cursor. Each class will have its own sub-calendar, enabling students to manage their coursework separately and toggle the visibility of individual classes for a more focused view. The project will also generate weekly study time estimates using a reference table that associates each assignment type with an estimated time range (e.g., quizzes may require 20 to 30 minutes, while essays might take 1 to 3 hours). Additionally, the application will support task completion tracking, allowing users to mark assignments as completed or uncompleted.

### Data Structures
The project will utilize two custom data structures: **assignment** and **subcal**.

**assignment**
| variable          | type    | description                                                                                      |
| ----------------- | ------- | ------------------------------------------------------------------------------------------------ |
| name              | string  | name of assignment                                                                               |
| date              | int     | due date of assignment as MMDDYYYY, e.g., 06152025, used to position assignments on the calendar |
| type              | int     | references time estimate table for time estimate aggregation purposes                            |
| completed         | boolean | toggle completed/uncompleted (default value false)                                               |

**subcal**
| variable | type    | description                                                            |
| -------- | ------- | ---------------------------------------------------------------------- |
| name     | string  | name of sub-calendar                                                   |
| color    | int     | used to designate ncurses colors from 0 to 8                           |
| hide     | boolean | used to toggle visibility of class sub-calendars (default value false) |

### User Interface
The application's primary interface is a home view that displays an interactive Gregorian calendar. Users can navigate dates using the arrow keys or Vim-style keybindings and provide a cursor-based mechanism for selecting specific days. From this view, users can create, view, or delete assignments directly. Actions will generally be performed using keyboard shortcuts. For example, pressing `a` may open a dialog to create a new assignment at the current selection within the currently selected sub-calendar, `c` will open a dialog that lists the currently loaded sub-calendars and allow for creation of new sub-calendars, `v` may toggle the visibility of individual class sub-calendars, and `d` may be used in both dialogs to delete assignments and sub-calenders.

## Deployment
### Requirements
To run this application locally, you will need:
- Python 3.11 or higher  
- A terminal emulator  

No external libraries are required as the application uses Python’s standard library, including the built-in curses module for terminal-based UI.

### Setup and Installation
Clone the repository:
```
git clone https://github.com/ma-choo/calicula.git
```

Run the application from the terminal:
```
python3 calicula.py
```

Data is stored locally in plain text files in `~/.calicula`. Calendar files are read and written on startup and exit.
