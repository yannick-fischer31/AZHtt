# coding: utf-8

"""
Definition of categories.

Categories are assigned a unique integer ID according to a fixed numbering
scheme, with digits/groups of digits indicating the different category groups:

"""

import law

from columnflow.util import maybe_import
from columnflow.categorization import Categorizer, categorizer

import order as od

logger = law.logger.get_logger(__name__)

np = maybe_import("numpy")
ak = maybe_import("awkward")


def name_fn(categories: dict[str, od.Category]):
    """Naming function for automatically generated combined categories."""
    return "__".join(cat.name for cat in categories.values() if cat)


def kwargs_fn(categories: dict[str, od.Category]):
    """Customization function for automatically generated combined categories."""
    return {
        "id": sum(cat.id for cat in categories.values()),
        "selection": [cat.selection for cat in categories.values()],
        "label": "\n".join(
            cat.label for cat in categories.values()
        ),
    }


def skip_fn(categories: dict[str, od.Category]):
    """Custom function for skipping certain category combinations."""
    return False  # don't skip


def add_categories(config: od.Config) -> None:
    @categorizer(uses={"event"})
    def cat_incl(self: Categorizer, events: ak.Array, **kwargs) -> tuple[ak.Array, ak.Array]:
        # fully inclusive selection
        return events, ak.ones_like(events.event) == 1


    @categorizer(uses={"Jet.pt"})
    def cat_2j(self: Categorizer, events: ak.Array, **kwargs) -> tuple[ak.Array, ak.Array]:
        # two or more jets
        return events, ak.num(events.Jet.pt, axis=1) >= 2