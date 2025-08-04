
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

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

# Ordinamento alfabetico
df_sorted = df.sort_values(by="Titolo univoco")
corsi_ordinati = df_sorted['Titolo univoco'].unique().tolist()

# Menu a tendina
corso_scelto = st.selectbox("Seleziona un corso:", corsi_ordinati)

# Estrai dati del corso selezionato
corso_row = df[df['Titolo univoco'] == corso_scelto].iloc[0]
gor = corso_row['Giorno']
inizio = datetime.strptime(str(corso_row['Ora inizio']), "%H:%M:%S").time()
fine = datetime.strptime(str(corso_row['Ora fine']), "%H:%M:%S").time()

# Mostra info principali del corso
st.markdown("---")
st.subheader("📄 Informazioni corso selezionato")
info_col1, info_col2 = st.columns(2)
with info_col1:
    st.markdown(f"**Titolo:** {corso_row['Titolo']}")
    st.markdown(f"**Giorno:** {gor}")
with info_col2:
    st.markdown(f"**Orario:** {inizio.strftime('%H:%M')} - {fine.strftime('%H:%M')}")
    st.markdown(f"**Date:** {corso_row['Data inizio'].date()} → {corso_row['Data fine'].date()}")

# Calcola sovrapposizioni
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

# Riquadro riepilogo
st.markdown("---")
if conflitti:
    st.success(f"📌 Trovati {len(conflitti)} corsi in sovrapposizione.")
else:
    st.info("✅ Nessuna sovrapposizione rilevata.")

# Mostra elenco conflitti
if conflitti:
    st.subheader("📋 Elenco corsi in sovrapposizione")
    for c in conflitti:
        st.markdown(f"- **{c['Titolo']}** ({c['Orario']} – {c['Aula']})")

# Pulsante di download
if conflitti:
    df_conflitti = pd.DataFrame(conflitti)

    # Funzione per convertire in Excel
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sovrapposizioni')
        processed_data = output.getvalue()
        return processed_data

    excel_data = to_excel(df_conflitti)
    csv_data = df_conflitti.to_csv(index=False).encode('utf-8')

    st.download_button(label="📥 Scarica in Excel",
                       data=excel_data,
                       file_name="sovrapposizioni.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button(label="📥 Scarica in CSV",
                       data=csv_data,
                       file_name="sovrapposizioni.csv",
                       mime="text/csv")
