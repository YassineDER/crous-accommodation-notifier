import logging
from html import escape as html_escape
from src.models import Accommodation, Notification, SearchResults


logger = logging.getLogger(__name__)


class NotificationBuilder:
    """Class that builds notifications from search results."""

    def __init__(
        self,
        notify_when_no_results: bool = False,
        max_price_eur: float | None = None,
        colocative: bool = False,
    ):
        self.notify_when_no_results = notify_when_no_results
        # Only send notifications for accommodations strictly cheaper than this value
        # If None, no price filtering is applied
        self.max_price_eur = max_price_eur
        self.colocative = colocative

    def search_results_notification(
        self, search_results: SearchResults
    ) -> Notification | None:
        accommodations = search_results.accommodations

        # Apply price filter if enabled
        if self.max_price_eur is not None:
            before = len(accommodations)
            filtered: list[Accommodation] = [
                a
                for a in accommodations
                if isinstance(a.price, float) and a.price < float(self.max_price_eur)
            ]
            logger.debug(
                "Price filter: kept %d/%d accommodations with price < %.2f",
                len(filtered),
                before,
                self.max_price_eur,
            )
            accommodations = filtered

        # Apply colocative filter if enabled
        if self.colocative:
            before = len(accommodations)
            filtered: list[Accommodation] = [
                a for a in accommodations if a.is_colocative
            ]
            logger.debug(
                "Colocative filter: kept %d/%d colocative accommodations",
                len(filtered),
                before,
            )
            accommodations = filtered

        # Check if we should notify when no accommodations are found
        if not accommodations and not self.notify_when_no_results:
            return None

        if not accommodations:
            message = "Aucun logement trouvé. Voici une liste des ponts de France où vous pourriez dormir : https://fr.wikipedia.org/wiki/Liste_de_ponts_de_France"
        else:
            s = "s" if len(accommodations) > 1 else ""
            verb = "sont" if len(accommodations) > 1 else "est"
            message = (
                f"Bonne nouvelle ! {len(accommodations)} logement{s} {verb} disponible{s} :\n"
                f"Filtre appliqué : prix max = {self.max_price_eur}€, colocation = {self.colocative}\n\n"
            )

        def format_one_accommodation(accommodation: Accommodation) -> str:
            title = accommodation.title or "Sans titre"
            price_val = (
                f"{accommodation.price}€"
                if isinstance(accommodation.price, float)
                else (accommodation.price or "")
            )
            title_html = html_escape(title)
            price_html = html_escape(str(price_val))
            link = (
                f"https://trouverunlogement.lescrous.fr/tools/42/accommodations/{accommodation.id}"
            )
            # Use HTML to avoid Telegram Markdown entity parsing issues
            return f"<a href=\"{link}\"><b>{title_html}</b></a> ({price_html})"

        message += "\n\n".join(map(format_one_accommodation, accommodations))

        message += (
            f"\n\n<a href=\"{search_results.search_url}\">{html_escape(str(search_results.search_url))}</a>"
        )

        return Notification(message=message)
