# coding: utf-8

"""
Selection methods for HHtobbWW.
"""

from operator import and_
from functools import reduce
from collections import defaultdict
from typing import Tuple

from columnflow.util import maybe_import

from columnflow.selection.stats import increment_stats
from columnflow.selection import Selector, SelectionResult, selector
from columnflow.selection.cms.met_filters import met_filters
from columnflow.selection.cms.json_filter import json_filter

from columnflow.production.util import attach_coffea_behavior
from columnflow.production.cms.mc_weight import mc_weight
from columnflow.production.processes import process_ids

from azh.selection.jet_selection import jet_selection
from azh.selection.lepton_selection import lepton_selection


np = maybe_import("numpy")
ak = maybe_import("awkward")


@selector(
    uses={
        process_ids, attach_coffea_behavior,
        mc_weight,  # not opened per default but always required in Cutflow tasks
        jet_selection, lepton_selection, #azh_selection,
        increment_stats,
    },
    produces={
         process_ids, attach_coffea_behavior,
        mc_weight, 
        jet_selection, lepton_selection, #azh_selection,
        increment_stats,
    },
    exposed=True,
    check_used_columns=False,
    check_produced_columns=False,
)
def default(
    self: Selector,
    events: ak.Array,
    stats: defaultdict,
    **kwargs,
) -> Tuple[ak.Array, SelectionResult]:

    if self.dataset_inst.is_mc:
        events = self[mc_weight](events, **kwargs)

    # ensure coffea behavior
    events = self[attach_coffea_behavior](events, **kwargs)

    # prepare the selection results that are updated at every step
    results = SelectionResult()

    # MET filters
    # events, met_filters_results = self[met_filters](events, **kwargs)
    # results += met_filters_results

    # JSON filter (data-only)
    # if self.dataset_inst.is_data:
    #     events, json_filter_results = self[json_filter](events, **kwargs)
    #     results += json_filter_results

    # # TODO Implement selection
    # # lepton selection
    events, results_lepton = self[lepton_selection](events, **kwargs)
    results += results_lepton

    # jet selection
    events, results_jet = self[jet_selection](events, **kwargs)
    results += results_jet

    # trigger selection
    # Uses pt_avg and the probe jet
    # if self.dataset_inst.is_data:
    #     events, results_trigger = self[trigger_selection](events, **kwargs)
    #     results += results_trigger

    # events, results_azh = self[azh_selection](events, **kwargs)
    # results += results_azh

    # create process ids
    print(process_ids)
    events = self[process_ids](events, **kwargs)

    # build categories
    # events = self[category_ids](events, results=results, **kwargs)

    # produce relevant columns
    # events = self[cutflow_features](events, results.objects, **kwargs)

    # results.event contains full selection mask. Sum over all steps.
    # Make sure all nans are present, otherwise next tasks fail
    results.event = reduce(and_, results.steps.values())
    results.event = ak.fill_none(results.event, False)
    print(results.event)

    weight_map = {
        "num_events": Ellipsis,
        "num_events_selected": results.event,
    }
    group_map = {}
    print("group")
    if self.dataset_inst.is_mc:
        weight_map = {
            **weight_map,
            # mc weight for all events
            "sum_mc_weight": (events.mc_weight, Ellipsis),
            "sum_mc_weight_selected": (events.mc_weight, results.event),
        }
        group_map = {
            # per process
            "process": {
                "values": events.process_id,
                "mask_fn": (lambda v: events.process_id == v),
            },
            # # per jet multiplicity
            # "njet": {
            #     "values": results.x.n_jets,
            #     "mask_fn": (lambda v: results.x.n_jets == v),
            # },
        }
    events, results = self[increment_stats](
        events,
        results,
        stats,
        weight_map=weight_map,
        group_map=group_map,
        **kwargs,
    )

    return events, results


# @default.init
# def default_init(self: Selector) -> None:
#     if self.config_inst.x("do_cutflow_features", False):
#         self.uses.add(cutflow_features)
#         self.produces.add(cutflow_features)

#     if not getattr(self, "dataset_inst", None) or self.dataset_inst.is_data:
#         return

#     self.uses.add(event_weights_to_normalize)
#     self.produces.add(event_weights_to_normalize)