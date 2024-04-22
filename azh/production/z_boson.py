from columnflow.util import maybe_import
from columnflow.columnar_util import EMPTY_FLOAT
from columnflow.columnar_util import set_ak_column
from columnflow.production import Producer, producer
from azh.production.leptons import choose_lepton
import functools

np = maybe_import("numpy")
ak = maybe_import("awkward")

@producer(
    uses={
        choose_lepton,
    },
    produces={
        "m_z",
    },
)

def z_boson(self: Producer, events: ak.Array, **kwargs) -> ak.Array:
    # leptons = events.Lepton
    # leptons = ak.pad_none(leptons,3)

    print("Leptons for z ", events.Leptons)
    for l in range(3):
        print(events.Leptons[l])
        print(events.Leptons[:, 0][l])
        print(events.Leptons[:, 1][l])
    z = events.Leptons[:, 0] + events.Leptons[:, 1]
    print(z)
    print(z.mass)
    events = set_ak_column(events, "m_z", z.mass)
    return events
