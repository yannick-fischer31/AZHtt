# coding: utf-8

"""
Column producers related to leptons.
"""
from columnflow.production import Producer, producer
from columnflow.util import maybe_import
from columnflow.columnar_util import set_ak_column

ak = maybe_import("awkward")
np = maybe_import("numpy")
coffea = maybe_import("coffea")
maybe_import("coffea.nanoevents.methods.nanoaod")


@producer(
    uses={
        "category_ids",
        "Electron.pt", "Electron.eta", "Electron.phi", "Electron.mass",
        "Electron.pdgId",
        "Muon.pt", "Muon.eta", "Muon.phi", "Muon.mass",
        "Muon.pdgId",
    },
    produces={
        "Leptons.pt", "Leptons.eta", "Leptons.phi", "Leptons.mass",
        "Leptons.pdgId",
    },
)
def choose_lepton(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    """
    Choose either muon or electron as the main lepton per event
    based on `channel_id` information and write it to a new column
    `Lepton`.
    """

    # extract only LV columns
    muon = events.Muon[["pt", "eta", "phi", "mass", "pdgId"]]
    electron = events.Electron[["pt", "eta", "phi", "mass", "pdgId"]]
    # from IPython import embed;
    # embed()
    leptons = ak.concatenate([
        ak.mask(muon, (ak.pad_none(events.category_ids,2) == 40)[:,0]),
        ak.mask(electron, (ak.pad_none(events.category_ids,2) == 30)[:,0]),
    ], axis=1)
    print("Category Id", events.category_ids)
    print((ak.pad_none(events.category_ids,2) == 30)[:,0])
    print(muon)
    print(ak.mask(muon, (ak.pad_none(events.category_ids,2) == 40)[:,0]))
    print("leptons", leptons)
    for l in range(30):
        print(l)
        for m in range(len(muon[l])):
            print("muon:", muon[l][m])
        for m in range(len(electron[l])):
            print("electron:",electron[l][m])
    for l in range(30):
        print(l)
        print((ak.pad_none(events.category_ids,2) == 40)[l,0])
    for l in range(30):
        print(l)
        print(leptons[l])

    # attach lorentz vector behavior to lepton
    leptons = ak.with_name(leptons, "PtEtaPhiMLorentzVector")
    print(leptons)
    # commit lepton to events array
    events = set_ak_column(events, "Leptons", leptons)

    print(events.Leptons)
    return events