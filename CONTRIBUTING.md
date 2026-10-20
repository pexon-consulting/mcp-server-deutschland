# Mitmachen

Danke, dass Sie das Projekt verbessern möchten. Am meisten hilft es, wenn Sie neue Server vorschlagen und veraltete Einträge korrigieren.

## Einen Server zur Liste hinzufügen

1. Ergänzen Sie einen Eintrag in [daten/server.yaml](daten/server.yaml). Felder und erlaubte Werte stehen in [scripts/liste_bauen.py](scripts/liste_bauen.py); Pflicht sind unter anderem `name`, `kategorie`, `system`, `url`, `typ`, `herkunft`, `transport`, `auth`, `zugriff`, `lizenz`, `quelle` und `geprueft_am`.
2. `typ: offiziell` nur, wenn der Hersteller des Systems den Server selbst veröffentlicht und eine Seite des Herstellers das belegt. Diese Seite gehört in `quelle`.
3. Schreiben Sie `hinweis` sachlich: was der Server kann, welche Voraussetzungen gelten. Keine Werbung, keine Abwertung anderer Projekte.
4. Erzeugen Sie Liste und README neu und prüfen Sie das Ergebnis:

   ```bash
   python3 -m venv .venv && . .venv/bin/activate
   pip install pyyaml pytest
   python3 scripts/liste_bauen.py
   python3 scripts/liste_bauen.py --check
   python3 -m pytest tests
   ```

5. Öffnen Sie einen Pull Request. Ändern Sie `docs/liste.md` und den Listenblock in der README nicht von Hand, beide werden erzeugt.

Reine Plugins ohne MCP-Server nehmen wir nicht auf. Projekte ohne Lizenz, archivierte oder lange inaktive Projekte nehmen wir nur auf, wenn es für das System kaum Alternativen gibt; das steht dann in `lizenz`, `archiviert` oder `hinweis`, damit Leser es sehen.

## Den DATEV-Server ändern

```bash
cd server/extf-buchungsstapel
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[test]"
pytest
```

Jede neue Prüfregel braucht eine Quelle in [SPEZIFIKATION.md](server/extf-buchungsstapel/SPEZIFIKATION.md) und einen Test. Verwenden Sie in Tests und Beispielen nur erfundene Daten, keine echten Buchungen, Namen oder Kontonummern.

## Texte

- Deutsch mit "Sie", Code-Bezeichner auf Englisch oder wie im bestehenden Code.
- Echte Umlaute (ä, ö, ü, ß), kein Gedankenstrich, sondern ein normaler Bindestrich. Die CI prüft die Gedankenstriche; auf Umlaute achten Sie bitte selbst.
- Angaben zu Produkten mit Datum und Quelle, weil sich MCP-Angebote schnell ändern.

## Verhalten

Bleiben Sie freundlich und sachlich. Beiträge, die andere Menschen herabsetzen, werden nicht übernommen.

## Lizenz

Mit einem Beitrag erklären Sie sich einverstanden, dass er unter der [MIT-Lizenz](LICENSE) des Projekts veröffentlicht wird.
