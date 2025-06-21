# Changelog

## [Unreleased]

### Added
- Integration von F5-TTS als neue TTS-Engine:
  - Neue Funktion `segments_f5_tts`, die das F5-TTS Docker-API (Standard: `http://localhost:5000/api/tts`) ansteuert.
  - Anpassung der Pattern- und Routing-Logik in `audio_segmentation_to_voice` für `"* F5-TTS"`-TTS-Namen.
  - TTS-Auswahl per `"de-DE F5-TTS"`, `"en-US F5-TTS"` etc. möglich.
- Hinweis: Für die Nutzung wird ein laufender F5-TTS Docker-Container benötigt.

### Changed
- Keine weiteren Änderungen.

### Fixed
- Keine Korrekturen.

---