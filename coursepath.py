# pip install openai
# pip install python-dotenv
# pip install openai==0.28

import sys
import json
import os
import openai
from dotenv import load_dotenv, find_dotenv

# load the .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# profile of somesort that acts like tda and shows courses theyve taken
RECORD_FILE = "record.json"

def load_profile():
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as f:
            return json.load(f)
    else:
        return {"completed_courses": []}

def save_profile(profile):
    with open(RECORD_FILE, "w") as f:
        json.dump(profile, f)

# shows their TDA
def display_profile(profile):
    print("\nHere is your current record!")
    if profile["completed_courses"]:
        for course in profile["completed_courses"]:
            print(f"- {course}")
    else:
        print("You haven't added any courses yet.")
        
        
# user can add courses theyve taken to tda/record
def update_profile(profile, courses):
    display_courses(courses)
    course_code = input("\nEnter the course code you completed: ")
    
    valid_codes = [course["code"] for course in courses]
    if course_code in valid_codes:
        if course_code not in profile["completed_courses"]:
            profile["completed_courses"].append(course_code)
            save_profile(profile)
            print(f"{course_code} has been added to your TDA.")
        else:
            print("Course already added to your profile.")
    else:
        print("Invalid course code.")

# load courses frm json
def load_courses(filename):
    with open(filename, "r") as f:
        return json.load(f)

# display courses in json file
def display_courses(courses):
    print("\nHere is a list of the courses available:\n")
    for course in courses:
        print(f"{course['code']} - {course['name']} ({course['units']} units)")

# check if prereqs are met
def met_prereqs(course, completed_courses):
    for prereq in course["prerequisites"]:
        if prereq not in completed_courses:
            return False
    return True

# recommendation system
def recommend_system(courses, profile, question):
    completed = profile.get("completed_courses", [])
    course_summaries = []

    for course in courses:
        course_summaries.append({
            "code": course["code"],
            "name": course["name"],
            "prerequisites": course.get("prerequisites", []),
            "interests": course.get("interests",[]),
            "description": course.get("description", "")
        })

    catalog_summary = ""
    for c in course_summaries:
        if c["code"] not in completed:
            catalog_summary += f"{c['code']}: {c['name']}\n"
            catalog_summary += f"  Prereqs: {', '.join(c['prerequisites'])}\n"
            catalog_summary += f"  Interests: {', '.join(c['interests'])}\n"
            desc = c.get("description", "")
            catalog_summary += f"  Description: {desc[:150]}...\n\n"

    prompt = [
        {"role": "system", "content":(
            "You are a helpful academic advisor. Suggest courses from the catalog based on the student's completed courses and interests."
            "Be specific, helpful, and reference course codes/"
        )},
        {"role": "user", "content": f"My completed courses: {', '.join(completed)}"},
        {"role": "user", "content": f"Here is the course catalog:\n{catalog_summary}"},
        {"role": "user", "content": question}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=prompt,
            temperature=0.7
        )
        print("\nAI Response:\n")
        print(response['choices'][0]['message']['content'])
    except Exception as e:
        print(f"OpenAI API error: {e}")

# main menu/cli
def main():
    courses = load_courses("catalog.json")
    profile = load_profile()
    
    while True:
        print("\n--- Course Recommender Menu ---")
        print("1. View Available Courses")
        print("2. View TDA")
        print("3. Update TDA")
        print("4. Ask AI about courses")
        print("5. Exit")
        choice = input("> ")

        if choice == "1":
            print("Displaying the courses...")
            display_courses(courses)
        elif choice == "2":
            print("Displaying your TDA...")
            display_profile(profile)
        elif choice == "3":
            print("Updating your TDA...")
            update_profile(profile, courses)
        elif choice == "4":
            question = input("What do you want to ask the AI? ")
            recommend_system(courses, profile, question)
        elif choice == "5":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()