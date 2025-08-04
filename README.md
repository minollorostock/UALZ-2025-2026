
# UALZ 2025 2026 Web App

Questa web app consente di selezionare un corso UALZ e verificare eventuali sovrapposizioni orarie con altri corsi nello stesso giorno.

## Pubblicazione su Streamlit Cloud (senza riga di comando)

1. Vai su [GitHub](https://github.com) e crea un nuovo repository vuoto (pubblico o privato).
2. Scarica e scompatta questo pacchetto `.zip` sul tuo computer.
3. Carica tutti i file del pacchetto nel repository (usando **Upload files** su GitHub).
4. Vai su [Streamlit Cloud](https://streamlit.io/cloud) ed effettua l'accesso con GitHub.
5. Clicca su **New app** e seleziona il repository caricato.
6. Imposta come **Main file path**: `ualz_app.py`
7. Premi **Deploy**.

L'app sarà pubblicata online con un link pubblico, ad esempio:
```
https://ualz-app-username.streamlit.app
```

## Requisiti
- `streamlit`
- `pandas`
- `openpyxl`
