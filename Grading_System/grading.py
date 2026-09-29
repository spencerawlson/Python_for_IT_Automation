'''''Ask: How many students?

Create the 5-subject list

Create counters for:
    A+/A
    B
    C
    D
    Failed

FOR each student:
    Ask for student's name

    Create an empty marks list
    Set failed_subjects = 0

    FOR each subject:
        Ask for mark

        Validate mark
        If invalid:
            ask again

        Store valid mark

        Determine subject performance

        If mark < 50:
            increase failed_subjects

    Calculate:
        total
        average
        highest
        lowest

    Determine grade

    Determine PASSED/FAILED

    Update class counters

    Print student's report

Print class summary'''

n_students = int(input("How many students you want to grade?\n"))

subjects = [
    "Python",
    "Cloud Computing",
    "Networking",
    "Database",
    "DevOps"
]

# Class counters
grade_a = 0
grade_b = 0
grade_c = 0
grade_d = 0
failed = 0


for n_ in range(n_students):

    name = input("\nEnter student name:\n")

    marks = []
    failed_subjects = 0

    for subject in subjects:

        while True:

            mark = float(input(f"Enter {subject} mark:\n"))

            if mark >= 0 and mark <= 100:

                if mark >= 90:
                    performance = "Excellent"

                elif mark >= 75:
                    performance = "Very Good"

                elif mark >= 60:
                    performance = "Good"

                elif mark >= 50:
                    performance = "Passed"

                else:
                    performance = "Failed"
                    failed_subjects += 1

                marks.append(mark)

                print(f"{subject}: {performance}")

                break

            else:
                print("Invalid Mark")


    # Calculate results
    total = sum(marks)
    average = total / len(marks)
    highest = max(marks)
    lowest = min(marks)


    # Determine final grade
    if average >= 90:
        grade = "A+"
        grade_a += 1

    elif average >= 80:
        grade = "A"
        grade_a += 1

    elif average >= 70:
        grade = "B"
        grade_b += 1

    elif average >= 60:
        grade = "C"
        grade_c += 1

    elif average >= 50:
        grade = "D"
        grade_d += 1

    else:
        grade = "F"
        failed += 1


    # Determine pass/fail
    if average >= 50 and failed_subjects == 0:
        status = "PASSED"
    else:
        status = "FAILED"


    # Student report
    print("\n----------------------------")
    print("STUDENT REPORT")
    print("----------------------------")

    print(f"Name: {name}")

    for i in range(len(subjects)):
        print(f"{subjects[i]}: {marks[i]}")

    print(f"Total: {total}")
    print(f"Average: {average:.2f}")
    print(f"Highest Mark: {highest}")
    print(f"Lowest Mark: {lowest}")
    print(f"Failed Subjects: {failed_subjects}")
    print(f"Grade: {grade}")
    print(f"Status: {status}")

    print("----------------------------")


# Class summary
print("\n============================")
print("CLASS SUMMARY")
print("============================")

print(f"Total Students: {n_students}")
print(f"A+/A Students: {grade_a}")
print(f"B Students: {grade_b}")
print(f"C Students: {grade_c}")
print(f"D Students: {grade_d}")
print(f"Failed Students: {failed}")

print("============================")







               
                
                       