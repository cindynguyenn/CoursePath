# ============================================================================================================================================
# Program Name: "coursepath.py"                                                                                                              =
# Program Description: This program is an course recommender for students who are unsure about what course they would like to take.          =
# ============================================================================================================================================

# ============================================================================================================================================
# Author Information:                                                                                                                        =
#   Author Name: Cindy Nguyen                                                                                                                =
#                Jacob Carlton                                                                                                               =
#   Author Email: ciindynguyen@csu.fullerton.edu                                                                                             =
#                 jrcarlton17@csu.fullerton.edu                                                                                              =
#                                                                                                                                            =
# Program Information:                                                                                                                       =
#   Program Name: coursepath                                                                                                                 =
#   Program Languages: python                                                                                                                =
#   Assemble: python coursepath.py                                                                                                           =
#   Date of last update: 05/07/2025                                                                                                          =
#   Comments reorganized: 05/07/2025                                                                                                         =
#                                                                                                                                            =
# Purpose:                                                                                                                                   =
#   The purpose of this program is to utilize AI to recommend Computer Science courses for students.                                         =
#                                                                                                                                            =
# References:                                                                                                                                =
#                                                                                                                                            =  
# ============================================================================================================================================

# ===== Begin code area ======================================================================================================================

# pip install openai
# pip install python-dotenv
# pip install openai==0.28

import sys
import json
import os
import openai
from dotenv import load_dotenv

# Load the .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# File used to track completed courses and interests
RECORD_FILE = "record.json"

# Load student profile from json in directory or return empty if missing
def load_profile():
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as f:
            profile = json.load(f)
            if "interests" not in profile:
                profile["interests"] = []
            return profile
    else:
        return {"completed_courses": [], "interests": []}

# Save student profile to json
def save_profile(profile):
    if "completed_courses" not in profile:
        profile["completed_courses"] = []
    if "interests" not in profile:
        profile["interests"] = []
    with open(RECORD_FILE, "w") as f:
        json.dump(profile, f, indent=2)

# Displays user's completed courses
def display_profile(profile):
    print("\nHere is your current record!")
    if profile["completed_courses"]:
        for course in profile["completed_courses"]:
            print(f"- {course}")
    else:
        print("You haven't added any courses yet.")
        
# Let's the user update their profile (add/remove courses or interests)
def update_profile(profile, courses):
    print("\nSelect an option:")
    print("1. Add a completed course")
    print("2. Add an interest")
    print("3. Remove an interest")
    option = input("Enter the option number: ")
    
    # Adding a completed course
    if option == "1": 
        display_courses(courses)
        course_input = input("\nEnter the course codes you completed (seperated by commas): ")
        entered_codes = [code.strip().upper() for code in course_input.split(",")]
    
        valid_codes = [course["code"] for course in courses]
        added_any = False

        for code in entered_codes:
            if code in valid_codes:
                if code in valid_codes:
                    if code not in profile ["completed_courses"]:
                        profile["completed_courses"].append(code)
                        print(f"{code} added to your TDA.")
                        added_any = True
                    else:
                        print(f"{code} is already in your profile.")
                else:
                    print(f"{code} is not a valid course code.")
        if added_any:
            save_profile(profile)
    
    # Can add interests. Will display their current interests and a list so they can see what they can add to make code work
    elif option == "2":
        print("\nCurrent interests:", profile.get("interests", []))
        
        all_catalog_interests = []
        for course in courses:
            for interest in course.get("interests", []):
                if interest not in all_catalog_interests:
                    all_catalog_interests.append(interest)
        print("\nHere is a list of possible interests: ")
        for interest in all_catalog_interests:
            print(f"- {interest}")
        
        interest_input = input("\nEnter your interests (seperated by commas): ").strip()
        entered_interests = [i.strip() for i in interest_input.split(",") if i.strip()]

        added_any = False

        for interest in entered_interests:
            if interest not in profile["interests"]:
                profile["interests"].append(interest)
                print(f"'{interest}' added to your profile.")
                added_any = True
            else:
                print(f"'{interest}' is already in your profile!")

        if added_any:
            save_profile(profile)
    
    # Remove existing interests       
    elif option == "3":
        print("\nCurrent interests: ")
        for interest in profile["interests"]:
            print(f"- {interest}")
        
        interest_input = input("\nEnter the interests you want to remove (seperated by commas): ").strip()
        interests_to_remove = [i.strip() for i in interest_input.split(",") if i.strip()]

        removed_any = False

        for interest in interests_to_remove:
            if interest in profile["interests"]:
                profile["interests"].remove(interest)
                print(f"'{interest}' removed from your profile.")
                removed_any = True
            else:
                print(f"'{interest}' is not in your profile!")

        if removed_any:
            save_profile(profile)

# Load available courses from catalog.json
def load_courses(filename):
    with open(filename, "r") as f:
        return json.load(f)

# Prints course codes, name, and unit count for each course
def display_courses(courses):
    print("\nHere is a list of the courses available:\n")
    for course in courses:
        print(f"{course['code']} - {course['name']} ({course['units']} units)")

# Checks if the user has met prerequisites for a course
def met_prereqs(course, completed_courses):
    for prereq in course["prerequisites"]:
        if prereq not in completed_courses:
            return False
    return True

# Asks GPT-3.5 a question using the user's profile + available courses
def recommend_system(courses, profile, question):
    completed = profile.get("completed_courses", [])
    course_summaries = []

    # Prepares a summary of all courses the user hasn't completed
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

    # Construct GPT prompt
    prompt = [
        {"role": "system", "content":(
            "You are a helpful academic advisor. Suggest courses from the catalog based on the student's completed courses and interests."
            "Be specific, helpful, and reference course codes/"
        )},
        {"role": "user", "content": f"My completed courses: {', '.join(completed)}"},
        {"role": "user", "content": f"My interests {', '.join(profile.get('interests', []))}"},
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