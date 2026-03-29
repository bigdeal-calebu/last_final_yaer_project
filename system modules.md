**main.py**

This is the starting point of the entire system.

Creates the main application window using Tkinter / CustomTkinter.

Defines the main container where all pages load.

Controls page switching between:

registration

login

dashboards

**Calls functions like:**

load\_registration()

load\_login()

Initializes the UI layout.

Loads global resources like fonts, colors, and images.





2\. login.py 

This module handles user login functionality.

What happens in this module

Creates the login user interface.

Displays:

email field

password field

Handles login button actions.

Connects to the database through:

db.py

Calls functions:

check\_user()

check\_admin()



After successful login

It redirects users to:

student\_dashboard.py

or

admin\_dashboard.py

Additional features



Forgot password link.

Input validation.

Error messages.





3\. register.py (User Registration Module)

Handles creation of new accounts.

What happens here

Creates registration form.

Collects:

name

email

password

Validates user inputs.

Saves user data into the database through:

db.py

Functions inside

Create registration UI

Validate inputs

Insert user into database



4\. forgot\_password.py (Password Recovery Module)

Handles password reset process.

What happens here

Displays password recovery form.

Asks for:

email

verification information

Verifies user from database.

Allows password update.



Flow

Login → Forgot Password → Reset Password → Login



5\. db.py (Database Communication Module)

This module is very important.

Responsibilities

Handles all database operations.

Operations inside

Database connection

Query execution

Data retrieval

Data insertion

Functions include

check\_user()

check\_admin()

insert\_user()

update\_password()

get\_attendance()

Used by

login.py

register.py

admin modules

student modules



6\. student\_dashboard.py (Student Interface)

This module creates the student control panel.

What happens here

Displays student dashboard with features like:

Student profile

Attendance history

Notifications

Start attendance recognition

Functions

Create dashboard layout

Load attendance data

Display student info



7\. admin\_dashboard.py (Admin Control Panel)

This module builds the admin dashboard interface.

Responsibilities

Creates the admin control panel.

Displays menu for:

registering students

managing attendance

generating reports

managing admins

Loads submodules from

admin\_dashboard\_files/



8\. header.py (Top Navigation Module)

This module creates the header section of the interface.

Responsibilities

Displays system title

Displays logo

Displays navigation buttons

Adds consistent UI header across pages



9\. layout.py (UI Layout Manager)

Controls layout structure of the dashboard.

Responsibilities

Define grid layouts

Arrange UI components

Control page spacing

Handle responsive UI behavior



10\. modify\_live.py (Live Camera Control Module)

This module helps manage live camera updates.

Responsibilities

Refresh UI while camera is running.

Prevent Tkinter from freezing.

Allow camera to run in GUI window.

Functions inside manage:

camera refresh

frame updating

UI synchronization



11\. admin\_dashboard\_files/face\_recognition.py

Handles real-time face recognition.

Responsibilities

Open camera

Detect faces using Haar Cascade Classifier

Recognize faces using trained model

Match student IDs

Trigger attendance recording



12\. admin\_dashboard\_files/generate\_dataset.py

This module captures student face images.

Responsibilities

Open camera

Capture multiple student images

Detect face

Save images inside:

train\_images/

Example output:

train\_images/studentID/



13\. admin\_dashboard\_files/train\_classifier.py

This module trains the face recognition model.

Responsibilities

Load images from train\_images

Convert images to grayscale

Extract facial features

Train the model using Local Binary Patterns Histograms

Save trained model inside:

models/



14\. admin\_dashboard\_files/admin\_register\_student.py

Allows admin to add new students.

Responsibilities

Display student registration form

Collect student details

Save student info in database

Optionally capture student images



15\. admin\_dashboard\_files/add\_admin.py

Handles creation of new admin accounts.

Responsibilities

Admin registration form

Insert admin into database

Manage admin privileges



16\. admin\_dashboard\_files/update\_users.py

Allows admin to edit user information.

Responsibilities

Modify student details

Modify admin details

Update database records



17\. admin\_dashboard\_files/view\_attendance.py

Displays attendance records.

Responsibilities

Fetch attendance from database

Display table of attendance

Filter by:

date

student

course



18\. admin\_dashboard\_files/comers.py

Handles students entering attendance area.

Responsibilities

Show students detected by camera

Display recognized students

Monitor attendance entry



19\. admin\_dashboard\_files/announcements.py

Allows admin to create announcements.

Responsibilities

Post announcements

Display notices to students

Save announcements in database



20\. admin\_dashboard\_files/settings.py

System configuration module.

Responsibilities

System settings

Camera settings

Model configuration

UI preferences



21\. admin\_dashboard\_files/config\_manager.py

Handles system configuration values.

Responsibilities

Load configuration

Save configuration

Manage system parameters



22\. admin\_dashboard\_files/shared.py

Contains shared helper functions.

Responsibilities

Utility functions

Reusable components

Shared UI elements



23\. admin\_dashboard\_files/export\_and\_help.py

Handles data export and help section.

Responsibilities

Export attendance to:

Excel

CSV

Provide system help documentation



24\. admin\_dashboard\_files/home.py

Creates admin dashboard home page.

Responsibilities

Display dashboard overview

Show system statistics

Quick navigation



25\. admin\_dashboard\_files/upload\_images.py

Allows admin to upload student images manually.

Responsibilities

Select image files

Store them in training dataset

Prepare images for model training

Other important folders

These are data folders used by modules.

cascade/

Contains:

haarcascade\_frontalface\_default.xml

Used for face detection.

train\_images/

Stores student face images used for training.

models/

Stores trained face recognition models.

unknowns/

Stores faces that the system could not recognize.

database/

Contains database scripts such as:

face\_recognition.sql





Complete System Module Structure

main.py

│

├ login.py

├ register.py

├ forgot\_password.py

├ db.py

├ student\_dashboard.py

├ admin\_dashboard.py

├ header.py

├ layout.py

├ modify\_live.py

│

└ admin\_dashboard\_files

&#x20;    ├ add\_admin.py

&#x20;    ├ admin\_register\_student.py

&#x20;    ├ announcements.py

&#x20;    ├ comers.py

&#x20;    ├ config\_manager.py

&#x20;    ├ export\_and\_help.py

&#x20;    ├ face\_recognition.py

&#x20;    ├ generate\_dataset.py

&#x20;    ├ home.py

&#x20;    ├ settings.py

&#x20;    ├ shared.py

&#x20;    ├ train\_classifier.py

&#x20;    ├ update\_users.py

&#x20;    ├ upload\_images.py

&#x20;    └ view\_attendance.py

