"""
Streamlit web app per la verifica della sovrapposizione dei corsi UALZ

Questa versione è adattata per funzionare con il file generato dallo
scraping (`UALZ_completo.xlsx`), che contiene un'unica colonna
`TimeRange` con gli orari. Il caricamento dei dati suddivide
automaticamente `TimeRange` in `StartTime` ed `EndTime` se queste
colonne non esistono già. Inoltre il menu a tendina elenca i corsi
ordinati alfabeticamente per titolo ma mostra sia l'ID sia il nome.

Per eseguire l'app: `streamlit run ualz_app.py`
"""

import streamlit as st
import pandas as pd
from datetime import time
from typing import Optional


@st.cache_data
def load_data(filename: str = "UALZ_completo.xlsx") -> pd.DataFrame:
    """Carica i dati dal file Excel specificato.

    Il file deve contenere almeno le colonne:
    - ID
    - CourseTitle
    - Day (giorno della settimana)
    - StartDate
    - EndDate
    - Teacher
    - Aula

    Se nel file non sono presenti le colonne `StartTime` ed `EndTime`,
    ma esiste `TimeRange`, questa funzione proverà a estrarle
    suddividendo la stringa in ore di inizio e fine. Gli orari nel
    dataset possono usare il punto come separatore dei minuti (es.
    "10.00"). Verranno convertiti nel formato `HH:MM`.

    Restituisce un DataFrame pronto per l'utilizzo nell'app.
    """
    df = pd.read_excel(filename)

    # Se TimeRange esiste e StartTime/EndTime no, suddividiamo gli orari
    if "TimeRange" in df.columns and (
        "StartTime" not in df.columns or "EndTime" not in df.columns
    ):
        def parse_time_range(range_str: Optional[str]) -> pd.Series:
            """Estrae orari di inizio e fine da una stringa di intervallo.

            Accetta formati come:
            - "10.00 12.00"
            - "10.00-12.00"
            - "10.00 alle 12.00"

            Restituisce una serie con chiavi 'StartTime' e 'EndTime'.
            """
            if pd.isna(range_str) or str(range_str).strip() == "":
                return pd.Series({"StartTime": None, "EndTime": None})
            s = str(range_str)
            # Sostituisce 'alle' e 'dalle' con spazi e '-' con spazio
            s = s.replace("alle", "").replace("dalle", "").replace("-", " ")
            # uniforma il separatore minuto
            s = s.replace(".", ":")
            parts = s.split()
            # Trova le prime due occorrenze che contengono ':'
            times = [p for p in parts if ":" in p]
            if len(times) >= 2:
                start = times[0]
                end = times[1]
            elif len(times) == 1:
                # Se c'è solo un tempo, tentativo di dedurre fine ignoto
                start = times[0]
                end = None
            else:
                start = end = None
            return pd.Series({"StartTime": start, "EndTime": end})

        time_split = df["TimeRange"].apply(parse_time_range)
        df = pd.concat([df, time_split], axis=1)

    # Conversione delle date (dayfirst per il formato italiano)
    if "StartDate" in df.columns:
        df["StartDate"] = pd.to_datetime(
            df["StartDate"], errors="coerce", dayfirst=True
        ).dt.date
    if "EndDate" in df.columns:
        df["EndDate"] = pd.to_datetime(
            df["EndDate"], errors="coerce", dayfirst=True
        ).dt.date

    # Conversione degli orari
    for col in ["StartTime", "EndTime"]:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col], errors="coerce", format="%H:%M"
            ).dt.time

    # Normalizza l'ID a stringa per confronti più facili
    if "ID" in df.columns:
        df["ID"] = df["ID"].astype(str)

    return df


def is_overlap(start1: time, end1: time, start2: time, end2: time) -> bool:
    """Verifica se due intervalli di tempo si sovrappongono."""
    # Se uno degli orari è mancante, non consideriamo sovrapposizione
    if pd.isna(start1) or pd.isna(end1) or pd.isna(start2) or pd.isna(end2):
        return False
    return (start1 < end2) and (start2 < end1)


def check_date_overlap(s1: Optional[pd.Timestamp], e1: Optional[pd.Timestamp],
                       s2: Optional[pd.Timestamp], e2: Optional[pd.Timestamp]) -> bool:
    """Verifica se due intervalli di date si sovrappongono."""
    # Se una data è mancante, assumiamo che si sovrapponga sempre
    if pd.isna(s1) or pd.isna(e1) or pd.isna(s2) or pd.isna(e2):
        return True
    return not (e1 < s2 or e2 < s1)


def main():
    """Funzione principale per costruire l'interfaccia Streamlit."""
    # Carica i dati
    df = load_data()

    st.set_page_config(page_title="UALZ 2025 2026", layout="wide")
    st.title("UALZ 2025 2026")

    # Prepara il menu a tendina: ordina alfabeticamente per titolo ma
    # visualizza anche l'ID
    if {"ID", "CourseTitle"}.issubset(df.columns):
        menu_df = (
            df[["ID", "CourseTitle"]]
            .drop_duplicates()
            .sort_values(by="CourseTitle")
        )
        menu_options = [
            f"{row['ID']} - {row['CourseTitle']}"
            for _, row in menu_df.iterrows()
        ]
        selected = st.selectbox(
            "Seleziona il corso (ID - Titolo):", menu_options
        )
        selected_id = selected.split(" - ")[0]
        corso_sel = df[df["ID"] == selected_id].iloc[0]
    else:
        st.error(
            "Il file dati non contiene le colonne ID e CourseTitle richieste."
        )
        return

    # Riquadro con i dettagli del corso selezionato
    with st.container():
        st.markdown(
            """<h3 style='background-color:#b3d9ff;
            padding:10px; border-radius:5px;'>Dettagli corso selezionato</h3>""",
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write(f"**Titolo:** {corso_sel.get('CourseTitle', '')}")
            st.write(f"**ID corso:** {corso_sel.get('ID', '')}")
            st.write(f"**Giorno della settimana:** {corso_sel.get('Day', '')}")
            if not pd.isna(corso_sel.get('StartTime')) and not pd.isna(corso_sel.get('EndTime')):
                st.write(
                    f"**Orario:** {corso_sel['StartTime'].strftime('%H:%M')} - "
                    f"{corso_sel['EndTime'].strftime('%H:%M')}"
                )
            else:
                st.write("**Orario:** non specificato")
        with col2:
            if not pd.isna(corso_sel.get('StartDate')) and not pd.isna(corso_sel.get('EndDate')):
                st.write(
                    f"**Date svolgimento:** "
                    f"{corso_sel['StartDate'].strftime('%d/%m/%Y')} - "
                    f"{corso_sel['EndDate'].strftime('%d/%m/%Y')}"
                )
            st.write(f"**Docenti:** {corso_sel.get('Teacher', '')}")
            st.write(f"**Sede/Aula:** {corso_sel.get('Aula', '')}")

    # Filtra i corsi dello stesso giorno
    if "Day" not in df.columns:
        st.error("La colonna 'Day' è mancante nel dataset.")
        return
    same_day = df[df["Day"] == corso_sel["Day"]]

    # Trova i corsi sovrapposti per orario e periodo
    def overlaps(row: pd.Series) -> bool:
        return (
            row["ID"] != corso_sel["ID"]
            and is_overlap(
                corso_sel["StartTime"], corso_sel["EndTime"],
                row["StartTime"], row["EndTime"]
            )
            and check_date_overlap(
                corso_sel["StartDate"], corso_sel["EndDate"],
                row["StartDate"], row["EndDate"]
            )
        )

    overlapping = same_day[same_day.apply(overlaps, axis=1)]

    # Riquadro con i corsi sovrapposti
    with st.container():
        st.markdown(
            """<h3 style='background-color:#ffcccc;
            padding:10px; border-radius:5px;'>Corsi che si svolgono in sovrapposizione</h3>""",
            unsafe_allow_html=True,
        )
        if overlapping.empty:
            st.write(
                "Nessun corso si svolge in sovrapposizione con il corso selezionato."
            )
        else:
            cols_to_show = [
                "CourseTitle", "ID", "StartTime", "EndTime", "StartDate",
                "EndDate", "Teacher", "Aula"
            ]
            # Rinomina le colonne per la tabella
            rename_map = {
                "CourseTitle": "Titolo",
                "ID": "ID",
                "StartTime": "Inizio",
                "EndTime": "Fine",
                "StartDate": "Dal",
                "EndDate": "Al",
                "Teacher": "Docenti",
                "Aula": "Sede/Aula",
            }
            df_over = overlapping[cols_to_show].rename(columns=rename_map)
            # Ordina per orario di inizio
            df_over = df_over.sort_values(by="Inizio").reset_index(drop=True)
            st.dataframe(df_over, height=300, use_container_width=True)


if __name__ == "__main__":
    main()