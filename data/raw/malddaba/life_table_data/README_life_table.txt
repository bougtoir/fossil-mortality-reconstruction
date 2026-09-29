#######
# MALDDABA life table
#######
The dataset on life table frol malddaba is presented as an R list “malddaba_life_table” with all the different information used from Malddba, life tables and demographic outputs for each populations. More details on the procedure used to build the life tables and compute the demographic output is given in the supplementary S2 of the original malddaba publication.

#######
# List malddaba_life_table
#######
Each element of this list corresponds to one full life table associated with a specific species. Each specific element contains 6 data frames with information on the life table.

-	Data frame species
Spe: genus and species latin name

-	Data frame data_used
Contain all the information regarding the data and the methodology used to build the different life tables. One row in that table corresponds to information associated with one life table.
Immature_survival_life_table_id: MALDDABA ID used for the survival information of young non-reproducing individuals
Adult_survival_life_table_id: MALDDABA ID used for the survival information of adult reproducing individuals
Censored_survival: whether survival series was artificially ended by censoring with a null survival at last age (Y or N)
Extended_survival: whether a procedure to extend survival probability at old ages was applied (Y or N)
Survival_modeled: whether survival from reported age-dependent model was used instead of the raw full age estimates (Y or N)
Survival_comments: any comments associated with a specific procedure used to compute Sx series for this population
Mx_id: MALDDABA ID used for the reproduction of individuals if mx data are extracted directly
N_offspring_id: MALDDABA ID used for the calculation of mx series if the age-specific age specific number of offspring produced per females was used
P_reproduce_id: MALDDABA ID used for the calculation of mx series if the age specific probability to reproduce was used
Litter_size_id: MALDDABA ID used for the calculation of mx series if the age specific litter size was used
Censored_reproduction: whether mx series was artificially censored at last age based on the Sx series (Y or N)
Extended_reproduction: whether a procedure to extend mx series at old ages was applied  (Y or N)
Reproduction_modeled: whether reproduction from reported age-dependent model was used instead of the raw full age estimates (Y or N)
Reproduction_comments: any comments associated to a specific procedure used to compute reproduction for this population 
Age_interval: age interval in years used for the building of the life tables

-	Data frame life_table
Combined_life_table_id: specific id of the life table (to link the life table id with the info dataframe)
Age: age (in years)
Sx: age-specific Sx, survival
Lx: age-specific lx, cumulative survival
Mx: average age-specific mx, number of daughters produced by females

-	Data frame extended_life_table
Combined_life_table_id: specific id of the life table (to link the life table id with the info dataframe)
Age: age (in years)
Sx: age-specific Sx, survival
Lx: age-specific lx, cumulative survival
Mx: average age-specific mx, number of daughters produced by females
dx: proportion of individuals dx dying in a specific age class
ex: life expectancy at age x
vx: age-specific reproductive value 

-	Data frame demographic_metric
AFR: age at first reproduction (in years)
R0: R0, net reproductive rate value
r: r, asymptotic growth rate value
Tb: population generation time Tb value (in years)
Tb: Cohort generation time Tc value (in years)
