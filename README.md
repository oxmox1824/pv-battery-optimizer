PV Battery Optimizer
Der PV Battery Optimizer ist eine intelligente Home-Assistant-Integration, die das Lademanagement deines PV-Speichersystems optimiert. Anstatt den Akku blind zu laden, berechnet diese Integration basierend auf dem Hausverbrauch, der PV-Prognose und Börsenstrompreisen den optimalen Ladezeitpunkt und die ideale Ladeleistung.

🚀 Kernfunktionen
Intelligente Ladestrategie: Optimiert die Akkuladung für die EEG-Vergütung – lädt intelligent über den Tag verteilt, anstatt den Akku sofort morgens vollzupumpen.

Wetter- & Preisbasiert: Nutzt Sonnenuntergangsdaten und integriert optional Börsenstrompreise (Nordpool), um bei negativen Preisen proaktiv zu agieren.

Batterieschonung: Verhindert unnötige Ladezyklen und schont die Zellchemie durch gleichmäßige Ladeprofile.

Automatisierte Steuerung: Kann die berechnete Ladeleistung direkt an deinen Wechselrichter senden (konfigurierbar).

Volle Transparenz: Liefert eine Vielzahl an Sensoren für Dashboards (SOC, PV-Überschuss, erreichte Ladung, verbleibende Energie heute, etc.).

⚡ Unterstützte Strategien
Derzeit voll implementiert:

EEG-Vergütung optimieren: Maximiert den Eigenverbrauch und stellt sicher, dass der Speicher netzdienlich arbeitet und jederzeit entladefähig bleibt.

In Vorbereitung (zukünftige Strategien):

Eigenverbrauch maximieren

Dynamische Preise nutzen (z.B. Tibber/Nordpool)

Netzdienliches Verhalten

🛠 Voraussetzungen
Home Assistant (neueste Version empfohlen).

HACS (Home Assistant Community Store) installiert.

Zugriff auf die Sensoren deiner PV-Anlage (SOC, Hausverbrauch, PV-Leistung).

Optional: Eine Entität zur Steuerung der Ladeleistung (z. B. ein number-Sensor deines Wechselrichters).

📥 Installation
Öffne HACS in Home Assistant.

Klicke auf die drei Punkte oben rechts -> Benutzerdefinierte Repositories.

Gib die URL dieses Repositorys ein und wähle Integration als Typ.

Klicke auf Installieren.

Starte Home Assistant neu.

Gehe zu Einstellungen -> Geräte & Dienste -> Integration hinzufügen und suche nach „PV Battery Optimizer“.

📊 Konfiguration
Nach der Installation führt dich ein Einrichtungs-Assistent durch drei logische Schritte:

Sensoren & Strategie: Verknüpfung der benötigten Entitäten.

Batterie-Parameter: Definition von Kapazität, Min/Max-SOC und Ladeeffizienz.

Strategie-Parameter: Feinabstimmung für die gewählte Optimierungsstrategie.

📝 Support & Mitwirken
Hast du Fragen, Verbesserungsvorschläge oder ein Problem gefunden?

Öffne ein Issue in diesem Repository.

Beiträge (Pull Requests) sind jederzeit willkommen!

Entwickelt mit ❤️ für eine intelligentere Energiewende zu Hause.
