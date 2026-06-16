import base64
import json
import os
import random
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


def ask_question(question, question_number, total_questions):
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

    original_answer_items = [
        ("1", answers.get("1", "")),
        ("2", answers.get("2", "")),
        ("3", answers.get("3", "")),
        ("4", answers.get("4", "")),
    ]

    random.shuffle(original_answer_items)

    display_labels = ["a", "b", "c", "d"]
    displayed_answers = {}

    for label, original_answer_item in zip(display_labels, original_answer_items):
        original_key, answer_text = original_answer_item
        displayed_answers[label] = original_key
        print(f"  {label.upper()}) {answer_text}")

    correct_answers = {
        displayed_label
        for displayed_label, original_key in displayed_answers.items()
        if original_key in correct_answer_keys
    }

    is_multiple_choice = len(correct_answers) > 1

    if is_multiple_choice:
        print("\nTo pytanie ma wiele poprawnych odpowiedzi.")
        print("Wpisz odpowiedzi razem, np. ac albo abcd.")
    else:
        print("\nWpisz jedną odpowiedź: a, b, c albo d.")

    user_input = input("\nTwoja odpowiedź: ").strip().lower().replace(" ", "")
    user_answers = set(user_input)

    allowed_answers = {"a", "b", "c", "d"}
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

    score = 0

    for index, question in enumerate(questions, start=1):
        if ask_question(question, index, len(questions)):
            score += 1

    clear_console()
    print_header("Wynik końcowy")

    percentage = round(score / len(questions) * 100)

    print(f"Quiz: {quiz_path.stem}")
    print(f"Wynik: {score}/{len(questions)}")
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