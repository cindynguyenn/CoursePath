import tkinter as tk
from tkinter import messagebox, scrolledtext
from coursepath import load_profile, load_courses, recommend_system

# Create the main window
root = tk.Tk()
root.title("Course Advisor")  # window title
root.geometry("800x600")      # window size

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

# Run the GUI loop
root.mainloop()
