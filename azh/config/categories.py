# coding: utf-8

"""
Definition of categories.

Categories are assigned a unique integer ID according to a fixed numbering
scheme, with digits/groups of digits indicating the different category groups:

"""

import law

from columnflow.util import maybe_import
from columnflow.categorization import Categorizer, categorizer
from azh.util import call_once_on_config


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

@call_once_on_config()
def add_categories_selection(config: od.Config) -> None:
    add_lepton_categories(config)
    add_incl_cat(config)


# def add_categories(config: od.Config) -> None:
#     @categorizer(uses={"event"})
#     def cat_incl(self: Categorizer, events: ak.Array, **kwargs) -> tuple[ak.Array, ak.Array]:
#         # fully inclusive selection
#         return events, ak.ones_like(events.event) == 1


    # @categorizer(uses={"Jet.pt"})
    # def cat_2j(self: Categorizer, events: ak.Array, **kwargs) -> tuple[ak.Array, ak.Array]:
    #     # two or more jets
    #     return events, ak.num(events.Jet.pt, axis=1) >= 2

@call_once_on_config()
def add_incl_cat(config: od.Config) -> None:

    cat_incl = config.add_category(  # noqa
        name="cat_incl",
        id=1,
        selection="catid_incl",
        label="Inclusive",
    )


@call_once_on_config()
def add_lepton_categories(config: od.Config) -> None:

    cat_2e = config.add_category(  # noqa
        name="2e",
        id=30,
        selection="catid_selection_2e",
        label="2 Electron",
    )

    cat_2mu = config.add_category(  # noqa
        name="2mu",
        id=40,
        selection="catid_selection_2mu",
        label="2 Muon",
    )

@call_once_on_config()
def add_categories_production(config: od.Config) -> None:
    """
    Adds categories to a *config*, that are typically produced in `ProduceColumns`.
    """

    #
    # switch existing categories to different production module
    #

    cat_2e = config.get_category("2e")
    cat_2e.selection = "catid_2e"

    cat_2mu = config.get_category("2mu")
    cat_2mu.selection = "catid_2mu"
