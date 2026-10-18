import pandas as pd
import numpy as np
from scipy.optimize import linprog


INPUT_FILE = "module2_feed_allocation_inputs_v1.xlsx"

KMOL_PER_DAY_PER_MMSCFD = 1195
C1_MMBTU_PER_DAY_PER_MMSCFD = 1000


def run_optimizer(input_file=INPUT_FILE):

    # =========================================================
    # 1. LOAD INPUT DATA
    # =========================================================

    feeds = pd.read_excel(
        input_file,
        sheet_name="Feeds"
    )

    plants = pd.read_excel(
        input_file,
        sheet_name="Plants"
    )

    recovery = pd.read_excel(
        input_file,
        sheet_name="Feed_Plant_Recovery"
    )

    prices = pd.read_excel(
        input_file,
        sheet_name="Product_Prices"
    )

    fractionation = pd.read_excel(
        input_file,
        sheet_name="Fractionation"
    )

    routing = pd.read_excel(
        input_file,
        sheet_name="Routing"
    )


    # =========================================================
    # 2. BASIC LISTS
    # =========================================================

    feed_ids = feeds["Feed_ID"].tolist()
    plant_ids = plants["Plant_ID"].tolist()
    frac_ids = fractionation["Fractionator_ID"].tolist()


    # =========================================================
    # 3. DEMO FRACTIONATION CAPACITIES
    # =========================================================
    # Original synthetic capacities were very restrictive.
    # These revised values create a more useful demonstration
    # while still allowing downstream bottlenecks.

    # Use the scenario capacities supplied by the user/input workbook.
    # The frontend sample scenario exposes these values so they can be edited.
    fractionation_demo = fractionation.copy()


    # =========================================================
    # 4. DEMO FEED-PLANT RECOVERY VARIATION
    # =========================================================
    # Makes the economic difference between routes more visible
    # in the synthetic demonstration.

    recovery_demo = recovery.copy()

    for i, row in recovery_demo.iterrows():

        f_num = int(row["Feed_ID"][1:])
        p_num = int(row["Plant_ID"][1:])

        route_factor = (
            0.88
            + ((f_num * 3 + p_num * 2) % 7) * 0.02
        )

        for col in [
            "C2_Recovery",
            "C3_Recovery",
            "C4_Recovery",
            "C5plus_Recovery"
        ]:

            adjusted_value = row[col] * route_factor

            recovery_demo.loc[i, col] = min(
                0.99,
                max(
                    0.70,
                    adjusted_value
                )
            )


    # =========================================================
    # 5. PRICE AND MOLECULAR-WEIGHT LOOKUPS
    # =========================================================

    price_lookup = (
        prices
        .set_index("Component")["Planning_Price"]
        .to_dict()
    )

    mw_lookup = (
        prices
        .set_index("Component")[
            "Molecular_Weight_kg_per_kmol"
        ]
        .to_dict()
    )


    # =========================================================
    # 6. FRACTIONATOR RECOVERY LOOKUP
    # =========================================================

    frac_recovery = {}

    for _, row in fractionation_demo.iterrows():

        fr = row["Fractionator_ID"]

        frac_recovery[(fr, "C2")] = row["C2_Recovery"]
        frac_recovery[(fr, "C3")] = row["C3_Recovery"]
        frac_recovery[(fr, "C4")] = row["C4_Recovery"]
        frac_recovery[(fr, "C5+")] = row["C5plus_Recovery"]


    # =========================================================
    # 7. ALLOWED ROUTING LOOKUP
    # =========================================================

    allowed_routes = {
        (
            row["Plant_ID"],
            row["Fractionator_ID"]
        ): row["Route_Allowed"]

        for _, row in routing.iterrows()
    }


    # =========================================================
    # 8. CREATE ALL ALLOWED FULL ROUTES
    # Feed -> Plant -> Fractionator
    # =========================================================

    full_routes = []

    for f in feed_ids:

        for p in plant_ids:

            for fr in frac_ids:

                if allowed_routes[(p, fr)] == 1:

                    full_routes.append(
                        (f, p, fr)
                    )


    # =========================================================
    # 9. CALCULATE ROUTE ECONOMICS
    # AND NGL LOAD
    # =========================================================

    full_value_lookup = {}
    ngl_load_lookup = {}

    for f, p, fr in full_routes:

        feed_row = feeds.loc[
            feeds["Feed_ID"] == f
        ].iloc[0]

        plant_row = recovery_demo[
            (recovery_demo["Feed_ID"] == f)
            &
            (recovery_demo["Plant_ID"] == p)
        ].iloc[0]


        # -----------------------------------------------------
        # C1 RESIDUE GAS VALUE
        # -----------------------------------------------------

        c1_value = (
            feed_row["C1_mol_pct"] / 100
            * plant_row["C1_Retention"]
            * C1_MMBTU_PER_DAY_PER_MMSCFD
            * price_lookup["C1"]
        )

        total_value = c1_value
        ngl_load = 0


        # -----------------------------------------------------
        # C2 / C3 / C4 / C5+
        # -----------------------------------------------------

        components = [
            (
                "C2",
                "C2_mol_pct",
                "C2_Recovery"
            ),
            (
                "C3",
                "C3_mol_pct",
                "C3_Recovery"
            ),
            (
                "C4",
                "C4_mol_pct",
                "C4_Recovery"
            ),
            (
                "C5+",
                "C5plus_mol_pct",
                "C5plus_Recovery"
            )
        ]

        for (
            component,
            composition_column,
            plant_recovery_column
        ) in components:

            plant_product_kmol = (
                KMOL_PER_DAY_PER_MMSCFD
                * feed_row[composition_column] / 100
                * plant_row[plant_recovery_column]
            )

            # Load entering fractionation
            ngl_load += plant_product_kmol


            # Apply fractionator recovery
            final_product_kmol = (
                plant_product_kmol
                * frac_recovery[
                    (fr, component)
                ]
            )


            # Convert kmol/day to tonnes/day
            tonnes = (
                final_product_kmol
                * mw_lookup[component]
                / 1000
            )


            # Product revenue
            component_value = (
                tonnes
                * price_lookup[component]
            )

            total_value += component_value


        full_value_lookup[
            (f, p, fr)
        ] = total_value

        ngl_load_lookup[
            (f, p, fr)
        ] = ngl_load


    # =========================================================
    # 10. DECISION VARIABLES
    # =========================================================
    #
    # First:
    # one variable for each Feed -> Plant -> Fractionator route
    #
    # Then:
    # one excess / curtailment variable for each feed
    #

    n_routes = len(full_routes)
    n_feeds = len(feed_ids)


    # =========================================================
    # 11. MAIN OPTIMIZATION OBJECTIVE
    # =========================================================
    #
    # scipy.linprog MINIMIZES.
    #
    # Therefore:
    #
    # maximize revenue
    #
    # becomes
    #
    # minimize negative revenue
    #
    # Excess / curtailed gas has zero artificial value.
    #

    route_objective = [
        -full_value_lookup[(f, p, fr)]

        for f, p, fr in full_routes
    ]

    curtailment_objective = [
        0
        for f in feed_ids
    ]

    c = np.array(
        route_objective
        +
        curtailment_objective
    )


    # =========================================================
    # 12. FEED BALANCE CONSTRAINTS
    # =========================================================
    #
    # Processed gas + excess gas = available gas
    #

    A_eq = []
    b_eq = []

    for feed_index, f in enumerate(feed_ids):

        row = [
            0
        ] * (
            n_routes
            +
            n_feeds
        )

        for i, (
            route_f,
            route_p,
            route_fr
        ) in enumerate(full_routes):

            if route_f == f:

                row[i] = 1


        # Excess / curtailment variable
        row[
            n_routes
            +
            feed_index
        ] = 1


        available = feeds.loc[
            feeds["Feed_ID"] == f,
            "Available_Flow_MMSCFD"
        ].iloc[0]


        A_eq.append(row)
        b_eq.append(available)


    # =========================================================
    # 13. PLANT CAPACITY CONSTRAINTS
    # =========================================================

    A_ub = []
    b_ub = []

    for p in plant_ids:

        row = [
            1
            if route_p == p
            else 0

            for (
                route_f,
                route_p,
                route_fr
            ) in full_routes
        ]

        # Curtailment variables do not use plant capacity
        row += [
            0
        ] * n_feeds


        capacity = plants.loc[
            plants["Plant_ID"] == p,
            "Max_Capacity_MMSCFD"
        ].iloc[0]


        A_ub.append(row)
        b_ub.append(capacity)


    # =========================================================
    # 14. FRACTIONATION CAPACITY CONSTRAINTS
    # =========================================================

    for fr in frac_ids:

        row = []

        for (
            f,
            p,
            route_fr
        ) in full_routes:

            if route_fr == fr:

                row.append(
                    ngl_load_lookup[
                        (f, p, route_fr)
                    ]
                )

            else:

                row.append(0)


        # Curtailment variables do not load fractionators
        row += [
            0
        ] * n_feeds


        capacity = fractionation_demo.loc[
            fractionation_demo[
                "Fractionator_ID"
            ] == fr,
            "Max_NGL_kmol_per_day"
        ].iloc[0]


        A_ub.append(row)
        b_ub.append(capacity)


    # =========================================================
    # 15. SOLVE MAIN OPTIMIZATION
    # =========================================================

    result = linprog(
        c,

        A_ub=np.array(A_ub),
        b_ub=np.array(b_ub),

        A_eq=np.array(A_eq),
        b_eq=np.array(b_eq),

        bounds=(0, None),

        method="highs"
    )


    if not result.success:

        raise RuntimeError(
            "Optimization failed: "
            +
            result.message
        )


    # =========================================================
    # 16. BUILD OPTIMAL ALLOCATION OUTPUT
    # =========================================================

    allocations = []

    for i, (
        f,
        p,
        fr
    ) in enumerate(full_routes):

        flow = result.x[i]

        if flow > 0.001:

            value = full_value_lookup[
                (f, p, fr)
            ]

            allocations.append({

                "feed": f,

                "plant": p,

                "fractionator": fr,

                "flow_mmscfd":
                    round(
                        float(flow),
                        2
                    ),

                "value_per_mmscfd":
                    round(
                        float(value),
                        2
                    ),

                "daily_revenue":
                    round(
                        float(
                            flow
                            *
                            value
                        ),
                        2
                    )
            })


    # =========================================================
    # 17. EXCESS / CURTAILED FEED
    # =========================================================

    curtailed_values = result.x[
        n_routes:
    ]

    curtailment = []

    for f, excess in zip(
        feed_ids,
        curtailed_values
    ):

        curtailment.append({

            "feed": f,

            "excess_mmscfd":
                round(
                    float(excess),
                    2
                )
        })


    # =========================================================
    # 18. MAIN OPTIMIZER SUMMARY
    # =========================================================

    total_processed = sum(
        item["flow_mmscfd"]
        for item in allocations
    )

    total_excess = sum(
        item["excess_mmscfd"]
        for item in curtailment
    )

    optimized_revenue = sum(
        item["daily_revenue"]
        for item in allocations
    )


    # =========================================================
    # 19. BASELINE OPERATING SCENARIO
    # =========================================================
    #
    # Synthetic conventional routing preference.
    #
    # This represents a simple fixed operating philosophy,
    # rather than dynamic economic optimization.
    #

    preferred_plant = {

        "F1": "P1",

        "F2": "P1",

        "F3": "P2",

        "F4": "P2",

        "F5": "P3",

        "F6": "P4",

        "F7": "P5",

        "F8": "P5"
    }


    preferred_frac = {

        "P1": "FR1",

        "P2": "FR2",

        "P3": "FR2",

        "P4": "FR3",

        "P5": "FR3"
    }


    baseline_scores = []

    for f, p, fr in full_routes:

        score = 0

        # Strong preference for historical/default plant
        if p == preferred_plant[f]:

            score += 100


        # Secondary preferred fractionator
        if fr == preferred_frac[p]:

            score += 10


        # Small incentive to process gas
        score += 1


        baseline_scores.append(
            -score
        )


    baseline_curtailment = [
        0
        for f in feed_ids
    ]


    c_baseline = np.array(
        baseline_scores
        +
        baseline_curtailment
    )


    # =========================================================
    # 20. SOLVE BASELINE
    # =========================================================

    result_baseline = linprog(
        c_baseline,

        A_ub=np.array(A_ub),
        b_ub=np.array(b_ub),

        A_eq=np.array(A_eq),
        b_eq=np.array(b_eq),

        bounds=(0, None),

        method="highs"
    )


    if not result_baseline.success:

        raise RuntimeError(
            "Baseline optimization failed: "
            +
            result_baseline.message
        )


    # =========================================================
    # 21. CALCULATE BASELINE REVENUE
    # =========================================================

    baseline_revenue = 0

    for i, (
        f,
        p,
        fr
    ) in enumerate(full_routes):

        flow = result_baseline.x[i]

        baseline_revenue += (
            flow
            *
            full_value_lookup[
                (f, p, fr)
            ]
        )


    # =========================================================
    # 22. BUSINESS VALUE
    # =========================================================

    incremental_daily_value = (
        optimized_revenue
        -
        baseline_revenue
    )

    incremental_annual_value = (
        incremental_daily_value
        *
        365
    )


    improvement_pct = 0

    if baseline_revenue > 0:

        improvement_pct = (
            incremental_daily_value
            /
            baseline_revenue
            *
            100
        )


    # =========================================================
    # 23. FINAL API RESPONSE
    # =========================================================

    return {

        "status":
            "Optimal",

        "total_available_mmscfd":
            round(
                float(
                    feeds[
                        "Available_Flow_MMSCFD"
                    ].sum()
                ),
                2
            ),

        "total_processed_mmscfd":
            round(
                float(total_processed),
                2
            ),

        "total_excess_mmscfd":
            round(
                float(total_excess),
                2
            ),

        "baseline_daily_revenue":
            round(
                float(baseline_revenue),
                2
            ),

        "optimized_daily_revenue":
            round(
                float(optimized_revenue),
                2
            ),

        "incremental_daily_value":
            round(
                float(
                    incremental_daily_value
                ),
                2
            ),

        "incremental_annual_value":
            round(
                float(
                    incremental_annual_value
                ),
                2
            ),

        "improvement_percent":
            round(
                float(improvement_pct),
                2
            ),

        "allocations":
            allocations,

        "curtailment":
            curtailment
    }


# =============================================================
# OPTIONAL DIRECT TEST
# =============================================================
# Allows:
#
# python optimizer.py
#
# to run the optimizer directly.
# =============================================================

if __name__ == "__main__":

    result = run_optimizer()

    print("\nOptimization Status:")
    print(result["status"])

    print("\nTotal Available Gas:")
    print(
        result[
            "total_available_mmscfd"
        ],
        "MMSCFD"
    )

    print("\nTotal Processed Gas:")
    print(
        result[
            "total_processed_mmscfd"
        ],
        "MMSCFD"
    )

    print("\nTotal Excess Gas:")
    print(
        result[
            "total_excess_mmscfd"
        ],
        "MMSCFD"
    )

    print("\nBaseline Daily Revenue:")
    print(
        "$",
        result[
            "baseline_daily_revenue"
        ]
    )

    print("\nOptimized Daily Revenue:")
    print(
        "$",
        result[
            "optimized_daily_revenue"
        ]
    )

    print("\nIncremental Daily Value:")
    print(
        "$",
        result[
            "incremental_daily_value"
        ]
    )

    print("\nIncremental Annual Value:")
    print(
        "$",
        result[
            "incremental_annual_value"
        ]
    )

    print("\nImprovement:")
    print(
        result[
            "improvement_percent"
        ],
        "%"
    )