import streamlit as st
import pandas as pd
from datetime import datetime, time

@st.cache_data
def load_data():
    df = pd.read_excel('UALZ_programma_2025-2026.xlsx')
    df['StartDate'] = pd.to_datetime(df['StartDate'], dayfirst=True).dt.date
    df['EndDate'] = pd.to_datetime(df['EndDate'], dayfirst=True).dt.date
    df['StartTime'] = pd.to_datetime(df['StartTime'], format='%H:%M').dt.time
    df['EndTime'] = pd.to_datetime(df['EndTime'], format='%H:%M').dt.time
    return df

def is_overlap(start1, end1, start2, end2):
    return (start1 < end2) and (start2 < end1)

df = load_data()

st.set_page_config(page_title="UALZ 2025 2026", layout="wide")
st.title("UALZ 2025 2026")

df['menu_option'] = df.apply(lambda r: f"{r['ID']} - {r['Titolo']}", axis=1)
menu_options = sorted(df['menu_option'].unique())
selected = st.selectbox("Seleziona il corso (ID - Titolo):", menu_options)
selected_id = int(selected.split(' - ')[0])
corso_sel = df[df['ID'] == selected_id].iloc[0]

with st.container():
    st.markdown("<h3 style='background-color:#b3d9ff; padding:10px; border-radius:5px;'>Dettagli corso selezionato</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns([1,2])
    with col1:
        st.write(f"**Titolo:** {corso_sel['Titolo']}")
        st.write(f"**ID corso:** {corso_sel['ID']}")
        st.write(f"**Giorno della settimana:** {corso_sel['Day']}")
        st.write(f"**Orario:** {corso_sel['StartTime'].strftime('%H:%M')} - {corso_sel['EndTime'].strftime('%H:%M')}")
    with col2:
        st.write(f"**Date svolgimento:** {corso_sel['StartDate'].strftime('%d/%m/%Y')} - {corso_sel['EndDate'].strftime('%d/%m/%Y')}")
        st.write(f"**Docenti:** {corso_sel['Teacher']}")
        st.write(f"**Sede/Aula:** {corso_sel['Aula']}")

same_day_courses = df[df['Day'] == corso_sel['Day']]

def check_date_overlap(r1_start, r1_end, r2_start, r2_end):
    return not (r1_end < r2_start or r2_end < r1_start)

def course_overlaps(row):
    return (
        is_overlap(corso_sel['StartTime'], corso_sel['EndTime'], row['StartTime'], row['EndTime'])
        and check_date_overlap(corso_sel['StartDate'], corso_sel['EndDate'], row['StartDate'], row['EndDate'])
        and row['ID'] != corso_sel['ID']
    )

overlapping_courses = same_day_courses[same_day_courses.apply(course_overlaps, axis=1)]

with st.container():
    st.markdown("<h3 style='background-color:#ffcccc; padding:10px; border-radius:5px;'>Corsi che si svolgono in sovrapposizione</h3>", unsafe_allow_html=True)
    if overlapping_courses.empty:
        st.write("Nessun corso si svolge in sovrapposizione con il corso selezionato.")
    else:
        st.dataframe(
            overlapping_courses[['Titolo','ID','StartTime','EndTime','StartDate','EndDate','Teacher','Aula']]
            .rename(columns={
                'Titolo':'Titolo',
                'ID':'ID',
                'StartTime':'Inizio',
                'EndTime':'Fine',
                'StartDate':'Dal',
                'EndDate':'Al',
                'Teacher':'Docenti',
                'Aula':'Sede/Aula'
            })
            .sort_values(by='StartTime')
            .reset_index(drop=True),
            height=300,
            use_container_width=True
        )
