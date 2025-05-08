import tkinter as tk
from tkinter import messagebox, scrolledtext
from coursepath import load_profile, load_courses, recommend_system, save_profile

# Create the main window
root = tk.Tk()
root.title("Course Advisor")  
root.geometry("800x600")      

# Add a heading label
title_label = tk.Label(root, text="CSUF Course Recommender", font=("Helvetica", 18))
title_label.pack(pady=20)

# Question Entry Label
entry_label = tk.Label(root, text="Ask the AI about courses:")
entry_label.pack()

# Question Entry Field
question_entry = tk.Entry(root, width=80)
question_entry.pack(pady=5)

# Response Output Box
output_box = scrolledtext.ScrolledText(root, wrap = tk.WORD, width=90, height=20)
output_box.pack(padx=10, pady=10)

# Ask AI Button Callback
def ask_ai():
    question = question_entry.get().strip()
    if not question:
        messagebox.showwarning("Empty", "Please enter a question.")
        return
    
    # Load data
    courses = load_courses("catalog.json")
    profile = load_profile()

    # Clears previous output
    output_box.delete("1.0", tk.END)

    # Redirect output from recommend_system()
    from io import StringIO
    import sys 
    buffer = StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buffer

    # Calling GPT
    try:
        recommend_system(courses, profile, question)
    except Exception as e:
        buffer.write(f"\n[ERROR]L {str(e)}")
    finally:
        sys.stdout = sys_stdout

    # Display results to GUI
    output_text = buffer.getvalue()
    output_box.insert(tk.END, output_text)

# Ask AI Button display
ask_button = tk.Button(root, text="Ask AI", command=ask_ai)
ask_button.pack(pady=10)

# Additional Action Buttons
action_frame = tk.Frame(root)
action_frame.pack(pady=10)

def view_courses():
    courses = load_courses("catalog.json")
    course_list="\n".join([f"{c['code']}]) - {c['name']} ({c['units']} units)" for c in courses])
    messagebox.showinfo("Available Courses", course_list)

def view_tda():
    profile = load_profile()
    completed = profile.get("completed_courses", [])
    interests = profile.get("interests", [])
    tda = f"Completed Courses:\n" + "\n".join(f"-{c}" for c in completed or ["None"]) + "\n\n" \
        + f"Interests:\n" + "\n".join(f"- {i}" for i in interests or ["None"])
    messagebox.showinfo("Your TDA", tda)

def update_tda():
    profile = load_profile()
    update_window=tk.Toplevel(root)
    update_window.title("Update TDA")
    update_window.geometry("400x250")

    tk.Label(update_window, text="Enter completed courses(seperated by commas):").pack(pady=5)
    course_entry = tk.Entry(update_window, width=50)
    course_entry.pack()

    tk.Label(update_window, text="Enter interests (seperated by commas):").pack(pady=5)
    interest_entry = tk.Entry(update_window, width=50)
    interest_entry.pack()

    def save_tda():
        # Add courses
        course_input = course_entry.get().strip()
        entered_codes = [c.strip().upper() for c in course_input.split(",") if c.strip()]
        valid_codes = {c["code"] for c in load_courses("catalog.json")}
        added_courses = [c for c in entered_codes if c in valid_codes]
        profile["completed_courses"] = list(set(profile.get("interests", []) + entered_codes))

        # Add interests
        interest_input = interest_entry.get().strip()
        entered_interests = [i.strip() for i in interest_input.split(",") if i.strip()]
        profile["interests"] = list(set(profile.get("interests", []) + entered_interests))

        save_profile(profile)
        messagebox.showinfo("Saved", "Your TDA has been updated.")
        update_window.destroy()

    tk.Button(update_window, text="Save", command=save_tda).pack(pady=15)

# Buttons for View/Update/Exit
tk.Button(action_frame, text="View Course Catalog", width=18, command=view_courses).grid(row=0, column=0, padx=5)
tk.Button(action_frame, text="View TDA", width=15, command=view_tda).grid(row=0, column=1, padx=5)
tk.Button(action_frame, text="Update TDA", width=15, command=update_tda).grid(row=0, column=2, padx=5)
tk.Button(action_frame, text="Exit", width=15, command=root.quit).grid(row=0, column=3, padx=5)

# Run the GUI loop
root.mainloop()
