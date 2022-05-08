# mcman/mmm (minecraft-mod-manager)

[![python](https://img.shields.io/pypi/pyversions/minecraft-mod-manager.svg)](https://pypi.python.org/pypi/minecraft-mod-manager)
[![Latest PyPI version](https://img.shields.io/pypi/v/minecraft-mod-manager.svg)](https://pypi.python.org/pypi/minecraft-mod-manager)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/Senth/minecraft-mod-manager.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Senth/minecraft-mod-manager/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Senth/minecraft-mod-manager.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Senth/minecraft-mod-manager/context:python)

Install and update mods from ~~CurseForge~~ and Modrinth through a simple command.

## News — CurseForge support disabled (hopefully only for now) (2022-05-08)

Hi everyone!

I'm not sure if you're aware, Overwolf will tomorrow disable the old API for CurseForge which is used by mcman.

The old API that mcman used is sort of in a gray area legally.
But on a positive note, Overwolf has decided to open up the new API.
Albeit it comes with some limitations; not all mods can be downloaded from 3rd party apps.

I just applied for an API key for the new API, so hopefully it gets accepted.
For the mods that can't be downloaded I plan to link directly to the CurseForge page for easier manual download.

The Overwolf client has also become a lot better with more support, but still lacks official linux and OSX support.

As a server owner though, it requires a bit of changes to how you update the mods.
A tip is to sync your mods folder with Dropbox, that makes it a lot easier.

This will mean that CurseForge mods will be unavailable for some time.
The change in mcman will only take ~4 hours with updating tests.
The issue is keeping the API key safe.
I have some ideas but it will take time to develop and I also need to check with the
Overwolf team that it's legally possible.

Anyway, thanks for all the support!
Hopefully we can get mcman up and running again with CurseForge support 🙂

If it's not accepted, thank you for all the support so far!

Cheers,
Senth

_[(News Archive)](./NEWS.md)_

## Features

- Install mods with `minecraft-mod-manager install mod_name`
- Update all mods with `minecraft-mod-manager update`, `mcman update` or `mmm update`
- Searches on CurseForge and Modrinth for updates on installed mods
- Filter updates by
  - Stable (default), beta `--beta`, or alpha `--alpha` releases
  - Minecraft version `-v 1.16.4`
  - Fabric/Forge mod `--mod-loader fabric`

## Installation/Upgrade & Requirements

1. Requires at least python 3.8
1. Install/Upgrade with `$ pip install --user --upgrade minecraft-mod-manager`

## Examples

**Note!** All examples start with `minecraft-mod-manager`, `mcman` or `mmm`
(shorthand commands) then comes the arguments.

| Arguments                                       | Description                                                                                         |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `install jei`                                   | Searches for jei on all sites and installs the latest version.                                      |
| `install sodium=modrinth`                       | Install Sodium specifically from modrinth.                                                          |
| `install dynmap=curse:dynmapforge`              | Install dynmap with slug dynmapforge on Curse.                                                      |
| `install sodium=modrinth --mod-loader fabric`   | Install fabric version of sodium. Generally not necessary to specify `mod-loader`                   |
| `install carpet fabric-api sodium lithium`      | Easily install many mods.                                                                           |
| `update`                                        | Update all mods.                                                                                    |
| `update --pretend`                              | Check what will be updated. Does not change anything.                                               |
| `update sodium lithium phosphor`                | Update specific mods.                                                                               |
| `update -v "1.16.5"`                            | Updates to latest mod version which works with specified MC version.                                |
| `update -v "1.16.1"`                            | If you upgraded the mods, to a higher version (e.g. snapshot), you can easily downgrade them again. |
| `configure sodium=modrinth`                     | Change the download site for a mod.                                                                 |
| `configure sodium=`                             | Doesn't work, known bug! Reset download sites (downloads from all sites again)                      |
| `configure carpet=curse:fabric-carpet`          | Change site slug for a mod.                                                                         |
| `configure carpet=curse`                        | If you don't define a slug, you will reset the slug for that mod.                                   |
| `configure sodium=modrinth carpet=curse`        | Easily configure multiple mods at the same time.                                                    |
| `configure carpet=modrinth,curse:fabric-carpet` | Configure different slugs for different sites.                                                      |
| `list`                                          | List all installed mods.                                                                            |

## Full usage

```none
positional arguments:
  {install,update,configure,list}
                        Install, update, configure, or list mods
  mods
                        The mods to update or configure.
                        If no mods are specified during an update, all mods will be updated.
                        You can specify download sites and slugs for each mod (if necessary)
                           dynmap=curse
                           dynmap=curse:dynmapforge
                           dynmap=curse:dynmapforge,modrinth
                           dynmap=curse:dynmapforge,modrinth:dynmap

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
  --version             Print application version
  --verbose             Print more messages
  --debug               Turn on debug messages
  --pretend             Only pretend to install/update/configure. Does not change anything
  --no-color            Disable color output
```

## Alternatives

### GUI

- [Overwolf](https://www.overwolf.com/)
- [kaniol-lck/modmanager](https://github.com/kaniol-lck/modmanager)
- [ReviversMC/modget-minecraft](https://github.com/ReviversMC/modget-minecraft)
- [4JX/mCubed](https://github.com/4JX/mCubed)

### CLI

- [sargunv/modsman](https://github.com/sargunv/modsman)
- [tyra314/modweaver](https://github.com/tyra314/modweaver)

## Authors

- Matteus Magnusson, senth.wallace@gmail.com
