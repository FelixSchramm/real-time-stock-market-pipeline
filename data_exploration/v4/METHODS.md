# V4 – Definitionen, Datenstand und Grenzen

## Quellen und Reproduzierbarkeit

- Yahoo Finance über yfinance 1.7.0: ein gemeinsam abgerufener Snapshot für
  sämtliche Diagramme und Varianten. Abrufdatum steht in jedem Bild und in
  `manifest.json`; Kurs- und Berichtsperioden stehen getrennt im Diagramm.
- Der mitgelieferte Stand wurde am **01.11.2026 um 22:50 UTC** abgerufen;
  jüngster Aktienhandelstag ist der **30.10.2026**. Eine Galerieöffnung holt
  keine neuen Daten. `generate.py --refresh` erzeugt eine neue Momentaufnahme.
- [Microsoft Annual Report 2026](https://www.microsoft.com/investor/reports/ar26/index.html),
  Note 18: manuell geprüfte Segmentdaten. Die Daten von 2024–2026 stammen
  aus einer gemeinsamen Berichtsversion; Zuordnung und Quelle in `research.md`.
- Keine erfundenen Ersatzdaten. Fehlen für ein Diagramm erforderliche Felder,
  schlägt die Generierung dieses Diagramms sichtbar fehl. `manifest.json`
  nennt Abruf-/Renderfehler. Nullwerte ersetzen keine fehlenden Fundamentaldaten.
- Der lokale API-Cache ist nicht versioniert. Bilder, Methodik, kleine belegte
  Segmentauswertung und Datum sind versioniert. Yahoo kann vergangene Daten
  revidieren; erneuter Abruf ist deshalb nicht zwangsläufig pixelidentisch.

## Kurse und Vergleichbarkeit

Die freigegebene Aktienauswahl bleibt ORCL, MSFT, 9988.HK und SAP.DE.
Keine Mengen, Gewichte, Einstandswerte oder privaten Portfolioquellen.

- Kursansichten verwenden explizit `auto_adjust=False`, `Close` / OHLC.
- Gesamtrenditevergleiche verwenden `Adj Close` als Näherung einer Bruttorendite
  mit Dividenden; persönliche Steuern, Gebühren und Reinvestitionskosten fehlen.
- Alle Vergleiche haben gemeinsame Start- und Endtage des letzten Jahres.
  Native Handelstage bleiben für Volatilität und Drawdown erhalten; der
  indexierte Linienvergleich nutzt gemeinsame Termine. Deshalb kann der
  Jahresverlust in der Karte minimal vom Drawdown auf gemeinsamen Terminen
  abweichen. Innerhalb der Version gilt überall dieselbe Währung/Renditewahl.
- HKD wird durch USDHKD=X geteilt, EUR mit EURUSD=X in USD umgerechnet.
  Für EUR-Darstellung wird anschließend durch EURUSD=X geteilt. Nur FX-Lücken
  werden aus vorherigen Beobachtungen bis maximal sieben Kalendertage gefüllt.
  Unterschiedliche Börsenschlusszeiten sind nicht intraday synchronisiert.
- Reine Kursbenchmarks: ^GSPC und ^NDX. Gesamtrendite-Näherung: SPY und QQQ
  als investierbare Index-Proxies inklusive Ausschüttungen; Tracking und
  Fondskosten können von einer offiziellen Total-Return-Indexserie abweichen.
- Monatsrendite = letzter Kurs im vollständigen Monat / letzter Kurs im
  Vormonat − 1; kein aufgefüllter Aktienkurs. Angezeigt werden zwölf Monate.
- Volatilität = Stichprobenstandardabweichung täglicher Log-Renditen × √252.
- Drawdown-Linie: Kurs / laufendes Hoch der geladenen zehn Jahre − 1.
  Karte: maximaler Drawdown **innerhalb** des gemeinsamen Jahreszeitraums,
  außerdem Kalendertage seit dem letzten beobachteten Zehnjahreshoch.
  Das ist kein Insolvenzrisiko und kein garantiertes Allzeithoch.

## Berichte und Unternehmensqualität

- Beträge in USD; Jahres- und Quartalsabschlüsse werden getrennt ausgewiesen.
  Microsoft-Geschäftsjahresende Juni. Abweichende Währung stoppt den Renderer.
- TTM summiert nur vier vollständige, zeitlich aufeinanderfolgende Quartale.
- FCF = operativer Cashflow − absoluter Cash-Capex. Anbieter-FCF wird dagegen
  auf Plausibilität geprüft. Cash-Capex umfasst keine vollständig geschätzten
  Erhaltungsinvestitionen und nicht automatisch alle Leasingverpflichtungen.
- ROIC = Operating Income × (1 − Tax Provision / Pretax Income) / mittleres
  Invested Capital aus Anfang und Ende des Geschäftsjahrs. Steuerquote nur
  bei positivem Vorsteuerergebnis und 0–100 %; Kapital muss positiv und die
  Vorjahresperiode vorhanden sein. Yahoo-Definition inklusive Goodwill;
  keine eigene F&E-Aktivierung oder Normalisierung von Sondereffekten.
- Bilanz-Nettofinanzschulden-Proxy = Total Debt − Cash/Cash Equivalents/Short
  Term Investments. Leasing wird separat genannt und nicht doppelt addiert.
  Zinsdeckung = operatives Ergebnis / positiver Bruttozinsaufwand.
- FCF je Aktie verwendet **verwässerte durchschnittliche Aktien** der
  passenden Gewinnperiode, keine aktuelle Stichtagszahl als historischen Nenner.
- Cashflow-Qualität zeigt Aktienvergütung und Working-Capital-Cash-Effekt.
  Ein pauschaler erneuter Abzug von SBC vom bereits belasteten Gewinn wäre
  falsch. Rückkäufe und Verwässerung müssen zusammen interpretiert werden.
- Kapitalallokation zeigt Bruttoverwendungen nach Capex gegenüber FCF sowie
  Schuldenaufnahme/-tilgung separat. Es ist keine vollständige Cashflow-Identität.
- Dividendendeckung nutzt jährliche ausgeschüttete Gesamtbeträge / Gewinn
  beziehungsweise FCF. TTM-Dividendenrendite verwendet tatsächliche Ex-Tage
  innerhalb eines Kalenderjahrs, nicht die letzte Rate × 4.

## Erwartungen und Bewertung

- Earnings-EPS stammen aus Yahoo Earnings und sind nicht ohne Prüfung mit
  GAAP-Diluted-EPS gleichzusetzen. Nachbörsliche EPS werden erst am Folgetag
  im rekonstruierten KGV wirksam. Fehlende/negative EPS ergeben kein KGV.
- EPS-Reaktion: erste Handelssitzung nach Veröffentlichung; Microsoft meldet
  üblicherweise nachbörslich. Zusätzlich wird die SPY-Rendite abgezogen.
  Das ist eine einfache Renditedifferenz, keine vollständige Faktormodellanalyse.
- Der KGV-Median beschreibt Vergangenheit, kein Kursziel. Anbieter-KGV,
  Forward P/E und EV/EBITDA haben unterschiedliche Grundlagen.
- Schätzspannen sind Min/Max-Analystenschätzungen, keine Konfidenzintervalle.
  EPS-Trend enthält 7/30/60/90-Tage-Rückblicke des aktuellen Snapshots und ist
  kein selbst archivierter täglicher Point-in-time-Datensatz. Für echte
  Langzeitanalyse künftig datierte Snapshots außerhalb des Git-Repos speichern.
- Reverse DCF: zehn explizite Jahre, danach 2,5 % ewiges Wachstum;
  Eigenkapitalrendite 8–12 %, konstante aktuelle Aktienanzahl. Basis ist letzter
  Jahres-CFO minus Cash-Capex als vereinfachter Eigenkapital-Cashflow-Proxy.
  Weder neue Verschuldung noch Verwässerung werden modelliert. Da auf
  Eigenkapitalebene gerechnet wird, wird nicht zusätzlich Nettoschuld abgezogen.
  Die Heatmap zeigt USD je Aktie; Braun liegt unter, Grün über dem aktuellen
  Kurs. Keine geschätzten Owner Earnings, kein Modell von Garantierenditen.
  Langfristiges Wachstum, Capex, Terminalwert und Discount Rate dominieren das
  Ergebnis. Gewünschte Annahmen sind in `business.reverse_dcf` ausdrücklich
  sichtbar; das Diagramm ist eine Szenarioanalyse, keine Kaufempfehlung.

## Insider, Eigentümer, Optionen

- Analysten-Kurszielmeldungen sind einzelne Veröffentlichungen. Historischer
  Konsens wird daraus nicht konstruiert. Tabelle nach Analyst filterbar.
- Insider: Transaktionstext bestimmt Kauf/Verkauf/Sonstige. Fehlende oder
  Nullwerte bleiben in der Detailtabelle. Verkaufspläne, persönliche Steuern
  und verbleibende Beteiligungen sind nicht aus diesen Meldungen ableitbar.
- Institutionen: Anteil und relative Bestandsänderung in getrennten Spalten;
  Meldedatum sichtbar. Indexfondsbestände sind kein Qualitätssignal.
- Optionen: Calls ±20 % vom Spot; Bid > 0; Ask ≥ Bid; relativer Spread ≤20 %;
  Open Interest ≥10; letzter Handel höchstens drei Kalendertage alt; IV >1 %
  bis 300 %. Unabhängige Quote-Zeitstempel fehlen. Auch gefilterte Quotes
  können außerhalb der Handelszeit veraltet sein. Punkte statt Glättung;
  fehlende Daten werden nicht mit künstlichen Optionspreisen ersetzt.

## Noch offene Unternehmensfragen

Das Dashboard ergänzt Primärquellen, ersetzt sie aber nicht: Erhaltungs-Capex,
Vertragsbindung, Preis/Mengen-Effekte, organisches Wachstum, Managementanreize,
Schuldenfälligkeiten und mindestens zehn Jahre Fundamentaldaten bleiben
Rechercheaufgaben. `research.md` trennt belegte Segmentfakten von Hypothesen
über Wettbewerbsvorteile. Es gibt absichtlich keinen universellen Buffett-Score.
