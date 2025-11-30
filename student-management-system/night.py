print("====== Smart Student Record Analyzer ======")

def add_student():
    print("Add Student")
    try:
        while True:
            student_id = input("Enter Student ID: ").strip()
            if not student_id:
                print("ID cannot be empty.")
                continue
            try:
                if int(student_id) < 0:
                    print("Invalid input. ID cannot be negative.")
                    continue
            except ValueError:
                print("Invalid input. ID should be numeric.")
                continue

            try:
                duplicate = False
                with open("students.txt", "r") as file:
                    for line in file:
                        line = line.strip().split(",")
                        if len(line) < 1:
                            continue
                        std_id = line[0].strip()
                        if student_id == std_id:
                            duplicate = True
                            break
                if duplicate:
                    print("Student ID already exists. Please enter a unique ID.")
                    continue
            except FileNotFoundError:
                print("file not found.")
            student_id = int(student_id)
            break
        
        while True:    
            name = input("Enter Student Name: ").strip().lower()
            if not name:
                print("Name cannot be empty.")
                continue
            if not all(ch.isalpha() or ch.isspace() or ch=='-' for ch in name):
                print("Invalid input. Name should contain only alphabetic characters.")
                continue
            else:
                break
        
        while True:
            age = input("Enter Student Age: ")
            if not age:
                print("Age cannot be empty.")
                continue
            if age < '0':
                print("Invalid input. Age cannot be negative.")
                continue
            if not age.isdigit():
                print("Invalid input. Age should be numeric.")
                continue
            else:
                age = int(age)
                break
                
        while True:
            grade = input("Enter Student Grade: ").lower()
            if not grade:
                print("Grade cannot be empty.")
                continue
            if grade not in ['a', 'b', 'c', 'd', 'f']:
                print("Invalid input. Grade should be A, B, C, D, or F.")
                continue
            else:
                break
        while True:
            marks = input("Enter Student Marks: ")
            if not marks:
                print("Marks cannot be empty.")
                continue
            try:
                marks_val = int(marks)
            except ValueError:
                print("Invalid input. Marks should be numeric.")
                continue
            if marks_val < 0:
                print("Invalid input. Marks cannot be negative.")
                continue
            if marks_val > 100:
                print("Invalid input. Marks cannot be greater than 100.")
                continue
            
            marks = marks_val
            break
            
            
        with open("students.txt", "a") as file:
            file.write(f"{student_id},{name},{age},{grade},{marks}\n")
        print("Student added successfully.")

    except FileNotFoundError:
        print('File not found. Could not add student.')

def view_students():
    print("View All Students")
    try:
        with open("students.txt", "r") as file:
            students = file.readlines()
            if len(students) == 0:
                print("No student records found.")
            for student in students:
                std_id, name, age, grade, marks = student.strip().split(",")
                print(f"ID: {std_id}, Name: {name}, Age: {age}, Grade: {grade}, Marks: {marks}")
            print("Total Students:", len(students))
    except FileNotFoundError:
        print("File not found.")
        

def search_student():
    print("Search Student")
    while True:
        search_std = input("Enter Student ID or Name to search: ").lower()
        if not search_std:
            print("Input cannot be empty.")
            continue
        searched_id = None
        try:
            searched_id = int(search_std)
        except ValueError:
            pass
        if searched_id is not None and searched_id < 0:
            print("Invalid input. ID cannot be negative.")
            continue
        try:
            with open("students.txt", "r") as file:
                students = file.readlines()
                found = False
                for student in students:
                    std_id, name, age, grade, marks = student.strip().split(",")
                    if search_std == std_id or search_std in name.lower():
                        print(f"ID: {std_id}, Name: {name}, Age: {age}, Grade: {grade}, Marks: {marks}")
                        found = True
                        break
                if not found: 
                    print("Student not found.")
                else:
                    break
        except FileNotFoundError:
            print("File not found.")
        

def update_student():

    print("Update Student")
    while True:
        update_std = input("Enter Student ID to update: ")
        if not update_std:
            print("ID cannot be empty.")
            continue
        try:
            updated_ID = int(update_std)
        except ValueError:
            print("Invalid input. ID should be numeric.")
            continue
        if updated_ID < 0:
            print("Invalid input. ID cannot be negative.")
            continue
        
        try:
            with open("students.txt", "r") as file:
                students = file.readlines()
            updated_students = []
            found = False
            for student in students:
                line = student.strip()
                parts = line.split(",")
                
                std_id, name, age, grade, marks = parts
                if update_std == std_id:
                    print("Current Data:", student.strip())
                    while True:
                        name = input(f"Enter new name : ").lower() or name
                        if not all(ch.isalpha() or ch.isspace() or ch=='-' for ch in name):
                            print("Invalid input. Name should contain only alphabetic characters.")
                            continue
                        name = " ".join(name.split()).title()
                        break
                    while True:
                        age = input(f"Enter new age : ") or age
                        if not age.isdigit():
                            print("Invalid input. Age should be numeric.")
                            continue
                        age = int(age)
                        if age < 0:
                            print("Invalid input. Age cannot be negative.")
                            continue
                        break
                    while True:
                        grade = input(f"Enter new grade : ") or grade
                        if grade.lower() not in ['a', 'b', 'c', 'd', 'f']:
                            print("Invalid input. Grade should be A, B, C, D, or F.")
                            continue
                        grade = grade.lower()
                        break
                    while True:
                        marks = input(f"Enter new marks : ") or marks
                        try:
                            marks_val = int(marks)
                        except ValueError:
                            print("Invalid input. Marks should be numeric.")
                            continue
                        if marks_val < 0:
                            print("Invalid input. Marks cannot be negative.")
                            continue
                        if marks_val > 100:
                            print("Invalid input. Marks cannot be greater than 100.")
                            continue
                        marks = marks_val
                        break
                    updated_students.append(f"{std_id},{name},{age},{grade},{marks}\n")
                    found = True
                else:
                    updated_students.append(student)
            if found:
                with open("students.txt", "w") as file:
                    file.writelines(updated_students)
                print("Student updated successfully.")
                break
            else:
                print("Student not found.")
        except FileNotFoundError:
            print("File not found.")
        
def delete_student():
    print("Delete Student")
    while True:
        delete_std = input("Enter Student ID to delete: ")
        if not delete_std:
            print("ID cannot be empty.")
            continue
        try:
            deleted_ID = int(delete_std)
        except ValueError:
            print("Invalid input. ID should be numeric.")
            continue
        if deleted_ID < 0:
            print("Invalid input. ID cannot be negative.")
            continue
        
        try:
            with open("students.txt", "r") as file:
                students = file.readlines()
            updated_students = []
            found_Match = False
            deleted = False
            for student in students:
                std_id, name, age, grade, marks = student.split(",")
                if delete_std == std_id:
                    found_Match = True
                    print(f"Deleting Student: ID: {std_id}, Name: {name}, Age: {age}, Grade: {grade}, Marks: {marks}")
                    while True:
                        confirm = input("Are you sure? (yes/no): ").lower()
                        if confirm == 'yes':
                            deleted = True
                            break
                        elif confirm == 'no':
                            deleted = False
                            break
                        else:
                            print("Please enter 'yes' or 'no'.")
                else:
                    updated_students.append(student)
            if deleted:
                with open("students.txt", "w") as file:
                    file.writelines(updated_students)
                print("Student deleted successfully.")
                break
            elif found_Match and not deleted:
                print("Deletion cancelled.")
                break
            else:
                print("Student not found.")
        except FileNotFoundError:
            print("File not found.")


def analyze_data():
    
    print("Analyze Data")
    try:
        with open("students.txt", "r") as file:
            students = file.readlines()
            total_marks = 0
            count = 0
            highest_marks = 0
            lowest_marks = 100
            failing = 0 
            top_performer = ""
            for student in students:
                std_id, name, age, grade, marks = student.split(",")
                marks = int(marks)
                total_marks += marks
                count += 1
                if marks > highest_marks:
                    highest_marks = marks
                    top_performer = name
                if marks < lowest_marks:
                    lowest_marks = marks
                if marks < 40:
                    failing += 1
            
            if count > 0:
                average_marks = total_marks / count
                below_average_count = sum(1 for student in students if int(student.split(",")[4]) < average_marks)
                print(f"Average Marks: {average_marks}")
                print(f"Top Performer: {top_performer} ({highest_marks})")
                print(f"Number of Students Below Average Marks: {below_average_count}")
                print(f"Highest Marks: {highest_marks} | Lowest Marks: {lowest_marks}")
                print(f"Number of Failing Students: {failing}")
            else:
                print("No student records to analyze.")
    except FileNotFoundError:
        print("File not found.")


def main():
    while True:
        print('''1. Add Student
2. View All Students
3. Search Student
4. Update Student
5. Delete Student
6. Analyze Data
7. Exit''')

        choice = input("Enter your choice (1-7): ")
        if choice == '1':
            add_student()
        elif choice == '2':
            view_students()
        elif choice == '3':
            search_student()
        elif choice == '4':
            update_student()
        elif choice == '5':
            delete_student()
        elif choice == '6':
            analyze_data()
        elif choice == '7':
            print("Exiting the program. Thank you! for using Smart Student Record Analyzer.")
            break
        else:
            print("Invalid choice. Please try again.")
            
main()

    

