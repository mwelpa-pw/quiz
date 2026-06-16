# Aplikacja Quizowa 🎓

Prosta aplikacja konsolowa do nauki i rozwiązywania quizów z plików JSON.

## Jak zacząć? 🚀

### 1. Wymagania
Musisz mieć zainstalowanego **Pythona**.

### 2. Uruchomienie
Otwórz terminal w folderze z projektem i wpisz:
```bash
python script.py
```
Aplikacja automatycznie wyszuka pliki `.json` w folderze `quizes/` i pozwoli Ci wybrać, który quiz chcesz rozwiązać.

Przed rozpoczęciem quizu możesz wybrać:
- **Od którego pytania zacząć** – przydatne, jeśli chcesz powtórzyć tylko końcówkę materiału.
- **Czy pokazywać informację o wielokrotnym wyborze** – możesz wyłączyć tę podpowiedź, aby zwiększyć poziom trudności.

## Jak dodawać własne quizy? ✍️

Wszystkie quizy znajdują się w folderze `quizes/`. Możesz tam wrzucić własne pliki `.json`. Aby ułatwić sobie pracę, możesz poprosić ChatGPT lub innego asystenta AI o przygotowanie takiego pliku.

### 💡 Prompt do LLM (skopiuj i wklej)

Poniżej znajduje się gotowy prompt, który możesz wkleić do czatu (np. ChatGPT, Claude), dołączając swój plik z notatkami (plik źródłowy) oraz plik `quizes/example.json`:

---
> **Prompt:**
> Cześć! Przesyłam Ci dwa pliki:
> 1. Mój plik źródłowy z treścią (notatki/pytania).
> 2. Plik `example.json`, który pokazuje wymagany format danych.
>
> Twoim zadaniem jest przetworzenie mojego pliku źródłowego na pełnoprawny quiz w formacie JSON, dokładnie takim jak w `example.json`.
>
> **Zasady:**
> - Każde pytanie musi mieć klucze: `"pytanie"`, `"odpowiedzi"` (słownik z kluczami "1", "2", "3", "4") oraz `"poprawne_odpowiedzi"` (lista kluczy jako stringi).
> - Jeśli pytanie ma więcej niż jedną poprawną odpowiedź, uwzględnij je wszystkie w liście `"poprawne_odpowiedzi"`.
> - Nie zmieniaj struktury JSON-a.
> - Zwróć tylko czysty kod JSON.
---

### 🖼️ Dodawanie zdjęć
Jeśli chcesz, aby w pytaniu pojawiało się zdjęcie:
1. Przekonwertuj swoje zdjęcie do formatu **Base64**.
2. W pliku JSON, w obiekcie pytania, dodaj klucz `"obrazek"` i wklej tam kod Base64.
   Przykład:
   ```json
   {
     "pytanie": "Co jest na obrazku?",
     "odpowiedzi": { "1": "A", "2": "B", "3": "C", "4": "D" },
     "poprawne_odpowiedzi": ["1"],
     "obrazek": "iVBORw0KGgoAAAANS..." 
   }
   ```
Podczas wyświetlania pytania, aplikacja automatycznie otworzy zdjęcie w Twojej domyślnej przeglądarce/przeglądarce obrazów.

Miłej nauki! 📚
