# Changelog

All notable changes to this project will be documented in this file

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2021-02-25

### Fixed

- Added --pretend and --verbose to README

## [0.2.1] - 2021-02-25

### Changed

- Automatic versioning from tags in `setup.py`

## [0.2.0] - 2021-02-25

### Added

- `--pretend` option to not save any changes/updates
- `--verbose` for slightly more information

### Changed

- Chromedriver is now installed automatically. No need to download and install it manually every time 🙂
- Made it easier to see which mods are updated and which are not, especially together with --pretend.

### Removed

- User configuration file `config.py`. Was only used for chromedriver location.

## [0.1.0] - 2020-11-11

### Added

- Syntax checking for mods supplied during arguments
- Keep information about mod (site and alias) even when it's removed
- List all installed mods (and their settings) with `minecraft-mod-manager list`

### Changed

- Faster runs during configure. Only initialize the webdriver when necessary
- DB structure

### Removed

- --pretend, hadn't been implemented
- --verbose, not necessary, better to use --debug instead

## [0.0.2] - 2020-11-10

### Added

- Get possible mod name not only from the `.jar` file but the filename as well
- Search on CurseForge for all these names and only raise an error if no match was found
- Error message if Curse changes their site (so you might have to update this script)

### Changed

- Print out more of what's happening by default
- Stops the script if a mod wasn't found
- Decrease selenium logging (only log errors)

### Fixed

- Running the script on a Linux device doesn't require a `config.py` file

## [0.0.1] - 2020-11-09

### Added

- Update feature
- Get existing mods in a directory and add `mod_id` from `.jar` file
- Synchronize mod files with the DB (add and remove)
- Get latest version of mod from CurseForge
- Download mod from CurseForge
