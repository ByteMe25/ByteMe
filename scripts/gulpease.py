import sys
import os
import re

def calculate_gulpease(text):
    # Rimuove commenti LaTeX (tutto ciò che è dopo %)
    text = re.sub(r'%.*', '', text)
    # Rimuove comandi LaTeX (es. \section{...}, \textbf{...})
    text = re.sub(r'\\[a-zA-Z]+\*{0,1}', '', text) 
    text = re.sub(r'[{}]', ' ', text)
    
    # Rimuove spazi multipli e newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    if not text:
        return 0

    sentences = len(re.findall(r'[.!?]+', text))
    words = len(re.findall(r'\b\w+\b', text)) 
    letters = len(re.findall(r'[a-zA-Z]', text))
    
    if words == 0: return 0
    
    # Formula di Gulpease
    return 89 + ((300 * sentences) - (10 * letters)) / words

def analyze_directory(directory):
    print(f"{'FILE':<50} | {'GULPEASE':<10} | {'STATO'}")
    print("-" * 75)
    
    failed_files = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".tex"):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    print(f"[WARN] Impossibile leggere {file}, encoding errato.")
                    continue
                    
                index = calculate_gulpease(content)
                status = "OK"
                
                # SOGLIA DI ACCETTABILITÀ (modificabile)
                if index < 40: 
                    status = "BASSO ❌"
                    failed_files += 1
                else:
                    status = "OK ✅"
                
                print(f"{file:<50} | {int(index):<10} | {status}")

    print("-" * 75)
    if failed_files > 0:
        print(f"\n[!] Trovati {failed_files} documenti con indice Gulpease insufficiente.")
        sys.exit(1) # Blocca il workflow se la qualità è bassa: ACTION NON COMPILERÀ
    else:
        print("\n[OK] Tutti i documenti rispettano la soglia di leggibilità.")
        sys.exit(0)

if __name__ == "__main__":
    # Analizza la cartella 'src' dove hai i tuoi .tex
    target_dir = "src"
    if os.path.exists(target_dir):
        analyze_directory(target_dir)
    else:
        print(f"Cartella '{target_dir}' non trovata.")
        sys.exit(0)
