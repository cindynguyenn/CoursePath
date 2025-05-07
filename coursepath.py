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
    print("\nSelect an option:")
    print("1. Add a completed course")
    print("2. Add an interest")
    print("3. Remove an interest")
    option = input("Enter the option number: ")
    
    # can add courses theyve cmpleted
    if option == "1": 
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
    
    # can add interests,. will display their current interests and a list so they can see what they can add to make code work
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
        
        new_interest = input("\nEnter an interest you have: ").strip()
        if new_interest not in profile["interests"]:
            profile["interests"].append(new_interest)
            save_profile(profile)
            print(f"'{new_interest}' has been added to your profile.")
        else:
            print(f"'{new_interest}' is already in your profile or is invalid.")
    
    # can remove itnerests        
    elif option == "3":
        print("\nCurrent interests: ")
        for interest in profile["interests"]:
            print(f"- {interest}")
        
        interest_to_remove = input("\nEnter the interest you want to remove: ").strip()
        if interest_to_remove in profile["interests"]:
            profile["interests"].remove(interest_to_remove)
            save_profile(profile)
            print(f"'{interest_to_remove}' has been removed from your profile.")
        else:
            print(f"'{interest_to_remove}' is not in your profile.")
        
    else:
        print("Invalid option selected.")

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