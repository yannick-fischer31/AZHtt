# coding: utf-8

from typing import Tuple
from columnflow.util import maybe_import
from columnflow.columnar_util import set_ak_column
from columnflow.selection import Selector, SelectionResult, selector
from azh.util import masked_sorted_indices

ak = maybe_import("awkward")


@selector(
    uses={"Jet.pt", "Jet.eta", "Jet.phi", "Jet.jetId", "Jet.puId"},
    exposed=True,
)
def jet_selection(
    self: Selector,
    events: ak.Array,
    **kwargs,
) -> Tuple[ak.Array, SelectionResult]:
    # DiJet jet selection
    # - require ...

    # assign local index to all Jets - stored after masks for matching
    # TODO: Drop for dijet ?
    events = set_ak_column(events, "Jet.local_index", ak.local_index(events.Jet))

    # jets
    # TODO: Correct jets
    # Selection by UHH2 framework
    # https://github.com/UHH2/DiJetJERC/blob/ff98eebbd44931beb016c36327ab174fdf11a83f/src/AnalysisModule_DiJetTrg.cxx#L692
    # IDs in NanoAOD https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD
    #  & JME NanoAOD https://cms-nanoaod-integration.web.cern.ch/integration/master-106X/mc102X_doc.html
    jet_mask = (
        (events.Jet.pt > 30) &
        (abs(events.Jet.eta) < 2.4) &
        # IDs in NanoAOD https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD
        (events.Jet.jetId == 6)  # &  # 2: fail tight LepVeto and 6: pass tightLepVeto
        # ((events.Jet.puId == 7) | (events.Jet.pt > 50))  # pass all IDs (l, m and t) only for jets with pt < 50 GeV
    )
    jet_sel = ak.num(events.Jet[jet_mask]) >= 5

    jet_indices = masked_sorted_indices(jet_mask, events.Jet.pt)
    jet_sel = ak.fill_none(jet_sel, False)
    jet_mask = ak.fill_none(jet_mask, False)
    print("Jet Selection:", jet_sel)
    # build and return selection results plus new columns
    return events, SelectionResult(
        steps={
            "Jet": jet_sel,
        },
        objects={
            "Jet": {
                "Jet": jet_indices,
            },
        },
        aux={
            "jet_mask": jet_mask,
            "n_central_jets": ak.num(jet_indices),
        },
    )
