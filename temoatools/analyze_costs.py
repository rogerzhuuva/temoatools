import os
import sqlite3
import pandas as pd

debug = False
resolution = 1000  # DPI


# ==============================================================================
def getCosts(folders, dbs, elc_dmd='ELC_DMD', conversion=0.359971, save_data='N', create_plots='N', run_name=''):
    #    inputs:
    #    1) folders         - paths containing dbs (list or single string if all in the same path)
    #    2) dbs             - names of databases (list)
    #    3) elc_dmd         - quantity that represents electricity demand
    #    4) conversion      - converts from cost units per activity to cents/kWH
    #           default is conversion from M$/PJ to cents/KWh (1E6*100 / (2.778E8))
    #    5) save_data         - 'Y' or 'N', default is 'N'
    #    6) create_plots     - 'Y' or 'N', default is 'N'
    #    7) run_name         - Used for saving results in dedicated folder
    #
    #    outputs:
    #    1) yearlyCosts     - pandas DataFrame holding yearly_costs
    #    2) LCOE            - dictionary holding LCOE, calculated wrt first model year
    # ==============================================================================
    # Save original directory
    wrkdir = os.getcwd()

    # If only a single db and folder provided, change to a list
    if type(dbs) == str and type(folders) == str:
        dbs = [dbs]
        folders = [folders]
    # If a list of folders is provided with one database, only use first folder
    elif type(dbs) == str:
        dbs = [dbs]
        folders = [folders[0]]
    # If only a single folder provided, create a list of the same folder
    elif type(folders) == str:
        fldrs = []
        for db in dbs:
            fldrs.append(folders)
        folders = fldrs

    # Create a dataframe
    yearlyCosts = pd.DataFrame()
    LCOE = pd.DataFrame()

    # Iterate through each db
    for folder, db in zip(folders, dbs):
        # Access costs
        yearlyCosts_single, LCOE_single = SingleDB(folder, db, elc_dmd=elc_dmd, conversion=conversion)

        yearlyCosts = pd.concat([yearlyCosts, yearlyCosts_single])
        LCOE = pd.concat([LCOE, LCOE_single])

    # Reset index (remove multi-level indexing, easier to use in Excel)
    yearlyCosts = yearlyCosts.reset_index()
    LCOE = LCOE.reset_index()

    # Directory to hold results
    if save_data == 'Y' or create_plots == 'Y':
        create_results_dir(wrkdir=wrkdir, run_name=run_name)

    # Save results to CSV
    if save_data == 'Y':
        # savename = 'Results_Costs.xls'
        # Create connection to excel
        # writer = pd.ExcelWriter(savename)
        # Write data
        # yearlyCosts.to_excel(writer, 'yearlyCosts')
        # LCOE.to_excel(writer, 'LCOE')
        yearlyCosts.to_csv('costs_yearly.csv')
        LCOE.to_csv('LCOE.csv')
        # Save
        # writer.save()

    # Plot Results
    if create_plots == 'Y':
        # yearlyCosts
        titlename = 'Yearly Costs'
        ax = yearlyCosts.plot(stacked=False, title=titlename)
        ax.set_xlabel("Year [-]")
        ax.set_ylabel("Costs [cents/kWh]")
        fig = ax.get_figure()
        fig.savefig('costs_yearly.png', dpi=resolution)

        # LCOE
        titlename = 'LCOE'
        # df_LCOE = pd.DataFrame.from_dict(LCOE,orient='index')
        ax = LCOE.plot.bar(stacked=False, title=titlename)
        ax.set_xlabel("Scenario [-]")
        ax.set_ylabel("Levelized Cost of Electricity [cents/kWh]")
        fig = ax.get_figure()
        fig.savefig('LCOE.png', dpi=resolution)

    # Return to original directory
    os.chdir(wrkdir)

    return yearlyCosts, LCOE

    # ==============================================================================


def SingleDB(folder, db, elc_dmd='ELC_DMD', conversion=0.359971):
    #    inputs:
    #    1) folder          - path containing db
    #    2) db              - names of databases
    #    3) elc_dmd         - quantity that represents electricity demand
    #    4) conversion      - converts from cost units per activity to cents/kWH
    #
    #    outputs:
    #    1) yearlyCosts     - pandas Series holding yearly costs
    #    2) LCOE            - LCOE (float), calculated wrt first model year
    # ==============================================================================
    print("Analyzing db: ", db)

    # Save original directory
    origDir = os.getcwd()

    # Move to folder
    os.chdir(folder)

    # Connect to Database
    con = sqlite3.connect(db)
    cur = con.cursor()

    #   Identify Unique Scenarios
    qry = 'SELECT * FROM Output_Objective'
    cur.execute(qry)
    db_objective = cur.fetchall()
    scenarios = []
    for scenario, objective_name, total_system_cost in db_objective:
        if scenario not in scenarios:
            scenarios.append(scenario)

    # Review time_periods, only interested in future periods
    qry = 'SELECT * FROM time_periods'
    cur.execute(qry)
    db_t_periods = cur.fetchall()

    t_periods = []
    for t_period, flag in db_t_periods:
        if flag == 'f':
            t_periods.append(t_period)

    t_periods = sorted(t_periods)
    t_periods = t_periods[:-1]

    # Review technologies  
    qry = "SELECT * FROM technologies"
    cur.execute(qry)
    db_tech = cur.fetchall()

    techs = []
    for tech, flag, sector, tech_desc, tech_category in db_tech:
        techs.append(tech)

    # ------------
    # CostInvest
    # ------------
    # Access database
    qry = "SELECT * FROM CostInvest"
    cur.execute(qry)
    db_CostInvest = cur.fetchall()

    # Create dataframe to hold technology costs (initialized to zero)
    rows = t_periods
    cols = techs
    df_CostInvest = pd.DataFrame(data=0.0, index=rows, columns=cols)

    # Store Data
    for tech, vintage, cost_invest, cost_invest_units, cost_invest_notes in db_CostInvest:
        if vintage in t_periods and tech in techs:
            df_CostInvest.loc[vintage, tech] = cost_invest

    # ------------
    # CostFixed
    # ------------
    # Access database
    qry = "SELECT * FROM CostFixed"
    cur.execute(qry)
    db_CostFixed = cur.fetchall()

    # Create dataframe to hold technology costs (initialized to zero)
    rows = t_periods
    cols = techs
    df_CostFixed = pd.DataFrame(data=0.0, index=rows, columns=cols)

    # Store Data
    for periods, tech, vintage, cost_fixed, cost_fixed_units, cost_fixed_notes in db_CostFixed:
        if periods in t_periods and tech in techs:
            df_CostFixed.loc[periods, tech] = cost_fixed

            # ------------
    # CostVariable
    # ------------
    # Access database
    qry = "SELECT * FROM CostVariable"
    cur.execute(qry)
    db_CostVariable = cur.fetchall()

    # Create dataframe to hold technology costs (initialized to zero)
    rows = t_periods
    cols = techs
    df_CostVariable = pd.DataFrame(data=0.0, index=rows, columns=cols)

    # Store Data
    for periods, tech, vintage, cost_variable, cost_variable_units, cost_variable_notes in db_CostVariable:
        if periods in t_periods and tech in techs:
            df_CostVariable.loc[periods, tech] = cost_variable

    # ------------
    # Discount Rate
    # ------------
    qry = "SELECT * FROM GlobalDiscountRate"
    cur.execute(qry)
    db_rate = cur.fetchall()
    rate = db_rate[0][0]

    # ------------
    # LifetimeLoanTech
    # ------------
    # Access database
    qry = "SELECT * FROM LifetimeLoanTech"
    cur.execute(qry)
    db_loanLife = cur.fetchall()

    # Create dataframe to hold yearly installs (initialized to zero)
    rows = techs
    cols = ["loan"]
    df_loanLife = pd.DataFrame(data=0.0, index=rows, columns=cols)

    # Store Data
    for tech, loan, loan_notes, in db_loanLife:
        df_loanLife.loc[tech, "loan"] = loan

    # Create pandas DataFrame to hold yearlyEmissions for all scenarios
    index = pd.MultiIndex.from_product([[db], scenarios], names=['database', 'scenario'])
    yearlyCosts = pd.DataFrame(index=index, columns=t_periods)
    yearlyCosts = yearlyCosts.fillna(0.0)  # Default value to zero
    LCOE = pd.DataFrame(index=index, columns=['LCOE'])
    LCOE = LCOE.fillna(0.0)  # Default value to zero

    # ------------
    # Iterate through scenarios
    # ------------
    for s in scenarios:
        print("\tAnalyzing Scenario: ", s)

        # Create dataframe to hold yearly costs (initialized to zero)
        rows = t_periods
        cols = ['CostInvest', 'CostFixed', 'CostVariable', 'CostTotal', 'ELC_DMD', 'ELC_Cost']
        df = pd.DataFrame(data=0.0, index=rows, columns=cols)

        # ------------
        # Activity
        # ------------
        # Access database
        qry = "SELECT * FROM Output_VFlow_Out"
        cur.execute(qry)
        db_activity = cur.fetchall()

        # Create dataframe to hold activity (initialized to zero)
        rows = t_periods
        cols = techs
        df_activity = pd.DataFrame(data=0.0, index=rows, columns=cols)

        # Store Data
        for scenario, sector, t_period, t_season, t_day, input_comm, tech, vintage, output_comm, vflow_out in db_activity:
            if scenario == s:
                # Store Activity for each technology
                if t_period in t_periods and tech in techs:
                    df_activity.loc[t_period, tech] = df_activity.loc[t_period, tech] + vflow_out
                # Store electricity demand
                if output_comm == elc_dmd:
                    df.loc[t_period, 'ELC_DMD'] = df.loc[t_period, 'ELC_DMD'] + vflow_out

        # ------------
        # New Capacity
        # ------------
        # Access database
        qry = "SELECT * FROM Output_V_Capacity"
        cur.execute(qry)
        db_newCapacity = cur.fetchall()

        # Create dataframe to hold yearly installs (initialized to zero)
        rows = t_periods
        cols = techs
        df_newCapacity = pd.DataFrame(data=0.0, index=rows, columns=cols)

        # Store Data
        for scenario, sector, tech, vintage, capacity, in db_newCapacity:
            if scenario == s:
                if vintage in t_periods and tech in techs:
                    df_newCapacity.loc[vintage, tech] = capacity

        # ------------
        # Active Capacity
        # ------------
        # Access database
        qry = "SELECT * FROM Output_CapacityByPeriodAndTech"
        cur.execute(qry)
        db_activeCapacity = cur.fetchall()

        # Create dataframe to hold yearly installs (initialized to zero)
        rows = t_periods
        cols = techs
        df_activeCapacity = pd.DataFrame(data=0.0, index=rows, columns=cols)

        # Store Data
        for scenario, sector, t_period, tech, capacity, in db_activeCapacity:
            if scenario == s:
                if t_period in t_periods and tech in techs:
                    df_activeCapacity.loc[t_period, tech] = capacity

        # ------------
        # Analysis - Investments
        # ------------
        # Create dataframe (initialized to zero)
        rows = t_periods
        cols = techs
        df_investments = pd.DataFrame(data=0.0, index=rows, columns=cols)

        for year in t_periods:
            for tech in techs:
                costInvest = df_newCapacity.loc[year, tech] * df_CostInvest.loc[year, tech]
                df_investments.loc[year, tech] = df_investments.loc[year, tech] + costInvest

        # ------------
        # Analysis - Translate Investments to Loans
        # ------------
        # Create dataframe (initialized to zero)
        rows = t_periods
        cols = techs
        df_loanPayments = pd.DataFrame(data=0.0, index=rows, columns=cols)

        for tech in techs:
            for buildYear in t_periods:

                if df_investments.loc[buildYear, tech] > 0:
                    loan = df_investments.loc[buildYear, tech]
                    N = df_loanLife.loc[tech, "loan"]
                    # Assume Fixed-Rate Payment (https://www.investopedia.com/terms/f/fixed-rate-payment.asp)
                    annualPayment = rate / (1 - (1 + rate) ** -N) * loan
                    if debug == True:
                        print("Tech: " + tech + ",Year: " + str(buildYear) + ",YearlyPayment: " + str(annualPayment))

                    for year in t_periods:
                        if buildYear <= year and year <= buildYear + N:
                            df_loanPayments.loc[year, tech] = df_loanPayments.loc[year, tech] + annualPayment

        # ------------
        # Analysis - Translate to yearly costs
        # ------------
        for year in t_periods:
            for tech in techs:
                # CostInvest (loan payments)
                costInvest = df_loanPayments.loc[year, tech]
                df.loc[year, 'CostInvest'] = df.loc[year, 'CostInvest'] + costInvest

                # CostFixed
                costFixed = df_activeCapacity.loc[year, tech] * df_CostFixed.loc[year, tech]
                df.loc[year, 'CostFixed'] = df.loc[year, 'CostFixed'] + costFixed

                # CostVariable
                costVariable = df_activity.loc[year, tech] * df_CostVariable.loc[year, tech]
                df.loc[year, 'CostVariable'] = df.loc[year, 'CostVariable'] + costVariable

                # Sum Costs
                totalTechCost = costInvest + costFixed + costVariable
                df.loc[year, 'CostTotal'] = df.loc[year, 'CostTotal'] + totalTechCost

            # Calculate Yearly Cost of Electricity
            df.loc[year, 'ELC_Cost'] = df.loc[year, 'CostTotal'] / df.loc[year, 'ELC_DMD'] * conversion

        # yearlyCosts_single = df.ELC_Cost

        # ------------
        # Analysis - Calculate LCOE (based on initial year)
        # based on: https://www.energy.gov/sites/prod/files/2015/08/f25/LCOE.pdf
        # ------------
        num = 0.0
        denom = 0.0

        for year in t_periods:
            t = year - t_periods[0]
            num = num + df.loc[year, 'CostTotal'] / (1.0 + rate) ** t
            denom = denom + df.loc[year, 'ELC_DMD'] / (1.0 + rate) ** t

        LCOE_single = num / denom * conversion

        # df.loc[t_periods[0],'LCOE'] = LCOE

        # Store yearlyCosts_single and LCOE_single
        for year in df.index:
            yearlyCosts.loc[(db, s), year] = df.loc[year, 'ELC_Cost']
        LCOE.loc[(db, s), year] = LCOE_single

    # Return to original directory
    os.chdir(origDir)

    # ------------
    # Return Calculations
    # ------------
    return yearlyCosts, LCOE
