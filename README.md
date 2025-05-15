# CoursePath
An AI-powered course recommendation system for CSUF Computer Science students.

# Overview
This project helps CSUF CS students select their courses each semester by analyzing their:
- Completed courses
- Prerequisites
- Academic interests

Built with Python and OpenAI-3.5 Turbo with a Tkinter GUI.

# Features
Features include:
- Student Profile System
- Course Catalog Browser
- AI Recommendation Engine
- Interactive GUI

# Files include:
- catalog.json | Structured course database
- coursepath.py | Backend logic that utilizes a CLI interface
- gui_coursepath.py | Backend logic that utilizes a GUI interface. This will be the main file.
- requirements.json | Requirements needed for Lower and Higher Division Courses and Electives
- record.json | User data storage/user profile

# Getting Started:
pip install openai
pip install python-dotenv
pip install openai==0.28
python gui_coursepath.py | for GUI interface
python coursepath.py | for CLI interface (less buggy)

Make sure to create a .env file to store the OpenAI API.
