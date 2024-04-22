# coding: utf-8

"""
Selection methods defining categories based on selection step results.
"""

from __future__ import annotations

import law

from columnflow.util import maybe_import
from columnflow.categorization import Categorizer, categorizer
from columnflow.selection import SelectionResult
from columnflow.columnar_util import has_ak_column, optional_column

np = maybe_import("numpy")
ak = maybe_import("awkward")

@categorizer(uses={"event"}, call_force=True)
def catid_incl(self: Categorizer, events: ak.Array, **kwargs) -> tuple[ak.Array, ak.Array]:
    mask = ak.ones_like(events.event) > 0
    return events, mask

@categorizer(uses={"event"}, call_force=True)
def catid_selection_2e(
    self: Categorizer, events: ak.Array, results: SelectionResult, **kwargs,
) -> tuple[ak.Array, ak.Array]:
    mask = (ak.num(results.objects.Electron.Electron, axis=-1) == 2) & (ak.num(results.objects.Muon.Muon, axis=-1) == 0)
    print("ele selections mask", mask)
    return events, mask


@categorizer(uses={"event"}, call_force=True)
def catid_selection_2mu(
    self: Categorizer, events: ak.Array, results: SelectionResult, **kwargs,
) -> tuple[ak.Array, ak.Array]:
    mask = (ak.num(results.objects.Electron.Electron, axis=-1) == 0) & (ak.num(results.objects.Muon.Muon, axis=-1) == 2)
    return events, mask

@categorizer(uses={"Electron.pt", "Muon.pt"}, call_force=True)
def catid_2e(self: Categorizer, events: ak.Array, **kwargs) -> tuple[ak.Array, ak.Array]:
    mask = ((ak.sum(events.Electron.pt > 0, axis=-1) == 2) & (ak.sum(events.Muon.pt > 0, axis=-1) == 0))
    print("ele mask", mask)
    return events, mask


@categorizer(uses={"Electron.pt", "Muon.pt"}, call_force=True)
def catid_2mu(self: Categorizer, events: ak.Array, **kwargs) -> tuple[ak.Array, ak.Array]:
    mask = ((ak.sum(events.Electron.pt > 0, axis=-1) == 0) & (ak.sum(events.Muon.pt > 0, axis=-1) == 2))
    return events, mask