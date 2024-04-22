# coding: utf-8

"""
Column production method
"""

import law

from columnflow.production import Producer, producer
from columnflow.selection import SelectionResult
from columnflow.util import maybe_import
from columnflow.columnar_util import set_ak_column, optional_column
from columnflow.production.util import attach_coffea_behavior
# from columnflow.production.util import attach_coffea_behavior

# from azh.util import four_vec
from azh.production.leptons import choose_lepton

ak = maybe_import("awkward")
coffea = maybe_import("coffea")
np = maybe_import("numpy")
maybe_import("coffea.nanoevents.methods.nanoaod")

logger = law.logger.get_logger(__name__)

custom_collections = {
    "Lepton": {
        "type_name": "Muon",  # is there some other collection?
        "check_attr": "metric_table",
        "skip_fields": "*Idx*G",
    },
}


@producer(
    # This producer only requires 4-vector properties,
    # but all columns required by the main Selector/Producer will be considered
    uses={
        attach_coffea_behavior, "Electron.pt", "Electron.eta", "Electron.phi", "Electron.mass",
        "Muon.pt", "Muon.eta", "Muon.phi", "Muon.mass", "Leptons.pt", "Leptons.eta", "Leptons.phi", "Leptons.mass",
        choose_lepton,
    },
    # no produces since we do not want to permanently produce columns
)
def prepare_objects(self: Producer, events: ak.Array, results: SelectionResult = None, **kwargs) -> ak.Array:
    """
    Producer that defines objects in a convenient way.
    When used as part of `SelectEvents`, be careful since it may override the original NanoAOD columns.
    """

    # coffea behavior for relevant objects
    events = self[attach_coffea_behavior](events, collections=custom_collections, **kwargs)


    return events