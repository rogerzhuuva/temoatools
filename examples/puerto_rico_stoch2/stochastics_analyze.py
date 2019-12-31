import os
import pandas as pd
import temoatools as tt
import multiprocessing
from joblib import Parallel, delayed, parallel_backend


# =======================================================
# Function to evaluate simulations by a single metric
# =======================================================

def analyze_results(metric, folder_db, folder_results, run_name, dbs, all_dbs, db_shift, node_prob, tech_group_dict,
                    prob_type_dict, infra_dict, carbon_tax_dict):
    print(metric)
    # --------------------------------
    # Analyze with temoatools
    # --------------------------------

    create_plots = 'N'  # Create default plots
    save_data = 'Y'  # Do not save data as a csv or xls
    sector_name = 'electric'  # Name of sector to be analyzed

    # Costs
    if metric == 'costs_yearly':
        tt.getCosts(folder_db, dbs, save_data=save_data, create_plots=create_plots, run_name=run_name)

    # Emissions
    elif metric == 'emissions_yearly':
        tt.getEmissions(folder_db, dbs, save_data=save_data, create_plots=create_plots, run_name=run_name)
    # Analyze activity by fuel types
    elif metric == 'activity_by_fuel':
        switch = 'fuel'
        tt.getActivity(folder_db, dbs, switch=switch, sector_name=sector_name, save_data=save_data,
                       create_plots=create_plots, run_name=run_name)

    # Analyze activity by fuel types
    elif metric == 'activity_by_tech':
        switch = 'tech'
        sector_name = 'all'
        tt.getActivity(folder_db, dbs, switch=switch, sector_name=sector_name, save_data=save_data,
                       create_plots=create_plots, run_name=run_name)

    # Analyze capacity by fuel types
    elif metric == 'capacity_by_fuel':
        switch = 'fuel'
        tt.getCapacity(folder_db, dbs, switch=switch, sector_name=sector_name, save_data=save_data,
                       create_plots=create_plots, run_name=run_name)

    # Analyze capacity by fuel types
    elif metric == 'capacity_by_tech':
        switch = 'tech'
        sector_name = 'all'
        tt.getCapacity(folder_db, dbs, switch=switch, sector_name=sector_name, save_data=save_data,
                       create_plots=create_plots, run_name=run_name)
    # --------------------------------
    # Expand Results (only costs and emissions)
    # --------------------------------

    if metric == 'costs_yearly' or metric == 'emissions_yearly'\
            or metric == 'activity_by_fuel' or metric == 'activity_by_tech':

        if metric == 'costs_yearly':
            filename = 'costs_yearly'
        elif metric == 'emissions_yearly':
            filename = 'emissions_yearly'
        elif metric == 'activity_by_fuel':
            filename = 'activity_by_fuel'
        elif metric == 'activity_by_tech':
            filename = 'activity_by_tech'

        tt.stoch_expand(folder_results, filename, db_shift)

    # --------------------------------
    # Resample Results (only costs and emissions)
    # --------------------------------
    if metric == 'costs_yearly' or metric == 'emissions_yearly'\
            or metric == 'activity_by_fuel' or metric == 'activity_by_tech':

        if metric == 'costs_yearly':
            filename = 'costs_yearly_exp'
        elif metric == 'emissions_yearly':
            filename = 'emissions_yearly_exp'
        elif metric == 'activity_by_fuel':
            filename = 'activity_by_fuel_exp'
        elif metric == 'activity_by_tech':
            filename = 'activity_by_tech_exp'

        tt.stoch_resample(folder_results, filename, node_prob)

    # --------------------------------
    # Move to results directory
    # --------------------------------
    cwd = os.getcwd()
    os.chdir(folder_results)

    # --------------------------------
    # Prepare for plotting
    # --------------------------------

    # Naming conventions and conversions
    if metric == 'costs_yearly':
        filename = "costs_yearly_exp_resampled.csv"
        conversion = 1.0 / 100.0  # Convert from cents/kWh to $/kWh/yr
        id_vars = ["database", "scenario", "entry"]
        col_renames = {"scenario": "s", "database": "Scenario"}
        csv_file = "costs_yearly_toPlot.csv"

    elif metric == 'emissions_yearly':
        filename = "emissions_yearly_exp_resampled.csv"
        conversion = 1.0 / 1000.0  # Convert from kton/yr to Mton/yr
        id_vars = ["database", "scenario", "entry"]
        col_renames = {"scenario": "s", "database": "Scenario"}
        csv_file = "emissions_yearly_toPlot.csv"

    elif metric == 'activity_by_fuel':
        filename = "activity_by_fuel_exp_resampled.csv"
        conversion = 1.0 / 1000.0  # GWh to TWh
        id_vars = ["database", "scenario", "fuelOrTech", "entry"]
        col_renames = {"scenario": "s", "database": "Scenario", "fuelOrTech": "Type"}
        csv_file = "activity_by_fuel_toPlot.csv"

    elif metric == 'activity_by_tech':
        filename = "activity_by_tech_exp_resampled.csv"
        conversion = 1.0 / 1000.0  # GWh to TWh
        id_vars = ["database", "scenario", "fuelOrTech", "entry"]
        col_renames = {"scenario": "s", "database": "Scenario", "fuelOrTech": "Type"}
        csv_file = "activity_by_tech_toPlot.csv"

    elif metric == 'capacity_by_fuel':
        filename = "capacity_by_fuel.csv"  # Don't expand and resample these results
        conversion = 1.0  # GW
        id_vars = ["database", "scenario", "fuelOrTech"]
        col_renames = {"scenario": "s", "database": "Scenario", "fuelOrTech": "Type"}
        csv_file = "capacity_by_fuel_toPlot.csv"

    elif metric == 'capacity_by_tech':
        filename = "capacity_by_tech.csv"  # Don't expand and resample these results
        conversion = 1.0  # GW
        id_vars = ["database", "scenario", "fuelOrTech"]
        col_renames = {"scenario": "s", "database": "Scenario", "fuelOrTech": "Type"}
        csv_file = "capacity_by_tech_toPlot.csv"

    # Load and Process data
    df = pd.read_csv(filename, index_col=0)
    if metric == 'costs_yearly' or metric == 'emissions_yearly'\
            or metric == 'activity_by_fuel' or metric == 'activity_by_tech':
        df = df.drop("prob", axis=1)
    for col in df.columns:
        if 'Unnamed' in col:
            df = df.drop(col, axis=1)
    df2 = pd.melt(df, id_vars=id_vars, var_name="Year", value_name="Value")
    df2.case = "unknown"
    df2.Value = df2.Value * conversion
    for db in all_dbs:
        ind = df2.loc[:, "database"] == db
        df2.loc[ind, "case"] = prob_type_dict[db] + "-" + infra_dict[db] + "-" + carbon_tax_dict[db]
        df2.loc[ind, "database"] = tech_group_dict[db]
        df2.loc[ind, "prob_type"] = prob_type_dict[db]
        df2.loc[ind, "infra"] = infra_dict[db]
        df2.loc[ind, "carbon_tax"] = carbon_tax_dict[db]
        df2.loc[ind, "infra_and_carbon_tax"] = infra_dict[db] + "-" + carbon_tax_dict[db]
    df2 = df2.rename(columns=col_renames)

    # For activity results, change from temoa names to a more standard naming convention
    # if metric == 'activity_by_fuel' or metric == 'activity_by_tech' or metric == 'capacity_by_fuel' or metric == 'capacity_by_tech':
    #     if metric == 'activity_by_fuel' or metric == 'capacity_by_fuel':
    #         # other_renew = "Other renew"
    #         # petrol = "Petroleum"
    #         # type_shift = {"BIO": other_renew, "COAL_TAXED": "Coal", "DSL_TAXED": petrol, "ELC_CENTRAL": "Battery",
    #         #               "ELC_DIST": "Battery", "HYDRO": other_renew, "MSW_LF_TAXED": other_renew,
    #         #               "NATGAS_TAXED": "Natural gas", "OIL_TAXED": petrol, "SOLAR": "Solar", "WIND": "Wind"}
    #
    #         type_shift = {"BIO": "Biomass", "COAL_TAXED": "Coal", "DSL_TAXED": "Diesel", "ELC_CENTRAL": "Battery",
    #                       "ELC_DIST": "Battery", "HYDRO": "Hydro", "MSW_LF_TAXED": "Landfill Gas",
    #                       "NATGAS_TAXED": "Natural Gas", "OIL_TAXED": "Oil", "SOLAR": "Solar", "WIND": "Wind"}
    #
    #     elif metric == 'activity_by_tech' or metric == 'capacity_by_tech':
    #         ex_fsl = "Exist. Fossil"
    #         ex_renew = "Exist. Renewable"
    #         cent_fsl = "Cent. Fossil"
    #         cent_renew = "Cent. Renewable"
    #         dist_fsl = "Dist. Fossil"
    #         dist_renew = "Dist. Renewable"
    #         stor = 'Storage'
    #
    #         type_shift = {'EX_DSL_CC': ex_fsl, 'DIST_COND': 'DIST_COND', 'DIST_TWR': 'DIST_TWR', 'SUB': 'SUB',
    #                       'EC_BATT': stor, 'EX_SOLPV': ex_renew, 'ED_BATT': stor, 'EX_COAL': ex_fsl,
    #                       'EX_HYDRO': ex_renew, 'EX_MSW_LF': ex_renew, 'TRANS': 'TRANS', 'ED_NG_OC': dist_fsl,
    #                       'LOCAL': 'LOCAL', 'EX_DSL_SIMP': ex_fsl, 'ED_NG_CC': dist_fsl, 'EC_NG_CC': cent_fsl,
    #                       'EX_OIL_TYPE3': ex_fsl, 'EX_OIL_TYPE2': ex_fsl, 'EC_WIND': cent_renew, 'EC_SOLPV': cent_renew,
    #                       'UGND_TRANS': 'UGND_TRANS', 'EX_WIND': ex_renew, 'EX_NG_CC': ex_fsl, 'EC_NG_OC': cent_fsl,
    #                       'ED_WIND': dist_renew, 'UGND_DIST': 'UGND_DIST', 'EX_OIL_TYPE1': ex_fsl, 'EC_BIO': cent_renew,
    #                       'ED_BIO': dist_renew, 'ED_SOLPV': dist_renew, 'EC_COAL': cent_fsl, 'EC_DSL_CC': cent_fsl,
    #                       'EC_OIL_CC': cent_fsl, 'COAL_TAX': 'COAL_TAX', 'DSL_TAX': 'DSL_TAX',
    #                       'NATGAS_TAX': 'NATGAS_TAX', 'OIL_TAX': 'OIL_TAX'}
    #
    #     for key in type_shift.keys():
    #         ind = df2.loc[:, "Type"] == key
    #         df2.loc[ind, "Type2"] = type_shift[key]

    # Save file
    df2.to_csv(csv_file)

    # --------------------------------
    # Return to original directory
    # --------------------------------
    os.chdir(cwd)


# ================================
# Main body of script
# ================================
if __name__ == '__main__':

    db_folder = os.getcwd() + '\\stochastic_databases'
    result_folder = os.getcwd() + '\\results'

    print("running")

    run_names = ["2019_12_17", ]

    # Names of databases simulated
    dbs = ["T_0.sqlite","U_0.sqlite"]

    # Node probabilities by case (0 is simulated, 1 is calculated)
    node_prob = {"0": [0.52, 0.32, 0.16],  # Historical (sum must equal 1)
                 "1": [0.2, 0.32, 0.48]}  # Climate Change

    # Dictionary relating simulated databases to calculated results using different distributions
    db_shift = {"T_0": "T_1", "U_0": "U_1",}

    # List of all databases after applying different distributions
    all_dbs = ["T_0.sqlite", "T_1.sqlite", "U_0.sqlite", "U_1.sqlite"]

    # Technology Groups
    tech_group = ['all', ]
    tech_group_dict = {"T_0.sqlite": tech_group[0], "T_1.sqlite": tech_group[0],
                       "U_0.sqlite": tech_group[0], "U_1.sqlite": tech_group[0], }

    # Historical or Climate Change Probabilities
    prob = ["Historical", "Climate Change"]
    prob_type_dict = {"T_0.sqlite": prob[0], "T_1.sqlite": prob[1], "U_0.sqlite": prob[0], "U_1.sqlite": prob[1]}

    # Infrastructure Type
    infra = ["all", ]
    infra_dict = {"T_0.sqlite": infra[0], "T_1.sqlite": infra[0],"U_0.sqlite": infra[0], "U_1.sqlite": infra[0]}

    # Carbon Tax
    carbon_tax = ["No Tax", "Tax"]
    carbon_tax_dict = {"T_0.sqlite": carbon_tax[0], "T_1.sqlite": carbon_tax[0],
                       "U_0.sqlite": carbon_tax[1], "U_1.sqlite": carbon_tax[1]}

    # Iterate through each run
    for run_name in run_names:
        print run_name
        folder_db = db_folder + "\\" + run_name
        folder_results = result_folder + "\\" + run_name

        # metrics = ['costs_yearly', 'emissions_yearly', 'activity_by_fuel', 'activity_by_tech', 'capacity_by_fuel',
        #            'capacity_by_tech']

        metrics = ['costs_yearly', 'emissions_yearly', 'activity_by_fuel', 'activity_by_tech']

        num_cores = multiprocessing.cpu_count() - 1  # Save one core for other processes

        # Perform simulations in parallel
        with parallel_backend('multiprocessing', n_jobs=num_cores):
            Parallel(n_jobs=num_cores, verbose=5)(
                delayed(analyze_results)(metric, folder_db, folder_results, run_name, dbs, all_dbs, db_shift, node_prob,
                                         tech_group_dict, prob_type_dict, infra_dict, carbon_tax_dict) for metric in
                metrics)