# ===========================================
#  LYNX Task to do manager
#  Autor: Franciszek Niemynski
# ===========================================

import customtkinter as ctk
import tkinter as tk
import sqlite3
from datetime import datetime

# --- Wygląd ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- Główne okno ---
app = ctk.CTk()
app.title("🦊 LYNX Twój menedżer dnia")
app.geometry("650x800")
app.resizable(False, False)

# --- Połączenie z bazą danych ---
db = sqlite3.connect("lynx_notes.db")
cursor = db.cursor()

# ====================================================================
# TUTAJ JEST NAPRAWA BAZY DANYCH
# ====================================================================
# --- aktualizacja bazy danych ---
try:
    # Sprawdzamy, jakie kolumny już istnieją w tabeli 'notes'
    cursor.execute("PRAGMA table_info(notes)")
    columns = [info[1] for info in cursor.fetchall()]

    # Jeśli brakuje kolumny 'priority', to ją dodajemy
    if 'priority' not in columns:
        print("Wykryto starą wersję bazy. Aktualizuję: dodaję kolumnę 'priority'...")
        cursor.execute("ALTER TABLE notes ADD COLUMN priority TEXT")

    # Jeśli brakuje kolumny 'due_time', też ją dodajemy
    if 'due_time' not in columns:
        print("Wykryto starą wersję bazy. Aktualizuję: dodaję kolumnę 'due_time'...")
        cursor.execute("ALTER TABLE notes ADD COLUMN due_time TEXT")
    
    db.commit() # Zapisujemy zmiany po ewentualnej modernizacji
except sqlite3.OperationalError:
    # Ten błąd pojawi się, jeśli tabela 'notes' w ogóle nie istnieje.
    # Wtedy nic nie robimy, bo zaraz i tak ją stworzymy poprawnie.
    pass
# ====================================================================

# Tworzymy tabelkę, jeśli jeszcze nie istnieje.
# Ten kod pozostaje bez zmian, jest potrzebny przy pierwszym uruchomieniu.
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    created_at TEXT,
    priority TEXT,
    due_time TEXT
)
""")
db.commit()

# --- Kolory do priorytetów ---
PRIORITY_COLORS = {
    "Ważne": "#FFD700",
    "Bardzo Ważne": "#FFA500",
    "Ultra Ważne": "#FF4500"
}

# --- Funkcje (cała reszta bez zmian) ---

def zapisz_zad():
    """Zapisuje zadanie do bazy, razem z priorytetem i godziną."""
    tresc = poletxt.get("1.0", "end-1c").strip()
    priorytet = priority_var.get()
    godzina = time_entry.get().strip()

    if tresc:
        data = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("INSERT INTO notes (content, created_at, priority, due_time) VALUES (?, ?, ?, ?)",
                       (tresc, data, priorytet, godzina))
        db.commit()
        wyczysc_pole()
        wczytaj_zad()

def wczytaj_zad():
    """Wczytuje zadania z bazy i pokazuje je na liście, kolorując co trzeba."""
    Lista_zadan.delete(0, "end")
    cursor.execute("SELECT id, content, created_at, priority, due_time FROM notes ORDER BY id DESC")
    
    for i, notka in enumerate(cursor.fetchall()):
        id, tresc, data, priorytet, godzina = notka
        skrot = tresc[:35].replace("\n", " ")

        info_godzina = f" | Godzina: {godzina}" if godzina else ""
        info_priorytet = f" | Priorytet: {priorytet}" if priorytet != "Brak" else ""
        
        Lista_zadan.insert("end", f"{id} | {skrot} ({data}){info_priorytet}{info_godzina}")

        if priorytet in PRIORITY_COLORS:
            Lista_zadan.itemconfig(i, {'bg': PRIORITY_COLORS[priorytet], 'fg': 'black'})

def pokaz_zad(event):
    """Gdy klikniesz na zadanie, ta funkcja pokaże jego pełną treść i opcje."""
    zaznaczone_idx = Lista_zadan.curselection()
    if zaznaczone_idx:
        id_notki = Lista_zadan.get(zaznaczone_idx[0]).split("|")[0].strip()
        
        cursor.execute("SELECT content, priority, due_time FROM notes WHERE id=?", (id_notki,))
        wynik = cursor.fetchone()
        
        if wynik:
            tresc, priorytet, godzina = wynik
            poletxt.delete("1.0", "end")
            poletxt.insert("1.0", tresc)
            priority_var.set(priorytet if priorytet else "Brak")
            time_entry.delete(0, "end")
            time_entry.insert(0, godzina if godzina else "")

def usun_zadanie():
    """Usuwa zaznaczone zadanie z bazy danych."""
    zaznaczone = Lista_zadan.curselection()
    if zaznaczone:
        id_notki = Lista_zadan.get(zaznaczone[0]).split("|")[0].strip()
        cursor.execute("DELETE FROM notes WHERE id=?", (id_notki,))
        db.commit()
        wyczysc_pole()
        wczytaj_zad()

def wyczysc_pole():
    """Czyści wszystkie pola, żeby można było zacząć pisać od nowa."""
    poletxt.delete("1.0", "end")
    time_entry.delete(0, "end")
    priority_var.set("Brak")

# --- Nagłówek ---
tytul = ctk.CTkLabel(app, text="LYNX Zorganizuj swój dzień 🦊", font=("Segoe UI", 24, "bold"))
tytul.pack(pady=10)

# --- Ramka do wprowadzania danych ---
input_frame = ctk.CTkFrame(app)
input_frame.pack(pady=10, padx=10, fill="x")

ctk.CTkLabel(input_frame, text="Zapisz swoje zadanie tutaj:", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=10)
poletxt = ctk.CTkTextbox(input_frame, width=380, height=130, font=("arial", 13))
poletxt.pack(pady=5, padx=10, fill="x")

# --- Ramka na opcje (godzina i priorytet) ---
options_frame = ctk.CTkFrame(input_frame)
options_frame.pack(pady=5, padx=10, fill="x")

ctk.CTkLabel(options_frame, text="Godzina wykonania (np. 14:30):", font=("Segoe UI", 12)).grid(row=0, column=0, padx=5, sticky="w")
time_entry = ctk.CTkEntry(options_frame, width=150, placeholder_text="HH:MM")
time_entry.grid(row=0, column=1, padx=5, pady=5)

ctk.CTkLabel(options_frame, text="Priorytet:", font=("Segoe UI", 12)).grid(row=0, column=2, padx=5, sticky="w")
priority_var = ctk.StringVar(value="Brak")
priority_options = ["Brak", "Ważne", "Bardzo Ważne", "Ultra Ważne"]
priority_menu = ctk.CTkOptionMenu(options_frame, values=priority_options, variable=priority_var)
priority_menu.grid(row=0, column=3, padx=5, pady=5)

# --- Ramka z przyciskami ---
przyciski_frame = ctk.CTkFrame(app)
przyciski_frame.pack(pady=10)

zapisz_btn = ctk.CTkButton(przyciski_frame, text="💾 Zapisz zadanie", width=120, command=zapisz_zad)
zapisz_btn.grid(row=0, column=0, padx=5)

usun_btn = ctk.CTkButton(przyciski_frame, text="🗑️ Usuń zadanie", fg_color="#D32F2F", hover_color="#B71C1C", width=120, command=usun_zadanie)
usun_btn.grid(row=0, column=1, padx=5)

czysc_btn = ctk.CTkButton(przyciski_frame, text="✨ Wyczyść pola", width=120, command=wyczysc_pole)
czysc_btn.grid(row=0, column=2, padx=5)

odswiez_btn = ctk.CTkButton(przyciski_frame, text="🔄 Odśwież listę", width=120, command=wczytaj_zad)
odswiez_btn.grid(row=0, column=3, padx=5)

# --- Lista zadań ---
lista_frame = ctk.CTkFrame(app)
lista_frame.pack(pady=10, padx=10, fill="both", expand=True)

Lista_zadan = tk.Listbox(
    lista_frame,
    width=60,
    height=15,
    bg="#343638",
    fg="#dce4ee",
    font=("Consolas", 12),
    selectbackground="#1F6AA5",
    selectforeground="white",
    relief="flat",
    borderwidth=0,
    highlightthickness=0
)
Lista_zadan.pack(pady=10, padx=10, fill="both", expand=True)
Lista_zadan.bind("<<ListboxSelect>>", pokaz_zad)

# --- Start ---
wczytaj_zad()
app.mainloop()

# --- Koniec ---
db.close()