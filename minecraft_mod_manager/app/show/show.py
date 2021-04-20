from datetime import date

from ...core.entities.mod import Mod
from ...utils.logger import LogColors, Logger
from .show_repo import ShowRepo


class Show:
    _padding = 4

    def __init__(self, show_repo: ShowRepo) -> None:
        self._repo = show_repo
        self._id_width = 0
        self._repo_alias_width = 0
        self._repo_site_width = 0
        self._update_time_width = len("YYYY-MM-DD")

    def execute(self) -> None:
        self._installed_mods = self._repo.get_all_mods()

        self._calculate_id_width()
        self._calculate_repo_alias_width()
        self._calculate_repo_site_width()

        self._print_header()
        self._print_row("Mod", "Alias", "Site", "Published")
        for mod in self._installed_mods:
            self._print_mod(mod)

    def _calculate_id_width(self) -> None:
        for mod in self._installed_mods:
            if len(mod.id) > self._id_width:
                self._id_width = len(mod.id)
        self._id_width += Show._padding

    def _calculate_repo_alias_width(self) -> None:
        for mod in self._installed_mods:
            # Make sure we display an empty alias instead of 'None'
            if not mod.site_slug:
                mod.site_slug = ""

            if len(mod.site_slug) > self._repo_alias_width:
                self._repo_alias_width = len(mod.site_slug)

        self._repo_alias_width += Show._padding

    def _calculate_repo_site_width(self) -> None:
        for mod in self._installed_mods:
            if len(mod.site.value) > self._repo_site_width:
                self._repo_site_width = len(mod.site.value)
        self._repo_site_width += Show._padding

    def _print_header(self) -> None:
        Logger.info(f"{LogColors.bold}Installed mods:{LogColors.no_color}")

    def _print_row(self, id, alias, site, published) -> None:
        print(
            f"{id}".ljust(self._id_width)
            + f"{alias}".ljust(self._repo_alias_width)
            + f"{site}".ljust(self._repo_site_width)
            + f"{published}"
        )

    def _print_mod(self, mod: Mod) -> None:
        self._print_row(mod.id, mod.site_slug, mod.site.value, Show._get_date_from_epoch(mod.upload_time))

    @staticmethod
    def _get_date_from_epoch(epoch: int) -> str:
        if epoch == 0:
            return "???"

        d = date.fromtimestamp(epoch)
        return d.strftime("%Y-%m-%d")
