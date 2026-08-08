# PV Battery Optimizer

![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-blue)
![Version](https://img.shields.io/badge/version-1.0.0-green)
![License](https://img.shields.io/badge/license-MIT-blue)

Der **PV Battery Optimizer** ist eine intelligente Home-Assistant-Integration, die das Lademanagement deines PV-Speichersystems optimiert. Anstatt den Akku blind zu laden, berechnet diese Integration basierend auf dem Hausverbrauch, der PV-Prognose und Strompreisen den optimalen Ladezeitpunkt und die ideale Ladeleistung.

---

## 🚀 Kernfunktionen

*   **Intelligente Ladestrategie:** Optimiert die Akkuladung für die EEG-Vergütung – lädt intelligent über den Tag verteilt, anstatt den Akku sofort morgens vollzupumpen.
*   **Wetter- & Preisbasiert:** Nutzt Sonnenuntergangsdaten und integriert Börsenstrompreise (Nordpool), um bei negativen Preisen proaktiv zu agieren.
*   **Batterieschonung:** Verhindert unnötige Ladezyklen und schont die Zellchemie durch gleichmäßige Ladeprofile.
*   **Automatisierte Steuerung:** Kann die berechnete Ladeleistung direkt an deinen Wechselrichter senden (konfigurierbar).
*   **Volle Transparenz:** Liefert zahlreiche Sensoren für deine Dashboards (SOC, PV-Überschuss, erreichte Ladung, verbleibende Energie heute, etc.).

---

## ⚡ Unterstützte Strategien

| Strategie | Status | Beschreibung |
| :--- | :--- | :--- |
| **EEG-Optimierung** | ✅ Voll implementiert | Maximiert Eigenverbrauch & Netzstabilität |
| **Eigenverbrauch** | 🚧 In Planung | Priorisiert sofortige Eigenverbrauchsdeckung |
| **Dynamische Preise** | 🚧 In Planung | Ladung bei günstigen/negativen Strompreisen |
| **Netzdienlichkeit** | 🚧 In Planung | Vermeidung von Einspeisespitzen |

---

## 📥 Installation

1.  Öffne **HACS** in deinem Home Assistant.
2.  Klicke auf die drei Punkte oben rechts -> **Benutzerdefinierte Repositories**.
3.  Gib die URL dieses Repositorys ein und wähle **Integration** als Typ.
4.  Klicke auf **Installieren**.
5.  Starte Home Assistant neu.
6.  Gehe zu **Einstellungen** -> **Geräte & Dienste** -> **Integration hinzufügen** und suche nach „PV Battery Optimizer“.

---

## 📊 Konfiguration

Nach der Installation führt dich ein Einrichtungs-Assistent durch drei logische Schritte:

1.  **Sensoren & Strategie:** Verknüpfung der benötigten Entitäten (SOC, Hausverbrauch, PV-Leistung etc.).
2.  **Batterie-Parameter:** Definition von Kapazität, Min/Max-SOC und Ladeeffizienz.
3.  **Strategie-Parameter:** Feinabstimmung für die gewählte Optimierungsstrategie.

---

## 📝 Support & Mitwirken

Hast du Fragen, Verbesserungsvorschläge oder ein Problem gefunden?
*   Öffne ein **[Issue](https://github.com/DEIN_GITHUB_USER/pv-battery-optimizer/issues)** in diesem Repository.
*   Beiträge (Pull Requests) sind jederzeit willkommen!

---
*Entwickelt mit ❤️ für eine intelligentere Energiewende zu Hause.*
