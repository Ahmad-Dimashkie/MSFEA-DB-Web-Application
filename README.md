# MSFEA Database Web Application

## Overview

This project is a web application built using Flask and Native HTML and CSS that interfaces with the MSFEA (Maroun Semaan Faculty of Engineering and Architecture) database. The application allows users to display various entities in the database, insert new data, and perform dynamic queries.

## Objective

The objective is to provide a user-friendly interface for the MSFEA database, including displaying existing data, registering new students and professors, adding new buildings and rooms, and allowing searches based on specific queries. The web app follows a CRUD (Create, Read, Update, Delete) model for database management.

## Features

### Part A: Display and Reporting

1. **Entity Tables Display**

   - Routes and views to display the contents of the following entity tables:
     - Departments
     - Administrative Staff
     - Students
     - Professors
     - Courses
     - Clubs
     - Buildings
     - Rooms
     - Room Booking
     - Final Exam Schedule
     - Research & Projects
   - HTML tables are used to show the data for each entity.

2. **Total Students Count**

   - A summary page shows the total number of students enrolled in MSFEA.

3. **Professor Details**
   - A search functionality that allows users to enter a professor's ID and get detailed information including:
     - Professor's name
     - Number of students they advise
     - Names of the students they advise
     - Names of the clubs they advise (if any)
     - Courses they are teaching in the current semester

### Part B: Data Insertion

1. **New Student Registration**

   - A form for inserting a new student record and assigning the student to a department and an advisor.

2. **New Professor Hiring**

   - A form to hire a new professor, including an option to assign them as an advisor to existing students.

3. **New Building and Room Addition**

   - A form to add a new building and rooms within the building.

4. **New Course Offering**
   - A form to schedule a new course, assign a professor to it, and book a room.

## How to Run the Application

### Prerequisites

1. **Python 3.x**
2. **Flask**
3. **SQLAlchemy (or any other ORM, if used)**
4. **Database** (PostgreSQL, MySQL, or SQLite)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd msfea-database-app
   ```
2. Activate venv directory:
   ```bash
   venv\scripts\activate
   ```
3. Run the code
   ```bash
   python webapp.py
   ```

### ER Diagram

![image](https://github.com/user-attachments/assets/fdae07ef-1867-4530-99c1-c3c9426a9b5d)
