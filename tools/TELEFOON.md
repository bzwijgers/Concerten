# Tivoli ophalen vanaf je telefoon (Samsung, Termux)

Tivoli blokkeert de servers van GitHub, maar niet jouw telefoon. Dit script haalt het programma op jouw
toestel op en zet het in de repository. Daarna verwerkt GitHub het zelf.

## 1. Sleutel maken (eenmalig)
1. GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token.
2. Repository access: alleen `Concerten`. Permissions → Repository permissions → **Contents: Read and write**.
3. Kopieer de sleutel (begint met `github_pat_`).

## 2. Termux installeren
Installeer **Termux** via F-Droid (niet de Play Store-versie). Open Termux en typ:

    pkg update -y && pkg install -y python curl
    export GITHUB_TOKEN=PLAK_HIER_JE_SLEUTEL
    curl -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github.raw" \
      -o tivoli_phone.py https://api.github.com/repos/bzwijgers/Concerten/contents/tools/tivoli_phone.py

## 3. Proefrun
    python3 tivoli_phone.py --dry-run

Dit haalt het programma op zonder iets te uploaden. Je ziet per pagina hoeveel concerten er staan.
Staat er "Gestopt: bot-controle", dan laat Tivoli deze route nu niet door: er is dan niets gedaan.
Meld dat, dan kijken we naar een andere route.

## 4. Echt uploaden
    python3 tivoli_phone.py

Na een minuut of twee staat Tivoli in de agenda (na verversen van de app).

## 5. Elke ochtend automatisch (optioneel)
Installeer **Termux:API** en **Termux:Boot** via F-Droid, en daarna in Termux:

    pkg install -y termux-api
    mkdir -p ~/.termux/boot
    printf '#!/data/data/com.termux/files/usr/bin/sh\nexport GITHUB_TOKEN=PLAK_HIER_JE_SLEUTEL\ncd ~ && python3 tivoli_phone.py\n' > ~/tivoli_run.sh
    chmod +x ~/tivoli_run.sh
    termux-job-scheduler --script ~/tivoli_run.sh --period-ms 86400000 --network any --persisted true

Zet in Android-instellingen de batterij-optimalisatie voor Termux uit, anders slaat Android de taak over.
