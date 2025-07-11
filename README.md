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
cop4504
"Week 2 Deliverables", 06152025, true
"Week 3 Deliverables", 06212025, false
...
```

These values will be read and parsed at runtime and stored in an assignment struct list, which will then be stored in a calendar struct. The class sub-calendar title will be read from the filename and stored in the calendar struct.

## Design Overview
### Core Features
The application will feature an interactive Gregorian calendar interface that displays upcoming assignments separated by class. It will also offer functionality for new assignments by selecting specific dates with the cursor. Each class will have its own sub-calendar, enabling students to manage their coursework separately and toggle the visibility of individual classes for a more focused view. The project will also generate weekly study time estimates using a reference table that associates each assignment type with an estimated time range (e.g., quizzes may require 20 to 30 minutes, while essays might take 1 to 3 hours). Additionally, the application will support task completion tracking, allowing users to mark assignments as completed or uncompleted.

### User Interface
The application's primary interface is a home view that displays an interactive Gregorian calendar. Users can navigate dates using the arrow keys or Vim-style keybindings and provide a cursor-based mechanism for selecting specific days. From this view, users can create, view, or delete assignments directly. Actions will generally be performed using keyboard shortcuts. For example, pressing `a` may open a dialog to create a new assignment at the current selection within the currently selected sub-calendar, `c` will open a dialog that lists the currently loaded sub-calendars and allow for creation of new sub-calendars, `v` may toggle the visibility of individual class sub-calendars, and `d` may be used in both dialogs to delete assignments and sub-calenders.

### Data Structures
The project will utilize two custom data structures: **Assignment** and **Subcalendar**.

#### Assignment
| variable          | type    | description                                                                                             |
| ----------------- | ------- | ------------------------------------------------------------------------------------------------------- |
| name              | string  | name of assignment                                                                                      |
| date              | string  | due date of assignment in MMDDYYYY format, e.g., 06152025, used to position assignments on the calendar |
| type              | int     | references time estimate table for time estimate aggregation purposes                                   |
| completed         | boolean | toggle completed/uncompleted (default value false)                                                      |

##### Class functions
`toggle_completion()` - switch the `completed` boolean between true/false

#### Subcalendar
| variable        | type          | description                                                            |
| --------------- | ------------  | ---------------------------------------------------------------------- |
| name            | string        | name of sub-calendar                                                   |
| color           | int           | used to designate ncurses colors from 0 to 8                           |
| hidden          | boolean       | used to toggle visibility of class sub-calendars (default value false) |
| assignments     | assignment[]  | list of assignments                                                    |

##### Class functions
`insert_assignment()` - inserts an assignment into the `assignments[]` list

`pop_assignment()` - pop an assignment from the `assigments[]` list

`hide()` - switch the `hidden` boolean between true/false

### Algorithms
`zeller()` - calculate first-day offset to properly render the calendar view.

### Class Structure
`main.py` - application startup and main loop.

`ui.py` - renders the calendar view and handles user input

`subcalendar.py` - defines `Assignment` and `Subcalendar` data structures.

`utils.py` - provides date, time, and calendar logic, as well as some other useful helper functions.

## Deployment
### Requirements
- Python3
- azure-blob-storage

### Setup and Installation
Clone the repository:
```
git clone https://github.com/ma-choo/calicula.git
```

Run the application from the terminal:
```
python main.py
```

## Storage
This application supports both local storage and Azure blob storage.

### Local Storage
The application will use local storage by default, but you may also configure `~/.config/calicula/config` as such:
```
[storage]
backend = local
```

Subcalendars will be stored locally in plain text files in `~/.config/calicula/subcalendars`. These subcalendar files are read and written on startup and exit.

### Azure Blob Storage
To store subcalendars in an Azure blob storage account, configure `~/.config/calicula/config` as such:
```
[storage]
backend = azure

[azure]
connection_string = <YOUR_AZURE_CONNECTION_STRING>
container = <YOUR_CONTAINER_NAME>
```