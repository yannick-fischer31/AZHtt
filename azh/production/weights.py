# coding: utf-8

"""
Column production methods related to generic event weights.
"""

from columnflow.util import maybe_import
from columnflow.columnar_util import set_ak_column, has_ak_column, Route
from columnflow.selection import SelectionResult
from columnflow.production import Producer, producer
from columnflow.production.cms.pileup import pu_weight
from columnflow.production.normalization import normalization_weights
from columnflow.production.cms.electron import electron_weights
from columnflow.production.cms.muon import muon_weights
from columnflow.production.cms.btag import btag_weights
from columnflow.production.cms.scale import murmuf_weights, murmuf_envelope_weights
from columnflow.production.cms.pdf import pdf_weights
from azh.production.normalized_weights import normalized_weight_factory
# from azh.production.normalized_btag import normalized_btag_weights

np = maybe_import("numpy")
ak = maybe_import("awkward")


@producer(
    produces={"event_weight"},
    mc_only=True,
)
def event_weight(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    """
    Producer that calculates the 'final' event weight (as done in cf.CreateHistograms)
    """
    weight = ak.Array(np.ones(len(events)))
    if self.dataset_inst.is_mc:
        for column in self.config_inst.x.event_weights:
            weight = weight * Route(column).apply(events)
        for column in self.dataset_inst.x("event_weights", []):
            if has_ak_column(events, column):
                weight = weight * Route(column).apply(events)
            else:
                self.logger.warning_once(
                    f"missing_dataset_weight_{column}",
                    f"weight '{column}' for dataset {self.dataset_inst.name} not found",
                )

    events = set_ak_column(events, "event_weight", weight)

    return events


@event_weight.init
def event_weight_init(self: Producer) -> None:
    if not getattr(self, "dataset_inst", None):
        return

    self.uses |= set(self.config_inst.x.event_weights.keys())
    self.uses |= set(self.dataset_inst.x("event_weights", {}).keys())


@producer(
    uses={pu_weight, btag_weights},
    # don't save btag_weights to save storage space, since we can reproduce them in ProduceColumns
    produces={pu_weight},
    mc_only=True,
)
def event_weights_to_normalize(self: Producer, events: ak.Array, results: SelectionResult, **kwargs) -> ak.Array:
    """
    Wrapper of several event weight producers that are typically called as part of SelectEvents
    since it is required to normalize them before applying certain event selections.
    """

    # compute pu weights
    events = self[pu_weight](events, **kwargs)

    # compute btag SF weights (for renormalization tasks)
    # events = self[btag_weights](events, jet_mask=results.aux["jet_mask"], **kwargs)

    # skip scale/pdf weights for some datasets (missing columns)
    if not self.dataset_inst.x("skip_scale", False):
        # compute scale weights
        events = self[murmuf_envelope_weights](events, **kwargs)

        # read out mur and weights
        events = self[murmuf_weights](events, **kwargs)

    if not self.dataset_inst.x("skip_pdf", False):
        # compute pdf weights
        events = self[pdf_weights](events, **kwargs)

    return events


@event_weights_to_normalize.init
def event_weights_to_normalize_init(self) -> None:
    if not getattr(self, "dataset_inst", None):
        return

    if not self.dataset_inst.x("skip_scale", False):
        self.uses |= {murmuf_envelope_weights, murmuf_weights}
        self.produces |= {murmuf_envelope_weights, murmuf_weights}

    if not self.dataset_inst.x("skip_pdf", False):
        self.uses |= {pdf_weights}
        self.produces |= {pdf_weights}


normalized_scale_weights = normalized_weight_factory(
    producer_name="normalized_scale_weights",
    weight_producers={murmuf_envelope_weights, murmuf_weights},
)

normalized_pdf_weights = normalized_weight_factory(
    producer_name="normalized_pdf_weights",
    weight_producers={pdf_weights},
)


@producer(
    # uses={
    #     normalization_weights, electron_weights, muon_weights, btag_weights,
    #     normalized_btag_weights, event_weight,
    # },
    uses={
        normalization_weights, electron_weights, muon_weights, event_weight,
    },
    # produces={
    #     "mc_weight",  # might be needed for ML
    #     normalization_weights, electron_weights, muon_weights,
    #     normalized_btag_weights, event_weight,
    # },
    mc_only=True,
)
def event_weights(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    """
    Wrapper of several event weight producers that are typically called in ProduceColumns.
    """

    # compute normalization weights
    events = self[normalization_weights](events, **kwargs)

    # compute btag SF weights
    # events = self[btag_weights](events, **kwargs)

    # compute electron and muon SF weights
    # events = self[electron_weights](events, **kwargs)
    # events = self[muon_weights](events, **kwargs)

    # normalize event weights using stats
    # events = self[normalized_btag_weights](events, **kwargs)

    # if not self.dataset_inst.x("skip_scale", False):
    #     events = self[normalized_scale_weights](events, **kwargs)

    # if not self.dataset_inst.x("skip_pdf", False):
    #     events = self[normalized_pdf_weights](events, **kwargs)

    # calculate the full event weight for plotting purposes
    events = self[event_weight](events, **kwargs)

    return events


@event_weights.init
def event_weights_init(self: Producer) -> None:
    if not getattr(self, "dataset_inst", None):
        return

    # if not self.dataset_inst.x("skip_scale", False):
    #     self.uses |= {normalized_scale_weights}
    #     self.produces |= {normalized_scale_weights}

    # if not self.dataset_inst.x("skip_pdf", False):
    #     self.uses |= {normalized_pdf_weights}
    #     self.produces |= {normalized_pdf_weights}


@producer(
    uses={"mc_weight"},
    produces={"mc_weight"},
    mc_only=True,
)
def large_weights_killer(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    """
    Simple producer that sets eventweights to 0 when too large.
    """
    if self.dataset_inst.is_data:
        raise Exception("large_weights_killer is only callable for MC")

    # TODO: figure out a good threshold when events are considered unphysical
    median_weight = ak.sort(abs(events.mc_weight))[int(len(events) / 2)]
    weight_too_large = abs(events.mc_weight) > 1000 * median_weight
    events = set_ak_column(events, "mc_weight", ak.where(weight_too_large, 0, events.mc_weight))

    return events