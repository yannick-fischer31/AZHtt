# coding: utf-8

from columnflow.util import maybe_import
from functools import wraps
from typing import Hashable, Iterable, Callable
import law

ak = maybe_import("awkward")
np = maybe_import("numpy")


def masked_sorted_indices(mask: ak.Array, sort_var: ak.Array, ascending: bool = False) -> ak.Array:
    """
    Helper function to obtain the correct indices of an object mask
    """
    indices = ak.argsort(sort_var, axis=-1, ascending=ascending)
    return indices[mask[indices]]

def call_once_on_config(include_hash=False):
    """
    Parametrized decorator to ensure that function *func* is only called once for the config *config*
    """
    def outer(func):
        @wraps(func)
        def inner(config, *args, **kwargs):
            tag = f"{func.__name__}_called"
            if include_hash:
                tag += f"_{func.__hash__()}"

            if config.has_tag(tag):
                return

            config.add_tag(tag)
            return func(config, *args, **kwargs)
        return inner
    return outer

# def four_vec(
#     collections: str | Iterable[str],
#     columns: str | Iterable[str] | None = None,
#     skip_defaults: bool = False,
# ) -> set[str]:
#     """
#     Helper to quickly get a set of 4-vector component string for all collections in *collections*.
#     Additional columns can be added wih the optional *columns* parameter.

#     Example:

#     .. code-block:: python

#     four_vec("Jet", "jetId")
#     # -> {"Jet.pt", "Jet.eta", "Jet.phi", "Jet.mass", "Jet.jetId"}

#     four_vec({"Electron", "Muon"})
#     # -> {
#             "Electron.pt", "Electron.eta", "Electron.phi", "Electron.mass",
#             "Muon.pt", "Muon.eta", "Muon.phi", "Muon.mass",
#         }
#     """
#     # make sure *collections* is a set
#     collections = law.util.make_set(collections)

#     # transform *columns* to a set and add the default 4-vector components
#     columns = law.util.make_set(columns) if columns else set()
#     default_columns = {"pt", "eta", "phi", "mass"}
#     if not skip_defaults:
#         columns |= default_columns

#     outp = set(
#         f"{obj}.{var}"
#         for obj in collections
#         for var in columns
#     )

#     # manually remove MET eta and mass
#     outp = outp.difference({"MET.eta", "MET.mass"})

#     return outp