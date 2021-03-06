# ======================================================================================================================
# test_build_single_MC_temoa_model.py
# Jeff Bennett, jab6ft@virginia.edu
# The purpose of this script is to demonstrate the ability of temoatools to build a single Monte Carlo input.
# ======================================================================================================================
import temoatools as tt

# =======================================================
# Model Inputs
# =======================================================
modelInputs_XLSX = 'data.xlsx'
scenarioInputs = 'scenarios.xlsx'
scenarioName = 'A'
sensitivityInputs = 'sensitivityVariables.xlsx'
sensitivityMultiplier = 10.0  # percent perturbation*

# Select which approach to use (both do the same thing, one makes the steps more clear)
option = 2

# =======================================================
# Move modelInputs to database
# =======================================================
modelInputs = tt.move_data_to_db(modelInputs_XLSX, path='data')

# Create monte carlo cases
n_cases = 1
caseNum = 0
cases = tt.createMonteCarloCases(scenarioInputs, scenarioName, sensitivityInputs, sensitivityMultiplier,
                                 n_cases=n_cases, path='data')
cols = ['type', 'variable', 'tech', caseNum]
MCinputs = cases.loc[:, cols]
MCinputs = MCinputs.rename(columns={caseNum: 'multiplier'})

# =======================================================
# Option 1 - Run Temoa Model Builder with single function
# =======================================================
if option == 1:
    #    from TemoaModelBuild import BuildModel
    model_filename = modelInputs[:modelInputs.find('.')] + '_' + scenarioName
    tt.build(modelInputs, scenarioInputs, scenarioName, model_filename, path='data')

# =======================================================
# Option 2 - Run Temoa Model Builder with access to all inputs, local variables and outputs
# =======================================================
if option == 2:
    path = 'data'
    # Get empty dictionary of local variables
    local = tt.temoa_model_build.getEmptyLocalDict()

    # Process scenarios
    local = tt.temoa_model_build.processScenarios(scenarioInputs, scenarioName, local, path)

    # Read-in inputs as dictionary
    inputs = tt.temoa_model_build.inputs2Dict(modelInputs, path)

    # Create empty dictionary of temoa outputs
    outputs = tt.temoa_model_build.getEmptyTemoaDict()

    # System parameters
    local, outputs = tt.temoa_model_build.processSystem(inputs, local, outputs)

    # PowerPlants
    local, outputs = tt.temoa_model_build.processPowerPlants(inputs, local, outputs)

    # Fuels
    local, outputs = tt.temoa_model_build.processFuels(inputs, local, outputs)

    # Connections
    local, outputs = tt.temoa_model_build.processConnections(inputs, local, outputs)

    # Copy db_schema_temoa_mod.db and write(commit) outputs to it
    model_filename = modelInputs[:modelInputs.find('.')] + '_' + scenarioName
    tt.temoa_model_build.Write2Temoa(outputs, model_filename)
