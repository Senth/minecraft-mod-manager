# minecraft-mod-manager

[![Latest PyPI version](https://img.shields.io/pypi/v/minecraft-mod-manager.svg)](https://pypi.python.org/pypi/minecraft-mod-manager)

Update mods from CurseForge (and other places in the future) through a simple command.

## Features

- Install mods with `minecraft-mod-manager install mod_name`
- Update all mods with `minecraft-mod-manager update`
- Searches on Modrinth and CurseForge for updates on installed mods
- Filter updates by
  - Stable (default), beta `--beta`, or alpha `--alpha` releases
  - Minecraft version `-v 1.16.4`
  - Fabric/Forge mod `--mod-loader fabric`

## Installation & Requirements

1. Requires at least python 3.8
1. Install with `$ pip install --user minecraft-mod-manager`

## Examples

**Note!** All examples start with `minecraft-mod-manager`, then comes the arguments.

| Arguments                                        | Description                                                                                         |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| `install jei`                                    | Searches for jei on all sites (from Modrinth first). and installs the latest version                |
| `install dynmap=dynmapforge`                     | Install dynmap with slug dynmapforge. Dynmap name on CurseForge is dynmapforge, even for fabric.    |
| `install dynmap=dynmapforge --mod-loader fabric` | Install fabric version of dynmap. Not necessary if you have other fabric mods installed.            |
| `install curse:sodium`                           | By default it searches for all sites, adding `curse:` in front only searches on CurseForge.         |
| `install carpet fabric-api sodium lithium`       | Easily install many mods.                                                                           |
| `update`                                         | Update all mods                                                                                     |
| `update --pretend`                               | Check what will be update. Does not change anything.                                                |
| `update sodium lithium phosphor`                 | Update specific mods                                                                                |
| `update -v "1.16.5"`                             | Updates to latest mod version which works with specified MC version.                                |
| `update -v "1.16.1"`                             | If you upgraded the mods, to a higher version (e.g. snapshot), you can easily downgrade them again. |
| `configure modrith:sodium`                       | Change the download site for a mod                                                                  |
| `carpet=fabric-carpet`                           | Change site slug for a mod                                                                          |
| `configure modrinth:sodium curse:carpet=carpet`  | Easily configure multiple mods at the same time.                                                    |
| `list`                                           | List all installed mods                                                                             |

## Full usage

```
Install or update Minecraft mods from Curseforge.

positional arguments:
  {install,update,configure,list}
                        Install, update, configure, or list mods
  mods
                        The mods to update or configure.
                        If no mods are specified during an update, all mods will be updated.
                        To specify the download site for the mod, put 'curse:' before the mod.
                        E.g. 'curse:litematica'
                        By default it searches all sites for the mod.
                        To configure an slug for the mod, use 'mod_name=SLUG'.
                        E.g. 'dynmap=dynmapforge' must be used to find dynmap on Curse.


minecraft:
  -d DIR, --dir DIR     Location of the mods folder. By default it's the current directory
  -v MINECRAFT_VERSION, --minecraft-version MINECRAFT_VERSION
                        Only update mods to this Minecraft version. Example: -v 1.16.4
  --beta                Allow beta releases of mods
  --alpha               Allow alpha and beta releases of mods
  --mod-loader {fabric,forge}
                        Only install mods that use this mod loader. You rarely need to be
                        this specific. The application figures out for itself which type
                        you'll likely want to install.

logging & help:
  -h, --help            show this help message and exit
  --verbose             Print more massages
  --debug               Turn on debug messages
  --pretend             Only pretend to install/update/configure. Does not change anything
```

## Planned features

- Automatically install dependencies

## Authors

- Matteus Magnusson, senth.wallace@gmail.com
