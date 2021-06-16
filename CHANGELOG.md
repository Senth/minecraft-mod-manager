# Changelog

All notable changes to this project will be documented in this file

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.3] - 2021-06-16

### Fixed

- Don't remove mods that are up-to-date [#81](https://github.com/Senth/minecraft-mod-manager/issues/81)

## [1.2.2] - 2021-06-15

### Fixed

- Don't use strict JSON parsing from API response [#79](https://github.com/Senth/minecraft-mod-manager/issues/79)

## [1.2.1] - 2021-06-14

### Fixed

- Don't remove mods when running with `--pretend` [#77](https://github.com/Senth/minecraft-mod-manager/issues/77)

## [1.2.0] - 2021-06-14

### Added

- Shorthand command for `minecraft-mod-manager`; you can now use `mcman` or `mmm` instead 🙂 [#57](https://github.com/Senth/minecraft-mod-manager/issues/57)

### Changed

- Can now download from multiple sites [#27](https://github.com/Senth/minecraft-mod-manager/issues/27) and [#68](https://github.com/Senth/minecraft-mod-manager/issues/68)

  - Because of this, `configure` command has changed; slugs are now set per-site and not globally. Example: `configure dynmap=curse:dynmapforge,modrinth:dynmap`

- Show a message why a mod wasn't installed if no versions were available [#58](https://github.com/Senth/minecraft-mod-manager/issues/58)

### Fixed

- Mod information is now loaded properly even if it contains character errors [#60](https://github.com/Senth/minecraft-mod-manager/issues/60)
- Mod information is now loaded properly even if JSON file is not strict [#53](https://github.com/Senth/minecraft-mod-manager/issues/53)
- Doesn't remove old jar file [#54](https://github.com/Senth/minecraft-mod-manager/issues/54)

## [1.1.0] - 2021-05-30

### Added

- Get application version using `--version` [#49](https://github.com/Senth/minecraft-mod-manager/issues/49)

### Fixed

- Can now install mods that don't specify a mod loader [#35](https://github.com/Senth/minecraft-mod-manager/issues/35)

## [1.0.4] - 2021-04-29

### Fixed

- Reinstalling a mod after deleting it manually [#33](https://github.com/Senth/minecraft-mod-manager/issues/33)
- Using `minecraft-mod-manager list` now doesn't display site if none is set
- Using `minecraft-mod-manager list` didn't align properly if no slug was set
- Changed `Alias` to `Slug` when using `list` command (to be consistent)

## [1.0.3] - 2021-04-25

### Fixed

- The published version didn't contain all source code. I.e., it didn't run.

## [1.0.2] - 2021-04-21

### Added

- Improved logging for when installing and updating. Had been removed in application restructure.

### Changed

- Now only downloads from the first site it finds, will make it download updates from all sites later down the line.

### Fixed

- Missing .com in Modrinth url
- Mod didn't do anything when running
- Crash when running
- Fixed crash when CurseForge supplied a date with missing milliseconds

## [1.0.1] - 2021-04-20

### Fixed

- Forgot to add date to CHANGELOG

## [1.0.0] - 2021-04-20

### Added

- Modrinth API support (you can now download mods from modrinth as well) [#11](https://github.com/Senth/minecraft-mod-manager/issues/11)
- Can parse and download Forge mods
- Filter installed mod by Fabric/Forge using `--mod-loader` argument [#18](https://github.com/Senth/minecraft-mod-manager/issues/18)

### Changed

- Restructured the whole project and added lots of test.
- Now uses Curse API instead of Selenium with Chrome, thus you don't have to have Chrome installed and more futureproof.
- Improved README with examples and minimum python requirement

### Fixed

- Mods weren't saved correctly to the DB sometimes.
- Doesn't crash when mod isn't fabric [#17](https://github.com/Senth/minecraft-mod-manager/issues/17)
- No longer can update to a wrong version (switching between fabric/forge version) [#10](https://github.com/Senth/minecraft-mod-manager/issues/10)

## [0.3.1] - 2021-03-02

### Changed

- README: Moved installation above usage, and fixed out-of-date information

## [0.3.0] - 2021-02-26

### Added

- Install feature; can now install mods through `minecraft-mod-manager install modname`

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
