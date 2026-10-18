import os
import streamlit as st
import requests
import pandas as pd
from ui_shared import apply_theme, module_header


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Gas Feed Allocation Optimizer",
    page_icon="⚙️",
    layout="wide"
)


# ============================================================
# PAGE HEADER
# ============================================================

apply_theme()
module_header(
    "Module 02 · Optimization",
    "Gas Feed Allocation Optimizer",
    "Optimize gas-feed routing across processing plants and fractionation units to maximize synthetic product value while respecting capacity and routing constraints.",
)

API_URL = os.getenv("OPTIMIZER_API_URL", "http://127.0.0.1:8002/optimizer/run")


# ============================================================
# RUN OPTIMIZATION
# ============================================================

if st.button(
    "Run Optimization",
    type="primary"
):

    with st.spinner(
        "Running feed allocation optimizer..."
    ):

        try:

            response = requests.post(
                API_URL,
                timeout=60
            )

        except requests.exceptions.RequestException as e:

            st.error(
                f"Could not connect to optimizer API: {e}"
            )

            st.stop()


    # ========================================================
    # CHECK API RESPONSE
    # ========================================================

    if response.status_code != 200:

        st.error(
            f"API returned error code "
            f"{response.status_code}"
        )

        st.write(response.text)

        st.stop()


    result = response.json()


    # ========================================================
    # OPTIMIZATION STATUS
    # ========================================================

    if result.get("status") != "Optimal":

        st.warning(
            "Optimizer did not return an optimal solution."
        )

        st.write(result)

        st.stop()


    st.success(
        "Optimization completed successfully"
    )


    # ========================================================
    # HEADLINE KPIs
    # ========================================================

    st.subheader(
        "Optimization Summary"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Available Gas",
        f'{result["total_available_mmscfd"]:,.1f} MMSCFD'
    )

    col2.metric(
        "Gas Processed",
        f'{result["total_processed_mmscfd"]:,.1f} MMSCFD'
    )

    col3.metric(
        "Excess / Curtailed Gas",
        f'{result["total_excess_mmscfd"]:,.1f} MMSCFD'
    )


    col4, col5, col6 = st.columns(3)

    col4.metric(
        "Baseline Revenue",
        f'${result["baseline_daily_revenue"]:,.0f}/day'
    )

    col5.metric(
        "Optimized Revenue",
        f'${result["optimized_daily_revenue"]:,.0f}/day'
    )

    col6.metric(
        "Incremental Value",
        f'${result["incremental_daily_value"]:,.0f}/day',
        delta=f'{result["improvement_percent"]:.2f}%'
    )


    st.info(
        f'Annualized synthetic optimization value: '
        f'${result["incremental_annual_value"]:,.0f}/year'
    )


    # ========================================================
    # ALLOCATION DATAFRAME
    # ========================================================

    allocations = pd.DataFrame(
        result["allocations"]
    )

    curtailment = pd.DataFrame(
        result["curtailment"]
    )


    # ========================================================
    # OPTIMAL ROUTING
    # ========================================================

    st.divider()

    st.subheader(
        "Optimal Feed → Plant → Fractionator Routing"
    )

    if allocations.empty:

        st.warning(
            "No feed allocation was returned."
        )

    else:

        display_allocations = allocations.copy()

        display_allocations = (
            display_allocations.rename(
                columns={
                    "feed": "Feed",
                    "plant": "Plant",
                    "fractionator": "Fractionator",
                    "flow_mmscfd": "Flow (MMSCFD)",
                    "value_per_mmscfd":
                        "Value / MMSCFD ($/day)",
                    "daily_revenue":
                        "Daily Revenue ($)"
                }
            )
        )

        st.dataframe(
            display_allocations,
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # FEED -> PLANT MATRIX
    # ========================================================

    st.subheader(
        "Feed → Plant Allocation Matrix"
    )

    if not allocations.empty:

        feed_plant_matrix = (
            allocations.pivot_table(
                index="feed",
                columns="plant",
                values="flow_mmscfd",
                aggfunc="sum",
                fill_value=0
            )
        )

        st.dataframe(
            feed_plant_matrix.round(2),
            use_container_width=True
        )


    # ========================================================
    # PLANT -> FRACTIONATOR MATRIX
    # ========================================================

    st.subheader(
        "Plant → Fractionator Routing Matrix"
    )

    if not allocations.empty:

        plant_frac_matrix = (
            allocations.pivot_table(
                index="plant",
                columns="fractionator",
                values="flow_mmscfd",
                aggfunc="sum",
                fill_value=0
            )
        )

        st.dataframe(
            plant_frac_matrix.round(2),
            use_container_width=True
        )


    # ========================================================
    # CURTAILMENT / EXCESS GAS
    # ========================================================

    st.subheader(
        "Excess / Curtailed Feed"
    )

    if not curtailment.empty:

        curtailment_display = (
            curtailment.rename(
                columns={
                    "feed": "Feed",
                    "excess_mmscfd":
                        "Excess / Curtailed (MMSCFD)"
                }
            )
        )

        st.dataframe(
            curtailment_display,
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # BUSINESS VALUE COMPARISON
    # ========================================================

    st.divider()

    st.subheader(
        "Baseline vs Optimized Value"
    )

    value_comparison = pd.DataFrame(
        {
            "Scenario": [
                "Baseline Routing",
                "Optimized Routing"
            ],

            "Daily Revenue ($)": [
                result[
                    "baseline_daily_revenue"
                ],

                result[
                    "optimized_daily_revenue"
                ]
            ]
        }
    )

    st.bar_chart(
        value_comparison.set_index(
            "Scenario"
        )
    )


    st.markdown(
        f"""
        **Incremental value from optimization:**
        ${result["incremental_daily_value"]:,.0f}/day

        **Annualized synthetic value:**
        ${result["incremental_annual_value"]:,.0f}/year

        **Revenue improvement:**
        {result["improvement_percent"]:.2f}%
        """
    )


    # ========================================================
    # HOW IT WORKS
    # ========================================================

    st.divider()

    with st.expander(
        "How this optimizer works"
    ):

        st.markdown(
            """
### Business objective

The optimizer determines how available gas
feeds should be routed across processing plants
and downstream fractionation units to maximize
total product revenue.

---

### Feed composition

Each feed contains:

- C1
- C2
- C3
- C4
- C5+
- CO2
- N2

Different feeds therefore have different
economic potential.

---

### Processing plant performance

The same feed can perform differently in
different plants.

The model includes feed-specific recoveries for:

- C2
- C3
- C4
- C5+

This means there is no single universally
"best plant."

---

### Fractionation

Recovered liquids are routed to downstream
fractionation units.

Each fractionator has:

- capacity limits
- component-specific recoveries
- permitted plant-to-fractionator routes

---

### Optimization decision

For every feasible route:

**Feed → Plant → Fractionator**

the optimizer determines the amount of gas
that should be allocated.

---

### Constraints

The optimization respects:

- feed availability
- processing plant capacity
- fractionation capacity
- plant-to-fractionator routing restrictions

---

### Excess / curtailed gas

If available gas exceeds the usable capacity
of the processing and fractionation network,
the remaining quantity is explicitly reported
as excess or curtailed gas.

---

### Economic objective

Revenue includes value from:

- C1 residue gas
- C2 ethane
- C3 propane
- C4 butane
- C5+ condensate / natural gasoline

The optimizer selects the combination of
routes that produces the highest total value.

---

### Baseline comparison

A synthetic fixed-routing operating scenario
is used as the baseline.

The optimized case dynamically changes routing
based on:

- feed composition
- recoveries
- capacities
- routing possibilities
- product prices

The difference between these two cases
represents the demonstrated optimization value.

---

### Important note

All operating data, prices, recoveries and
economic values in this module are synthetic.

The purpose of this module is to demonstrate
the optimization architecture and methodology,
not to represent an actual operating asset.
"""
        )


# ============================================================
# INFORMATION SHOWN BEFORE RUNNING
# ============================================================

else:

    st.info(
        """
        Click **Run Optimization** to calculate the
        optimal gas-feed allocation.
        """
    )

    st.markdown(
        """
### Optimization flow

**Available Gas Feeds**

↓  

**Processing Plants**

↓  

**Fractionation Units**

↓  

**C1 + C2 + C3 + C4 + C5+ Product Value**

↓  

### Maximize Total Revenue
"""
    )