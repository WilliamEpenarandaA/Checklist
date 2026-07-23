# Changelog

All important changes will be documented here.

## [2.0.0] 2026-0?-??
### Changed
- **Complete Module Refactor**. Overhauled the core architecture to a layered architecture to ease maintain and develop.
- Core functions are divided in a smaller functions with unique responsability to reduce coupling.
- Environment variables are grouped in an unique entry point.

### Performance
- Reduce memory consumption by 30% during dataframe operations.
- Decreased execution times by 92%. Passing from 6 seconds to 0.5 seconds.

### Added
- +d. Re-validate stations status after a specified time interval in seconds.

### Removed
- +n. Number of process to use in parallel. 
- ++wave. Compute delays from last connection datetime from stations not tracked by slinktool. 
- Default values of last connection datetime in the cases when the station is not tracked by slinktool, **1970-01-01 00:00:00**, and when a station has no data stored in the actual year, **one year and one day before the current time**.

## [1.3.3] 2026-07-17
### Added
- Option to run checklist in server .95 

## [1.3.2] 2026-03-26
### Added
- Option to run checklist in server .91 

## [1.3.1] 2026-02-05
### Deprecated
- Eliminate AUA1 station from checklist.

## [1.3.0] 2025-12-23
### Added
- Feature to run checklist in the others servers of data adquisition. 

## [1.2.2] 2025-12-09
## Added
- New parameter to define channel code in shared national and international stations.
- GUAP station. 

## [1.2.1] 2025-10-23
### Changed
- Dispĺay color for stations not tracked by slinktool module.

### Fixed
- Error with stations with similar code names.

## [1.2.0] 2025-10-06
### Added
- Enable Paralelization option.

## [1.1.0] 2025-09-27
### Added
- New waveform module.
- Server options. 

## [1.0.1] 2025-09-24
### Added
- Colorful output display in terminal.

## [1.0.0] - 2025-09-09
### Added
- Initial public release.
