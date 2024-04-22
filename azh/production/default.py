# coding: utf-8

"""
Column production methods related to higher-level features.
"""


from columnflow.production import Producer, producer
from columnflow.production.categories import category_ids
from columnflow.production.normalization import normalization_weights
from columnflow.util import maybe_import

# from azh.production.azh_quantities import azh_quantities
from azh.production.z_boson import z_boson
from azh.production.prepare_objects import prepare_objects
from azh.production.leptons import choose_lepton
from azh.production.weights import event_weights


ak = maybe_import("awkward")
coffea = maybe_import("coffea")
np = maybe_import("numpy")
maybe_import("coffea.nanoevents.methods.nanoaod")


@producer(
    uses={
        category_ids, normalization_weights,
        event_weights, z_boson, choose_lepton,
        prepare_objects,
    },
    produces={
        category_ids, normalization_weights,
        event_weights, z_boson, choose_lepton,
        prepare_objects,
    },
)
def default(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    print("WELCOME TO THE DEFAULT PRODUCER")
    # mc-only weights
    if self.dataset_inst.is_mc:
        # normalization weights
        # events = self[normalization_weights](events, **kwargs)
        events = self[event_weights](events, **kwargs)

    # dijet properties: alpha, asymmetry, pt_avg
    # Include MPF production here
    # events = self[azh_quantities](events, **kwargs)
    # category ids
    # events = self[category_ids](events, **kwargs)
    events = self[choose_lepton](events, **kwargs)
    events = self[prepare_objects](events, **kwargs)
    events = self[z_boson](events, **kwargs)


    # deterministoc seeds
    # events = self[category_ids](events, **kwargs)
    print(events)

    return events