## Project Purpose
The purpose of this project is to address the challenge of time management and academic workload organization among students. Many students struggle with tracking assignments, prioritizing tasks, and maintaining a balanced academic schedule. These challenges can lead to last-minute cramming, missed deadlines, lower academic performance, and increased stress.

This project introduces a terminal-based student calendar application. This application enables students to:
- Organize assignments by class
- Estimate weekly study time based on assignment type
- Visualize their workload more clearly
- Focus on specific classes
- Mark tasks as complete

The application's design emphasizes simplicity, intuitive design, class-focused planning, and time estimation to give students better control over their schedules.

## Technology Stack
The application is developed using Python as the core programming language, which is well-suited for managing data structures, expandable arrays, and handling input/output operations. The language also offers standard libraries for date time logic and file operations.

The project uses the ncurses library to create a terminal-based graphical interface that can render the calendar interface and interactive dialogs in the terminal.

Development is primarily done in Visual Studio Code, which provides support for Python development as well as Azure and Git integration.

Data persistence is handled locally using plain text. Class sub-calendars are stored in the following format, with each line designating an assignment name, due date, completion status, and optional study time:

```
cop4504
"Week 2 Deliverables", 06152025, true
"Week 3 Deliverables", 06212025, false, 30
...
```

These values are read and parsed at runtime and stored in an assignment list, which is then stored in a subcalendar object. The class sub-calendar title is read from the filename and stored in the subcalendar object.

## Design Overview
### Core Functionality
This application provides an interactive calendar interface displaying assignments separated by individual class subcalendars. The user can create/delete assignments and subcalendars, mark assignment completion, and toggle visibility of each subcalendar to focus on specific classes.

### User Interface
The primary interface is a Gregorian calendar with Vim-style navigation. Navigation is done via the arrow keys or Vim-style movement keys (`h`, `j`, `k`, `l`).

#### Keyboard actions:
Calendar view:
- `[` and `]` - Cycle subcalendar selection
- `z` - Toggle subcalendar visibility
- `A` - Create new assignment on the selected date withinin the selected sub-calendar
- `Enter` - Open selected date in date view

Date view:
-  `Space` - Mark assignment completed
- `d` - Mark assignment for deletion
- `Enter` - Commit changes
- `Esc` - Exit date view

#### Commands
- `:` - Enter command mode
- `w`, `wq` - Write, write and quit
- `nc` - Create new subcalendar
- `dc` - Delete currently selected subcalendar

### ### Vim-style Navigation
The application incorporates Vim-style navigation commands to efficiently move through the calendar.

#### Motion Commands
You can prefix the motion commands (`h`, `j`, `k`, `l`) with numbers to move multiple steps at once. The numeric prefix is entered by typing the digits before pressing the motion key, similar to Vim. For example:
- `3l` moves 3 days to the right
- `2k` moves 2 weeks up (14 days)

#### Goto Commands (`gg`)
You can enter the numeric prefix as a date and press `g` twice (`gg`) to jump directly to a specific date. The date prefix can be in one of the following formats:
- `MMDDYYYY` (8 digits): jump to that exact date.
- `MMYYYY` (6 digits): jump to the first day of that month and year.
- `MMDD` (4 digits): jump to that month and day in the current year.
- `M` or `MM` (1 or 2 digits): jump to the first day of that month in the current year.
- Pressing `gg` without entering a date prefix jumps to the current date.

Press `Esc` to cancel any partial command or numeric prefix input.

### Data Structures
#### Assignment
##### Class Variables

| Variable    | Type      | Description                                                            |
| ----------- | --------- | ---------------------------------------------------------------------- |
| `name`      | `str`     | Name of the assignment                                                 |
| `date`      | `str`     | Due date in `MMDDYYYY` format (e.g., `06152025`)                       |
| `completed` | `boolean` | Task completion status (default: false)                                |
| `studytime` | `int`     | Estimated study time in minutes, used for weekly studytime aggregation |

##### Class Functions

| Function              | Arguments         | Description                                                              |
| --------------------- | ----------------- | ------------------------------------------------------------------------ |
| `rename()`            | `self, name: str` | Changes the assignment name to the one supplied in the function argument |
| `toggle_completion()` | `self`            | Toggles the `completed` boolean variable between True and False          |

#### Subcalendar
##### Class Variables

| Variable      | Type               | Description                                           |
| ------------- | ------------------ | ----------------------------------------------------- |
| `name`        | `str`              | Name of the subcalendar                               |
| `color`       | `int`              | ncurses color index (0–8)                             |
| `hidden`      | `boolean`          | Toggle visibility of the subcalendar (default: false) |
| `assignments` | `List[Assignment]` | List of assignments                                   |

##### Class Functions

| Function              | Arguments                      | Description                                                                |
| --------------------- | ------------------------------ | -------------------------------------------------------------------------- |
| `rename()`            | `self, name: str`              | Changes the subcalendar name to the one supplied in the function argument  |
| `insert_assignment()` | `self, assignment: Assignment` | Inserts an assignment into the assignments maintaining date order          |
| `toggle_hidden()`     | `self`                         | Toggles the `hidden` boolean variable between True and False               |
| `change_color()`      | `self, color: int`             | Changes the subcalendar color to the one supplied in the function argument |

##### Functions
- `rename(name: str)` - Changes the assignment name to the one supplied in the function argument
- `insert_assignment()` - Inserts an assignment into the `assignments` list
- `pop_assignment()` - Removes an assignment from the `assignments` list
- `toggle_hidden()` - Toggles the `hidden` variable

### Algorithms
- `zeller()` - Calculates the first day offset for calendar rendering

### Class Structure
- `main.py` - Application startup and main loop
- `ui.py` - Renders calendar view and handles user input
- `subcalendar.py` - Defines `Assignment` and `Subcalendar` data structures
- `utils.py` - Provides date, time, calendar logic, and helper functions

## Deployment
### Requirements
- Python 3.x
- azure-blob-storage (optional, if using Azure blob storage backend)

### Setup and Installation
Clone the repository:
```
git clone https://github.com/ma-choo/calicula.git
```

Run the application from the terminal:
```
python main.py
```

## Storage Backend
This application uses a storage backend to handle local storage and Azure blob storage.

### Local Storage
The default backend is local storage, but you may also configure it by creating or editing `~/.config/calicula/config`:
```
[storage]
backend = local
```

Subcalendars are stored as plaintext files in `~/.local/share/subcalendars`. These files are loaded at startup and saved on exit.

### Azure Blob Storage
To use Azure blob storage, configure `~/.config/calicula/config` as such:
```
[storage]
backend = azure

[azure]
connection_string = <YOUR_AZURE_CONNECTION_STRING>
container = <YOUR_CONTAINER_NAME>
```
