

**core system modules**

+-----------------------+---------------------------------------------------------------+------------------------------------------------------------------+



| MODULE                | WHAT IT DOES                                                  | DEPENDENCIES                                                     |

+-----------------------+---------------------------------------------------------------+------------------------------------------------------------------+

| main.py               | Starts the application, creates the main window, manages     | login.py, register.py, forgot\_password.py,                      |

|                       | navigation between pages.                                     | student\_dashboard.py, admin\_dashboard.py,                       |

|                       |                                                               | layout.py, header.py                                            |

+-----------------------+---------------------------------------------------------------+------------------------------------------------------------------+

| login.py              | Handles user login, validates credentials, and redirects     | db.py, student\_dashboard.py, admin\_dashboard.py,                |

|                       | users to the appropriate dashboard.                          | forgot\_password.py, header.py                                   |

+-----------------------+---------------------------------------------------------------+------------------------------------------------------------------+

| register.py           | Handles new user registration and stores user details        | db.py, login.py, header.py                                      |

|                       | in the database.                                             |                                                                  |

+-----------------------+---------------------------------------------------------------+------------------------------------------------------------------+

| forgot\_password.py    | Allows users to reset forgotten passwords.                   | db.py, login.py                                                 |

+-----------------------+---------------------------------------------------------------+------------------------------------------------------------------+

| db.py                 | Manages database connection, executes SQL queries,           | Used by all modules requiring database access                   |

|                       | and retrieves data.                                          |                                                                  |

+-----------------------+---------------------------------------------------------------+------------------------------------------------------------------+

| student\_dashboard.py  | Displays the student dashboard and shows attendance          | db.py, layout.py, header.py                                     |

|                       | information.                                                 |                                                                  |

+-----------------------+---------------------------------------------------------------+------------------------------------------------------------------+

| admin\_dashboard.py    | Displays the admin dashboard and loads admin modules.        | admin\_dashboard\_files/, db.py, layout.py, header.py             |

+-----------------------+---------------------------------------------------------------+------------------------------------------------------------------+

| header.py             | Creates the top navigation header used across system pages.  | Used by most UI modules                                         |

+-----------------------+---------------------------------------------------------------+------------------------------------------------------------------+

| layout.py             | Defines UI layout structure and widget positioning.          | main.py, student\_dashboard.py, admin\_dashboard.py               |

+-----------------------+---------------------------------------------------------------+------------------------------------------------------------------+

| modify\_live.py        | Handles live camera updates and prevents the GUI from        | face\_recognition.py, GUI components                             |

|                       | freezing during camera operation.                            |                                                                  |

|<br />|||
|-|-|-|







**ADMIN DASHBOARD MODULES**

**Location: admin\_dashboard\_files/**

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| MODULE                   | WHAT IT DOES                                             | DEPENDENCIES                               |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| home.py                  | Displays admin dashboard overview and statistics.       | db.py                                      |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| admin\_register\_student.py| Registers new students in the system.                   | db.py, generate\_dataset.py                 |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| add\_admin.py             | Creates new admin accounts.                             | db.py                                      |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| update\_users.py          | Updates student or admin information.                   | db.py                                      |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| view\_attendance.py       | Displays attendance records in table format.            | db.py                                      |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| announcements.py         | Allows admin to post announcements to users.            | db.py                                      |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| comers.py                | Monitors students entering the attendance area.         | face\_recognition.py, db.py                 |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| settings.py              | Allows modification of system configuration settings.   | config\_manager.py                          |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| config\_manager.py        | Manages loading and saving system configuration.        | settings.py                                |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| shared.py                | Contains shared helper functions used across modules.   | Used by admin modules                      |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| export\_and\_help.py       | Exports attendance data and provides system help.       | db.py                                      |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| upload\_images.py         | Uploads student images manually for training dataset.   | train\_images/                              |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| generate\_dataset.py      | Captures student face images using the camera.          | OpenCV, train\_images/, cascade file        |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| train\_classifier.py      | Trains the face recognition model using training data.  | train\_images/, models/                     |

+--------------------------+----------------------------------------------------------+--------------------------------------------+

| face\_recognition.py      | Detects and recognizes faces and records attendance.    | db.py, cascade file, trained model         |

||||
|-|-|-|





SUPPORTING DATA COMPONENTS

+--------------+-----------------------------------------------------------+----------------------------------------+

| COMPONENT    | PURPOSE                                                   | USED BY                                |

+--------------+-----------------------------------------------------------+----------------------------------------+

| cascade/     | Stores face detection model                              | face\_recognition.py,                   |

|              | (haarcascade\_frontalface\_default.xml).                   | generate\_dataset.py                    |

+--------------+-----------------------------------------------------------+----------------------------------------+

| train\_images/| Stores captured student face images used for training.   | generate\_dataset.py,                   |

|              |                                                           | train\_classifier.py                    |

+--------------+-----------------------------------------------------------+----------------------------------------+

| models/      | Stores trained face recognition models.                  | train\_classifier.py,                   |

|              |                                                           | face\_recognition.py                    |

+--------------+-----------------------------------------------------------+----------------------------------------+

| unknowns/    | Stores images of faces that are not recognized.          | face\_recognition.py                    |

+--------------+-----------------------------------------------------------+----------------------------------------+

| database/    | Contains SQL scripts for database structure.             | db.py                                  |

+--------------+-----------------------------------------------------------+----------------------------------------+

