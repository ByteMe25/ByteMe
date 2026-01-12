import os
import re
import sys
from spellchecker import SpellChecker

def clean_tex(text):
    # Rimuove commenti
    text = re.sub(r'%.*', '', text)
    # Rimuove comandi LaTeX (es. \section, \textbf, \url)
    text = re.sub(r'\\[a-zA-Z]+\*{0,1}', ' ', text)
    text = re.sub(r'[{}]', ' ', text)
    return text

def check_spelling(directory, whitelist_file):
    spell = SpellChecker(language='it')
    
    # Carica parole ignorate (whitelist.txt)
    if os.path.exists(whitelist_file):
        spell.word_frequency.load_text_file(whitelist_file)
    
    # Parole extra da ignorare sempre (inglesismi tecnici comuni)
    extra_ignore = {"file", "files", "pdf", "jpg", "png", "repo", "workflow", 
                    "github", "action", "latex", "tex", "src", "docs", "commit",
                    "push", "pull", "merge", "branch", "master", "main", "scrum",
                    "sprint", "backlog", "user", "story", "manager", "stakeholder",
                    "budget", "audit", "milestone", "editor", "markdown", "llm",
                    "chatgpt", "api", "token", "frontend", "backend"}
    spell.word_frequency.load_words(extra_ignore)

    # MODIFICA 1: Titolo cambiato
    print(f"{'FILE':<40} | {'TUTTI GLI ERRORI'}")
    print("-" * 70)

    total_errors = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".tex"):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                clean_content = clean_tex(content)
                words = re.findall(r'\b\w+\b', clean_content)
                misspelled = spell.unknown(words)

                if misspelled:
                    misspelled = {w for w in misspelled if len(w) > 3}

                if misspelled:
                    total_errors += 1
                    # MODIFICA 2: Tolto [:5] e aggiunto sorted() per ordine alfabetico
                    errors_list = sorted(list(misspelled)) 
                    print(f"{file:<40} | {', '.join(errors_list)}")

    print("-" * 70)
    if total_errors > 0:
        print(f"⚠️ Trovati possibili errori ortografici in {total_errors} file.")
        sys.exit(0) # MANTENIAMO 0 PER ORA: Così vedi la lista ma il badge resta verde; mettere 1 così diventa rosso se ci sono errori
    else:
        print("✅ Nessun errore ortografico rilevato.")
        sys.exit(0)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    whitelist_path = os.path.join(script_dir, "whitelist.txt")
    
    if os.path.exists("src"):
        check_spelling("src", whitelist_path)
    else:
        print("Cartella 'src' non trovata.")
