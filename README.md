# Jalkapalloseura-Sovellus

- Sovelluksessa käyttäjät pystyvät etsimään peliseuraa jalkapalloon. Ilmoituksessa lukee missä ja milloin pelivuoro on sekä tarvittava pelaajien määrä
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään ilmoituksia ja muokkaamaan ja poistamaan niitä.
- Käyttäjä näkee sovellukseen lisätyt ilmoitukset.
- Käyttäjä pystyy etsimään ilmoituksia sen perusteella, milloin vuoro on.
- Käyttäjäsivu näyttää, montako ilmoitusta käyttäjä on lähettänyt ja listan ilmoituksista.
- Käyttäjä pystyy valitsemaan ilmoitukselle yhden tai useamman luokittelun (esim. Lämsi-Helsinki, Harrastetaso, 11 vs 11)
- Käyttäjä pystyy ilmoittautumaan pelivuoroon. Ilmoituksessa näytetään, ketkä käyttäjät ovat ilmoittautuneet.

* Tässä pääasiallinen tietokohde on ilmoitus ja toissijainen tietokohde on ilmoittautuminen.

## Sovelluksen asennus

Reposition kloonaus ja siirtyminen projektikansioon:

```bash
git clone <github-repo-url>
cd Jalkapalloseura-Sovellus
```

Aktivointi ja asennus:

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask
```

Tietokannan luonti:

```bash
sqlite3 database.db < schema.sql
```

Käynnistys:

```bash
export FLASK_APP=app.py
flask run
```
