"""
Definition of variables that can be plotted via `PlotCutflowVariables` tasks.
"""

import order as od


# cutflow variables
def add_cutflow_variables(config: od.Config) -> None:
    """
    defines reco-level cutflow variables in a convenient way; variables are lowercase and have
    names in the format:
    cf_{obj}{i}_{var}, where `obj` is the name of the given object, `i` is the index of the
    object (starting at 1) and `var` is the variable of interest; example: cf_loosejet1_pt
    """
    # default xtitle formatting per variable
    var_title_format = {
        "jet1_pt": r"$p_{T}$",
        "jet1_eta": r"$\eta$",
        "jet1_phi": r"$\phi$",
    }
    # default binning per variable
    var_binning = {
        "jet1_pt": (40, 0, 500),
        "jet1_eta": (40, -5, 5),
        "jet1_phi": (40, 0, 3.2),
    }
    # default units per variable
    var_unit = {
        "jet1_pt": "GeV",
    }

    # name = "cf_{obj}{i}_{var}"
    # expr = "cutflow.{obj}.{var}[:, {i}]"
    # x_title_base = r"{obj} {i} "
    # def quick_addvar(obj: str, i: int, var: str):
    #     """
    #     Helper to quickly generate generic variable instances
    #     """
    #     config.add_variable(
    #         name=name.format(obj=obj, i=i + 1, var=var).lower(),
    #         expression=expr.format(obj=obj, i=i, var=var),
    #         null_value=EMPTY_FLOAT,
    #         binning=var_binning[var],
    #         unit=var_unit.get(var, "1"),
    #         x_title=x_title_base.format(obj=obj, i=i + 1) + var_title_format.get(var, var),
    #      )

    # number of objects
    # for obj in (
    #         "jet",
    # ):
    #     config.add_variable(
    #         name=f"cf_n_{obj}",
    #         expression=f"cutflow.n_{obj}",
    #         binning=(11, -0.5, 10.5),
    #         x_title=f"Number of {obj}s",
    #     )

    for prop in ("jet1_pt", "jet1_eta", "jet1_phi"):
        config.add_variable(
            name=f"cf_{prop}",
            expression=f"cutflow.{prop}",
            binning=var_binning[prop],
            x_title=var_title_format[prop],
            unit=var_unit.get(prop),
        )
