from typing import Tuple
from columnflow.util import maybe_import
from columnflow.columnar_util import set_ak_column
from columnflow.selection import Selector, SelectionResult, selector
from azh.util import masked_sorted_indices

ak = maybe_import("awkward")


@selector(

    uses={
        "Electron.pt", "Electron.eta",
        "Muon.pt", "Muon.eta", "Muon.tightId",
    },
    produces={"cutflow.n_ele", "cutflow.n_muo"},
    exposed=True,
)
def lepton_selection(
    self: Selector,
    events: ak.Array,
    **kwargs,
) -> Tuple[ak.Array, SelectionResult]:
    # lepton selection based on old UHH2 framework
    # https://github.com/UHH2/DiJetJERC/blob/ff98eebbd44931beb016c36327ab174fdf11a83f/src/AnalysisModule_DiJetTrg.cxx#L703
    # IDs in JME Nano https://cms-nanoaod-integration.web.cern.ch/integration/master-106X/mc102X_doc.html
    # mask for muons
    muo_mask = (
        (events.Muon.pt > 20) &
        (abs(events.Muon.eta) < 2.4) &
        (events.Muon.tightId)
    )
    # mask for electrons
    ele_mask = (
        (events.Electron.pt > 20) &
        (abs(events.Electron.eta) < 2.4)
    )

    events = set_ak_column(events, "cutflow.n_ele", ak.sum(ele_mask, axis=1))
    events = set_ak_column(events, "cutflow.n_muo", ak.sum(muo_mask, axis=1))

    # select only events with no leptons
    lep_sel = (events.cutflow.n_ele == 2) | (events.cutflow.n_muo == 2)

    ele_indices = masked_sorted_indices(ele_mask, events.Electron.pt)
    muo_indices = masked_sorted_indices(muo_mask, events.Muon.pt)

    ele_mask = ak.fill_none(ele_mask, False)
    muo_mask = ak.fill_none(muo_mask, False)

    lep_sel = ak.fill_none(lep_sel, False)
    print("Lepton selection:", lep_sel)
    # build and return selection results plus new columns
    return events, SelectionResult(
        steps={
            "Lepton": lep_sel,
        },
        objects={
            "Electron": {
                "Electron": ele_indices,
            },
            "Muon": {
                "Muon": muo_indices,
            },
        },
        aux={
            "ele_mask": ele_mask,
            "n_central_eletons": ak.num(ele_indices),
            "muo_mask": muo_mask,
            "n_central_muons": ak.num(muo_indices),
        },
    )
