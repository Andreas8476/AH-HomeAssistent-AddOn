# ASKOHEAT+ für Home Assistant

Custom Integration für den [ASKOHEAT+](https://www.askoma.com) PV-Heizstab
(Hersteller Askoma) — liest das Gerät über dessen lokale REST-API aus und
steuert es.

**Status:** Phase 1 (Lesen) + Phase 2 (Steuern) — Sensoren/Binary-Sensoren
sowie drei Number-Entities zum Setzen von Heizstufe/Leistungsvorgabe/
Einspeisewert. Ein Dashboard mit Heizstab-Bildern ist eine spätere Phase.

## Dokumentation

Vollständige, durchnummerierte Doku unter
[`custom_components/askoheat_plus/docs/`](custom_components/askoheat_plus/docs/),
Start bei [`01_ueberblick.md`](custom_components/askoheat_plus/docs/01_ueberblick.md).

## Installation

Siehe [`04_installation.md`](custom_components/askoheat_plus/docs/04_installation.md)
(HACS, manuell, oder lokale Entwicklung per Symlink).

## Repositories

- **[GitLab](https://gitlab.com/SyberAlf/ah-homeassistent-addon)** — Haupt-Repo für die Entwicklung.
- **[GitHub](https://github.com/Andreas8476/AH-HomeAssistent-AddOn)** — öffentlicher Spiegel, nötig für die HACS-Installation (HACS unterstützt nur GitHub). Beide enthalten denselben Stand.

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md).

## Autor

Entwickelt von **Andreas Stegemann** in Zusammenarbeit mit **Claude**
(Anthropic, Modell Sonnet 5) als Coding-Assistent.

Andreas ist Mitarbeiter der **ASKOMA AG** (Bützberg, Schweiz), Hersteller des
ASKOHEAT+ und weiterer Heizelemente/Thermostate für Trink- und Heizungswasser
(u.a. Produktlinien ASKOHEAT+ und ASKOFAMILY+, [askoma.com](https://www.askoma.com)).
Dieses Projekt ist jedoch ein **privates Projekt für den Eigengebrauch** und
**keine offizielle Software der ASKOMA AG** — es basiert auf öffentlich
zugänglicher Herstellerdokumentation der REST-/Modbus-Schnittstelle.

## Lizenz

MIT, siehe [LICENSE](LICENSE).
