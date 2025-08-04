
import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione pagina
st.set_page_config(page_title="UALZ 2025 2026", page_icon="📚", layout="wide")

# Logo e titolo
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo.png", width=100)
with col2:
    st.title("UALZ 2025 2026")
    st.markdown("### Verifica sovrapposizioni corsi")

# Carica i dati da Excel
df = pd.read_excel("Corsi UALZ 2025 2026.xlsx", sheet_name="Foglio1", header=4)
df.columns = [
    "Giorno", "Fascia oraria", "Titolo", "Aula",
    "Ora inizio", "Ora fine", "Data inizio", "Data fine"
]
df.dropna(subset=["Titolo", "Ora inizio", "Ora fine"], inplace=True)

# Rinominare titoli duplicati
counts = {}
titoli_unici = []
for titolo in df['Titolo']:
    if titolo not in counts:
        counts[titolo] = 1
        titoli_unici.append(titolo)
    else:
        counts[titolo] += 1
        titoli_unici.append(f"{titolo} ({counts[titolo]})")
df['Titolo univoco'] = titoli_unici

# Menu a tendina
corso_scelto = st.selectbox("Seleziona un corso:", df['Titolo univoco'])

# Estrai dati del corso selezionato
corso_row = df[df['Titolo univoco'] == corso_scelto].iloc[0]
gor = corso_row['Giorno']
inizio = datetime.strptime(str(corso_row['Ora inizio']), "%H:%M:%S").time()
fine = datetime.strptime(str(corso_row['Ora fine']), "%H:%M:%S").time()

# Mostra info principali del corso
st.subheader("Informazioni corso selezionato")
st.markdown(f"**Titolo**: {corso_row['Titolo']}")
st.markdown(f"**Giorno**: {gor}")
st.markdown(f"**Orario**: {inizio.strftime('%H:%M')} - {fine.strftime('%H:%M')}")
st.markdown(f"**Date**: {corso_row['Data inizio'].date()} → {corso_row['Data fine'].date()}")

# Calcola sovrapposizioni
st.subheader("Corsi in sovrapposizione nello stesso giorno")
conflitti = []
for _, r in df.iterrows():
    if r['Giorno'] != gor:
        continue
    start_r = datetime.strptime(str(r['Ora inizio']), "%H:%M:%S").time()
    end_r = datetime.strptime(str(r['Ora fine']), "%H:%M:%S").time()
    if (start_r < fine and end_r > inizio) and r['Titolo univoco'] != corso_scelto:
        conflitti.append({
            "Titolo": r['Titolo univoco'],
            "Orario": f"{start_r.strftime('%H:%M')} - {end_r.strftime('%H:%M')}",
            "Aula": r['Aula']
        })

if conflitti:
    for c in conflitti:
        st.markdown(f"- **{c['Titolo']}** ({c['Orario']} – {c['Aula']})")
else:
    st.markdown("Nessuna sovrapposizione rilevata.")
