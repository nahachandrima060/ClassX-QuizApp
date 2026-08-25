import random
import json  
import threading
from datetime import datetime


def input_with_timeout(prompt, timeout):
    answer = [None]

    def get_input():
        answer[0] = input(prompt)

    thread = threading.Thread(target=get_input)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        print(f"\nTime's up! ({timeout} seconds)")
        return None

    return answer[0]


class Question:
    def __init__(self, text, options, correct_answer, category, difficulty):
        self.text = text
        self.options = options
        self.correct_answer = correct_answer
        self.category = category
        self.difficulty = difficulty

    def ask(self, time_limit=None):
        print(f"\n[{self.category} | {self.difficulty}] {self.text}")

        shuffled_options = self.options[:]
        random.shuffle(shuffled_options)

        labels = "ABCDEFGH"[:len(shuffled_options)]
        label_to_option = dict(zip(labels, shuffled_options))

        for label, option in label_to_option.items():
            print(f"{label}) {option}")

        if time_limit:
            raw_answer = input_with_timeout("Your answer: ", time_limit)
        else:
            raw_answer = input("Your answer: ")

        if raw_answer is None:
            return False

        user_answer = raw_answer.strip().upper()
        chosen_option = label_to_option.get(user_answer)

        return chosen_option == self.correct_answer


def load_questions(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: could not find '{filepath}'. Make sure it's in the same folder.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: '{filepath}' has invalid JSON — {e}")
        return []

    questions = []
    for item in raw_data:
        questions.append(Question(
            text=item["text"],
            options=item["options"],
            correct_answer=item["correct_answer"],
            category=item.get("category", "General"),
            difficulty=item.get("difficulty", "medium")
        ))
    return questions


def get_available_values(questions, attribute):
    values = {getattr(q, attribute) for q in questions}
    return sorted(values)


SUBJECT_GROUPS = {
    "SST": ["Geography", "History"],
    "Maths": ["Maths"],
    "Physics": ["Physics"],
    "Chemistry": ["Chemistry"],
    "Biology": ["Biology"],
}


def get_available_subjects(questions):
    present_categories = set(get_available_values(questions, "category"))
    return [subject for subject, cats in SUBJECT_GROUPS.items() if present_categories & set(cats)]


def choose_subject(questions):
    subjects = get_available_subjects(questions)

    print("\nAvailable subjects:")
    for i, subject in enumerate(subjects, start=1):
        print(f"{i}. {subject}")

    choice = input("Choose a subject (number): ").strip()

    try:
        index = int(choice) - 1
        selected_subject = subjects[index]
    except (ValueError, IndexError):
        print("Invalid choice.")
        return [], None

    wanted_categories = {c.lower() for c in SUBJECT_GROUPS[selected_subject]}
    filtered = [q for q in questions if q.category.lower() in wanted_categories]
    return filtered, selected_subject


def choose_difficulty(questions):
    available = get_available_values(questions, "difficulty")
    options = available + ["all"]

    print("\nChoose difficulty:")
    for i, level in enumerate(options, start=1):
        print(f"{i}. {level.capitalize()}")

    choice = input("Choose a difficulty (number): ").strip()

    try:
        index = int(choice) - 1
        selected = options[index]
    except (ValueError, IndexError):
        print("Invalid choice — showing all difficulty levels instead.")
        return questions

    if selected == "all":
        return questions

    return [q for q in questions if q.difficulty.lower() == selected.lower()]


def run_quiz(questions, time_limit=None):
    score = 0
    missed = []
    category_stats = {}

    shuffled_questions = questions[:]
    random.shuffle(shuffled_questions)

    for i, question in enumerate(shuffled_questions, start=1):
        print(f"\n--- Question {i}/{len(shuffled_questions)} ---")

        category_stats.setdefault(question.category, [0, 0])
        category_stats[question.category][1] += 1

        if question.ask(time_limit):
            print("Correct!")
            score += 1
            category_stats[question.category][0] += 1
        else:
            print(f"Wrong! The correct answer was {question.correct_answer}.")
            missed.append(question)

    return score, missed, category_stats


def show_summary(score, total, missed):
    percentage = (score / total) * 100 if total > 0 else 0

    print("\n" + "=" * 40)
    print("QUIZ COMPLETE")
    print("=" * 40)
    print(f"Score: {score}/{total} ({percentage:.1f}%)")

    if missed:
        print(f"\nQuestions you missed ({len(missed)}):")
        for q in missed:
            print(f"  - [{q.category} | {q.difficulty}] {q.text}")
            print(f"    Correct answer: {q.correct_answer}")
    else:
        print("\nPerfect score! No questions missed.")

    print("=" * 40)


def load_high_scores(filepath="high_scores.json"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_high_score(score, total, filepath="high_scores.json"):
    scores = load_high_scores(filepath)

    percentage = (score / total) * 100 if total > 0 else 0
    scores.append({
        "score": score,
        "total": total,
        "percentage": round(percentage, 1),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    scores.sort(key=lambda s: s["percentage"], reverse=True)
    scores = scores[:10]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)


def show_high_scores(filepath="high_scores.json"):
    scores = load_high_scores(filepath)

    print("\n" + "=" * 40)
    print("HIGH SCORES")
    print("=" * 40)

    if not scores:
        print("No scores recorded yet.")
    else:
        for i, entry in enumerate(scores, start=1):
            print(f"{i}. {entry['score']}/{entry['total']} "
                  f"({entry['percentage']}%) - {entry['date']}")

    print("=" * 40)


def load_progress(filepath="progress.json"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_progress(category_stats, filepath="progress.json"):
    progress = load_progress(filepath)

    for category, (correct, total) in category_stats.items():
        if category not in progress:
            progress[category] = {"correct": 0, "total": 0}
        progress[category]["correct"] += correct
        progress[category]["total"] += total

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)


def show_progress(filepath="progress.json"):
    progress = load_progress(filepath)

    print("\n" + "=" * 40)
    print("YOUR PROGRESS BY TOPIC")
    print("=" * 40)

    if not progress:
        print("No quiz attempts recorded yet.")
        print("=" * 40)
        return

    results = []
    for category, stats in progress.items():
        total = stats["total"]
        correct = stats["correct"]
        percentage = (correct / total) * 100 if total > 0 else 0
        results.append((category, correct, total, percentage))

    results.sort(key=lambda r: r[3])

    for category, correct, total, percentage in results:
        print(f"{category:12s} {correct}/{total}  ({percentage:.1f}%)")

    weakest = results[0]
    print(f"\nFocus tip: You're weakest in {weakest[0]} ({weakest[3]:.1f}%) — spend more revision time there.")
    print("=" * 40)


def start_quiz():
    questions = load_questions("questions.json")
    print(f"DEBUG: Loaded {len(questions)} questions.")
    print(f"DEBUG: Categories found: {get_available_values(questions, 'category')}")

    if not questions:
        print("No questions loaded — returning to menu.")
        return

    questions, subject_name = choose_subject(questions)
    if not questions:
        print("No questions available for that selection — returning to menu.")
        return

    questions = choose_difficulty(questions)
    if not questions:
        print("No questions match that difficulty — returning to menu.")
        return

    time_input = input("\nSeconds per question (or press Enter for no limit): ").strip()
    time_limit = int(time_input) if time_input.isdigit() else None

    score, missed, category_stats = run_quiz(questions, time_limit)
    show_summary(score, len(questions), missed)
    save_high_score(score, len(questions))
    save_progress(category_stats)


def main():
    while True:
        print("\n" + "-" * 30)
        print("QUIZ APP MENU")
        print("-" * 30)
        print("1. Start Quiz")
        print("2. View High Scores")
        print("3. View Progress (weak areas)")
        print("4. Exit")

        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            start_quiz()
        elif choice == "2":
            show_high_scores()
        elif choice == "3":
            show_progress()
        elif choice == "4":
            print("Thanks for playing!")
            break
        else:
            print("Invalid choice — please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()