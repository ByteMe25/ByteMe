#!/usr/bin/env python3
"""
glossario.py

Legge le parole definite nel glossario LaTeX e, in tutti gli altri file .tex
della repo, sostituisce ogni occorrenza con \gls{parola} dove \gls è
definito come parola con pedice G.

Formato atteso nel glossario:
    \item \textbf{PAROLA}: definizione...

Utilizzo:
    python scripts/glossario.py
"""

import re
import sys
import glob
from pathlib import Path

# ──────────────────────────────────────────────
# CONFIGURAZIONE
# ──────────────────────────────────────────────

# Cartella in cui cercare il glossario
GLOSSARIO_DIR = "src/Documenti_interni"

# Cartella sorgente in cui cercare gli altri .tex
SRC_ROOT = Path("src")

# Comando LaTeX da usare per marcare le parole
# Verrà definito nel preambolo come: \newcommand{\gls}[1]{#1\textsubscript{G}}
COMANDO = "\\gls"

# ──────────────────────────────────────────────
# STEP 0 — Trova il file glossario
# ──────────────────────────────────────────────

def trova_glossario() -> Path:
    risultati = glob.glob(f"{GLOSSARIO_DIR}/Glossario_*.tex")
    if not risultati:
        print(f"❌ Nessun file Glossario_*.tex trovato in {GLOSSARIO_DIR}/")
        sys.exit(1)
    if len(risultati) > 1:
        risultati.sort()
        print(f"⚠️  Trovati più glossari, uso il più recente: {risultati[-1]}")
    glossario = Path(risultati[-1])
    print(f"📖 Glossario rilevato: {glossario}")
    return glossario

# ──────────────────────────────────────────────
# STEP 1 — Estrai le parole dal glossario
# ──────────────────────────────────────────────

def estrai_parole_glossario(path: Path) -> list[str]:
    """
    Cerca righe del tipo:
        \\item \\textbf{PAROLA}: ...
    e restituisce la lista delle parole (conservando il case originale).
    """
    testo = path.read_text(encoding="utf-8")
    pattern = re.compile(r"\\item\s+\\textbf\{([^}]+)\}", re.MULTILINE)
    parole = pattern.findall(testo)

    if not parole:
        print("⚠️  Nessuna parola trovata nel glossario. Controlla il formato.")
        sys.exit(1)

    # Ordina dal più lungo al più corto per evitare sostituzioni parziali
    # es. "API REST" prima di "API"
    parole.sort(key=len, reverse=True)
    print(f"📖 Parole trovate nel glossario ({len(parole)}):")
    for p in parole:
        print(f"   • {p}")
    return parole


# ──────────────────────────────────────────────
# STEP 2 — Normalizza marcature manuali esistenti
# ──────────────────────────────────────────────

def normalizza_marcature_manuali(testo: str, parole: list[str]) -> tuple[str, int]:
    """
    Converte le marcature manuali già presenti nei formati:
        parola\\textsubscript{G}              → \\gls{parola}
        \\textbf{parola}\\textsubscript{G}    → \\textbf{\\gls{parola}}

    Questo evita doppie marcature come \\gls{parola}\\textsubscript{G}.
    """
    totale = 0
    for parola in parole:
        escaped = re.escape(parola)

        # Caso 1: \textbf{parola}\textsubscript{G} → \textbf{\gls{parola}}
        pat_bold = re.compile(
            r"\\textbf\{(" + escaped + r")\}\\textsubscript\{G\}",
            re.IGNORECASE
        )
        def rimpiazza_bold(m, _cmd=COMANDO):
            return f"\\textbf{{{_cmd}{{{m.group(1)}}}}}"
        nuovo, n = pat_bold.subn(rimpiazza_bold, testo)
        if n:
            totale += n
            testo = nuovo

        # Caso 2: parola\textsubscript{G} → \gls{parola}
        pat = re.compile(
            r"\b(" + escaped + r")\\textsubscript\{G\}",
            re.IGNORECASE
        )
        def rimpiazza(m, _cmd=COMANDO):
            return f"{_cmd}{{{m.group(1)}}}"
        nuovo, n = pat.subn(rimpiazza, testo)
        if n:
            totale += n
            testo = nuovo

    return testo, totale


# ──────────────────────────────────────────────
# STEP 3 — Assicura che il preambolo abbia il comando \gls
# ──────────────────────────────────────────────


DEFINIZIONE_COMANDO = r"\newcommand{\gls}[1]{#1\textsubscript{G}}"

def aggiungi_comando_preambolo(testo: str, filepath: Path) -> str:
    """
    Se il file contiene \\documentclass, inserisce la definizione di \\gls
    subito dopo \\documentclass{...} (prima di \\begin{document}).
    Se il comando è già presente, non fa nulla.
    """
    if DEFINIZIONE_COMANDO in testo:
        return testo  # già presente

    pattern = re.compile(r"(\\documentclass(?:\[.*?\])?\{.*?\})", re.DOTALL)
    match = pattern.search(testo)
    if match:
        inserimento = match.group(0) + "\n" + DEFINIZIONE_COMANDO
        testo = testo[:match.start()] + inserimento + testo[match.end():]
        print(f"   ✏️  Comando \\gls aggiunto al preambolo di {filepath.name}")
    # Se non c'è \documentclass (sottofile incluso con \input) non serve aggiungerlo
    return testo


# ──────────────────────────────────────────────
# STEP 3 — Sostituisci le parole nel corpo del testo
# ──────────────────────────────────────────────

# ──────────────────────────────────────────────
# STEP 4 — Sostituisci le parole nel corpo del testo
# ──────────────────────────────────────────────

# Ambienti LaTeX in cui NON bisogna sostituire
AMBIENTI_ESCLUSI = [
    "verbatim", "lstlisting", "minted", "comment",
    "equation", "align", "math",
]

# Comandi LaTeX i cui argomenti non vanno toccati
COMANDI_ESCLUSI = [
    r"\\label", r"\\ref", r"\\cite", r"\\url", r"\\href",
    r"\\includegraphics", r"\\bibliographystyle", r"\\bibliography",
    r"\\newcommand", r"\\renewcommand", r"\\def",
    r"\\gls",      # già marcata
]


def _costruisci_regex_parola(parola: str) -> re.Pattern:
    escaped = re.escape(parola)
    pattern = (
        r"(?<!\\gls\{)"
        r"\b(" + escaped + r")\b"
    )
    return re.compile(pattern, re.IGNORECASE)


def _rimuovi_ambienti_esclusi(testo: str) -> tuple[str, dict]:
    """
    Sostituisce temporaneamente gli ambienti esclusi con placeholder
    in modo che il replace non li tocchi.
    """
    placeholder_map = {}
    contatore = [0]

    def segnaposto(match):
        token = f"PLACEHOLDER_{contatore[0]}_END"
        placeholder_map[token] = match.group(0)
        contatore[0] += 1
        return token

    # Ambienti \begin{...}...\end{...}
    for ambiente in AMBIENTI_ESCLUSI:
        pat = re.compile(
            r"\\begin\{" + re.escape(ambiente) + r"\}.*?\\end\{" + re.escape(ambiente) + r"\}",
            re.DOTALL
        )
        testo = pat.sub(segnaposto, testo)

    # Commenti LaTeX (% ...)
    pat_commento = re.compile(r"(?m)^[ \t]*%.*$")
    testo = pat_commento.sub(segnaposto, testo)

    pat_commento_inline = re.compile(r"(?<!\\)%.*")
    testo = pat_commento_inline.sub(segnaposto, testo)

    # Argomenti dei comandi esclusi
    for cmd in COMANDI_ESCLUSI:
        pat = re.compile(cmd + r"\{[^}]*\}")
        testo = pat.sub(segnaposto, testo)

    return testo, placeholder_map


def _ripristina_placeholder(testo: str, placeholder_map: dict) -> str:
    for token, originale in placeholder_map.items():
        testo = testo.replace(token, originale)
    return testo


def sostituisci_parole(testo: str, parole: list[str]) -> tuple[str, int]:
    """
    Sostituisce le parole del glossario con \\gls{parola}.
    Ritorna il testo modificato e il numero di sostituzioni.
    """
    testo_lavoro, placeholder_map = _rimuovi_ambienti_esclusi(testo)

    totale = 0
    for parola in parole:
        regex = _costruisci_regex_parola(parola)
        def rimpiazza(m, _parola=parola):
            return f"{COMANDO}{{{m.group(1)}}}"
        nuovo, n = regex.subn(rimpiazza, testo_lavoro)
        if n:
            totale += n
            testo_lavoro = nuovo

    testo_finale = _ripristina_placeholder(testo_lavoro, placeholder_map)
    return testo_finale, totale


# ──────────────────────────────────────────────
# STEP 5 — Processa tutti i file .tex
# ──────────────────────────────────────────────

def processa_file(filepath: Path, parole: list[str]) -> None:
    testo_originale = filepath.read_text(encoding="utf-8")

    # Prima normalizza le marcature manuali esistenti (parola\textsubscript{G} → \gls{parola})
    testo_modificato, n_normalizzate = normalizza_marcature_manuali(testo_originale, parole)
    if n_normalizzate:
        print(f"   🔄 {filepath}  →  {n_normalizzate} marcatura/e manuale/i normalizzate")

    # Poi applica le sostituzioni sulle parole ancora non marcate
    testo_modificato, n_sostituzioni = sostituisci_parole(testo_modificato, parole)

    if n_normalizzate > 0 or n_sostituzioni > 0:
        testo_modificato = aggiungi_comando_preambolo(testo_modificato, filepath)

    if testo_modificato != testo_originale:
        filepath.write_text(testo_modificato, encoding="utf-8")
        print(f"   ✅ {filepath}  →  {n_sostituzioni} nuova/e sostituzione/i")
    else:
        print(f"   ⏭️  {filepath}  →  nessuna modifica")


def main():
    print("=" * 60)
    print("🔤  APPLICAZIONE PEDICE GLOSSARIO")
    print("=" * 60)

    # 0. Trova il glossario automaticamente
    glossario_path = trova_glossario()

    # 1. Estrai parole
    parole = estrai_parole_glossario(glossario_path)

    # 2. Trova tutti i .tex tranne il glossario stesso
    tutti_tex = [
        p for p in SRC_ROOT.rglob("*.tex")
        if p.resolve() != glossario_path.resolve()
    ]

    if not tutti_tex:
        print("⚠️  Nessun file .tex trovato in src/")
        sys.exit(0)

    print(f"\n📂 File .tex da processare: {len(tutti_tex)}")
    print("-" * 60)

    # 3. Processa ogni file
    for filepath in sorted(tutti_tex):
        processa_file(filepath, parole)

    print("=" * 60)
    print("🏁  Completato!")


if __name__ == "__main__":
    main()