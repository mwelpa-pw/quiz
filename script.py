import base64
import json
import os
import random
import string
import tempfile
import webbrowser
from pathlib import Path


QUIZ_FOLDER = Path(__file__).resolve().parent / "quizes"


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title):
    line = "═" * 60
    print(f"\n╔{line}╗")
    print(f"║{title.center(60)}║")
    print(f"╚{line}╝\n")


def print_box(text):
    lines = text.splitlines()
    width = min(max(len(line) for line in lines) + 4, 80) if lines else 20

    print("┌" + "─" * width + "┐")
    for line in lines:
        print(f"│  {line.ljust(width - 2)}│")
    print("└" + "─" * width + "┘")


def load_quiz_files():
    if not QUIZ_FOLDER.exists():
        QUIZ_FOLDER.mkdir(parents=True, exist_ok=True)
        return []

    return sorted(QUIZ_FOLDER.glob("*.json"))


def choose_quiz(quiz_files):
    while True:
        clear_console()
        print_header("Dostępne quizy")

        if not quiz_files:
            print("Nie znaleziono żadnych quizów.")
            print(f"Utwórz pliki JSON w folderze: {QUIZ_FOLDER}")
            return None

        for index, quiz_file in enumerate(quiz_files, start=1):
            print(f"  {index}. {quiz_file.stem}")

        print("\n  0. Wyjdź")

        choice = input("\nWybierz numer quizu: ").strip()

        if choice == "0":
            return None

        if choice.isdigit():
            choice_number = int(choice)
            if 1 <= choice_number <= len(quiz_files):
                return quiz_files[choice_number - 1]

        input("\nNieprawidłowy wybór. Naciśnij Enter i spróbuj ponownie...")


def load_quiz(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict) and "pytania" in data:
        return data["pytania"]

    if isinstance(data, list):
        return data

    raise ValueError("Quiz musi być listą pytań albo obiektem z kluczem 'pytania'.")


def normalize_answer_key(key):
    key = str(key).strip().lower()

    mapping = {
        "1": "a",
        "2": "b",
        "3": "c",
        "4": "d",
        "a": "a",
        "b": "b",
        "c": "c",
        "d": "d",
    }

    return mapping.get(key)


def normalize_answers(answer_list):
    normalized = set()

    for answer in answer_list:
        normalized_key = normalize_answer_key(answer)

        if normalized_key:
            normalized.add(normalized_key)

    return normalized


def decode_and_open_image(base64_data, question_number):
    try:
        image_bytes = base64.b64decode(base64_data)

        temp_dir = Path(tempfile.gettempdir())
        image_path = temp_dir / f"quiz_question_{question_number}.png"

        with open(image_path, "wb") as image_file:
            image_file.write(image_bytes)

        webbrowser.open(image_path.as_uri())

        return True
    except Exception:
        return False


def ask_question(question, question_number, total_questions, show_multiple_choice_info=True):
    clear_console()
    print_header(f"Pytanie {question_number}/{total_questions}")

    question_text = question.get("pytanie", "").strip()
    answers = question.get("odpowiedzi", {})
    correct_answer_keys = {str(answer) for answer in question.get("poprawne_odpowiedzi", [])}
    image_base64 = question.get("obrazek")

    if not question_text:
        print("To pytanie nie ma treści.")
        return False

    print_box(question_text)

    if image_base64:
        opened = decode_and_open_image(image_base64, question_number)

        if opened:
            print("\n🖼️  Do tego pytania otwarto obrazek w nowym oknie.")
        else:
            print("\n⚠️  Nie udało się otworzyć obrazka z tego pytania.")

    print("\nOdpowiedzi:\n")

    original_answer_items = sorted(answers.items(), key=lambda x: str(x[0]))

    random.shuffle(original_answer_items)

    display_labels = list(string.ascii_lowercase[:len(original_answer_items)])
    displayed_answers = {}

    for label, original_answer_item in zip(display_labels, original_answer_items):
        original_key, answer_text = original_answer_item
        displayed_answers[label] = str(original_key)
        print(f"  {label.upper()}) {answer_text}")

    correct_answers = {
        displayed_label
        for displayed_label, original_key in displayed_answers.items()
        if original_key in correct_answer_keys
    }

    is_multiple_choice = len(correct_answers) > 1

    if is_multiple_choice and show_multiple_choice_info:
        print("\nTo pytanie ma wiele poprawnych odpowiedzi.")
        print(f"Wpisz odpowiedzi razem, np. {''.join(display_labels[:2])} albo {''.join(display_labels)}.")
    elif is_multiple_choice and not show_multiple_choice_info:
        print("\nTo pytanie może mieć jedną lub wiele poprawnych odpowiedzi.")
        print(f"Wpisz odpowiedzi razem, np. {''.join(display_labels[:2])} albo {''.join(display_labels)}.")
    else:
        if len(display_labels) > 0:
            if len(display_labels) == 1:
                 print(f"\nWpisz odpowiedź: {display_labels[0]}.")
            else:
                 labels_str = ", ".join(display_labels[:-1]) + " albo " + display_labels[-1]
                 print(f"\nWpisz jedną odpowiedź: {labels_str}.")

    user_input = input("\nTwoja odpowiedź: ").strip().lower().replace(" ", "")
    user_answers = set(user_input)

    allowed_answers = set(display_labels)
    user_answers = user_answers.intersection(allowed_answers)

    is_correct = user_answers == correct_answers

    print()

    if is_correct:
        print("✅ Dobrze!")
    else:
        correct_text = ", ".join(sorted(answer.upper() for answer in correct_answers))
        print("❌ Źle.")
        print(f"Poprawna odpowiedź: {correct_text}")

    input("\nNaciśnij Enter, aby przejść dalej...")

    return is_correct

def run_quiz(quiz_path):
    try:
        questions = load_quiz(quiz_path)
    except Exception as error:
        clear_console()
        print_header("Błąd ładowania quizu")
        print(f"Nie udało się wczytać quizu: {quiz_path.name}")
        print(f"Szczegóły: {error}")
        input("\nNaciśnij Enter, aby wrócić do menu...")
        return

    if not questions:
        clear_console()
        print_header("Pusty quiz")
        print("Ten quiz nie zawiera pytań.")
        input("\nNaciśnij Enter, aby wrócić do menu...")
        return

    clear_console()
    print_header(f"Ustawienia quizu: {quiz_path.stem}")

    try:
        start_from = input(f"Od którego pytania chcesz zacząć? (1-{len(questions)}, domyślnie 1): ").strip()
        start_index = int(start_from) if start_from else 1
        if not (1 <= start_index <= len(questions)):
            start_index = 1
    except ValueError:
        start_index = 1

    show_info_input = input("Czy pokazywać informację, że pytanie jest wielokrotnego wyboru? (t/n, domyślnie t): ").strip().lower()
    show_multiple_choice_info = show_info_input != "n"

    score = 0
    active_questions = questions[start_index - 1:]
    total_active = len(active_questions)

    for i, question in enumerate(active_questions):
        current_question_number = start_index + i
        if ask_question(question, current_question_number, len(questions), show_multiple_choice_info):
            score += 1

    clear_console()
    print_header("Wynik końcowy")

    percentage = round(score / total_active * 100) if total_active > 0 else 0

    print(f"Quiz: {quiz_path.stem}")
    print(f"Wynik: {score}/{total_active}")
    print(f"Procent: {percentage}%")

    if percentage == 100:
        print("\n🏆 Perfekcyjnie!")
    elif percentage >= 70:
        print("\n🎉 Bardzo dobrze!")
    elif percentage >= 50:
        print("\n🙂 Nieźle, ale można lepiej.")
    else:
        print("\n📚 Warto jeszcze poćwiczyć.")

    input("\nNaciśnij Enter, aby wrócić do menu...")


def main():
    while True:
        quiz_files = load_quiz_files()
        selected_quiz = choose_quiz(quiz_files)

        if selected_quiz is None:
            clear_console()
            print("Do zobaczenia!")
            break

        run_quiz(selected_quiz)


if __name__ == "__main__":
    main()