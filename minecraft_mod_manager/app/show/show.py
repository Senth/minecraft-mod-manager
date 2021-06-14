from datetime import date

from ...core.entities.mod import Mod
from ...utils.logger import LogColors, Logger
from .show_repo import ShowRepo


class Show:
    _padding = 4

    def __init__(self, show_repo: ShowRepo) -> None:
        self._repo = show_repo
        # Using width of headers as a minimum
        self._id_width = 3
        self._site_slug_width = 9
        self._update_time_width = len("YYYY-MM-DD")

    def execute(self) -> None:
        self._installed_mods = self._repo.get_all_mods()

        self._calculate_id_width()
        self._calculate_site_slug_width()

        self._print_header()
        self._print_row("Mod", "Site:Slug", "Published")
        for mod in self._installed_mods:
            self._print_mod(mod)

    def _calculate_id_width(self) -> None:
        for mod in self._installed_mods:
            if len(mod.id) > self._id_width:
                self._id_width = len(mod.id)
        self._id_width += Show._padding

    def _calculate_site_slug_width(self) -> None:
        for mod in self._installed_mods:
            site_slug = mod.get_site_slug_string()
            if len(site_slug) > self._site_slug_width:
                self._site_slug_width = len(site_slug)

        self._site_slug_width += Show._padding

    def _print_header(self) -> None:
        Logger.info(f"{LogColors.bold}Installed mods:{LogColors.no_color}")

    def _print_row(self, id, site_slug, published) -> None:
        print(f"{id}".ljust(self._id_width) + f"{site_slug}".ljust(self._site_slug_width) + f"{published}")

    def _print_mod(self, mod: Mod) -> None:
        self._print_row(mod.id, mod.get_site_slug_string(), Show._get_date_from_epoch(mod.upload_time))

    @staticmethod
    def _get_date_from_epoch(epoch: int) -> str:
        if epoch == 0:
            return "???"

        d = date.fromtimestamp(epoch)
        return d.strftime("%Y-%m-%d")
