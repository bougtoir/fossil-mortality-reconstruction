# Author: Eva Maria Griebeler, 
#         Institut für Organismische und Molekulare Evolutionsbiologie, 
#         Evolutionäre Ökologie, 
#         Johannes Gutenberg-Universität Mainz, 
#         55099 Mainz, Germany
#         em.griebeler@uni-mainz.de


The following R-script was used for
checking whether surviorship curves of dinosaurs and extant species are from SAD populations
---------------------------------------------------------------------------------------------
R-package:
no additional package required

File:
check_for_SAD_populations_extant_species_dinosaurs.R

Description:
This R-script provides the algorithm for searching for the best combination of lambda and R0 for a given empirical survivorship curve 
and a given fecundity schedule (mx model).
It can be run for all empirical survivorship curves (from dinosaurs and extant species) used in the paper.

If you like to apply this R-script to your own taxon you must create code that looks like the following:

# Albertosaurus sacrophagus from Erickson et al. 2004, 2006
empirical_x <-  c(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28)
   # all ages from zero to maximum longevity seen in the taxon
empirical_lx <- c(1000, 1000, 954, 954, 909, 909, 864, 864, 818, 773, 773, 727, 682, 636, 545, 456, 409, 312, 273, 182, 136, 91, 91, 45, 45, 45, 45, 45, 1)
   # lx values for each age x
empirical_lx <- log10(empirical_lx)
   # log-transform lx
Dinoname <- "Albertosaurus sacrophagus 2006"  # this string is only used in the plots and for textual output
BM <- 1223                 # body mass in kg
ASM <- 14                  # age at sexual maturity from growth curve
max_longevity <- 28        # maximum longevity, asymptotic age from growth curves
AEN_model <- "b"           # the bird model on annual egg number is used
#AEN_model <- "r"          # the reptile model on annual egg number is used
# for extant species AEN_model <- "AnAge" must be coded if you have information on its annual egg number, in this case you have also to change the
# next command accordingly; e.g., annual_offspring_number <- 5
annual_offspring_number <- annual_egg_number(BM, AEN_model) # number of offspring per year, fecundity, estimated from allometries

The script plots the empirical survivorship curve and tests all five mx models.
After having found the best combination of R0 and lambda for a given mx model, parameter estimates and values on goodness of fit are printed
and the fitted survivorship curve is plotted in the same plot.


The following R-script was used for
estimating lambda for SAD populations of dinosaurs and extant species
----------------------------------------------------------------------
R-package:
no additional package required

File:
SAD_survivorship_curves_extant_species_dinosaurs.R

Description:
The R-script provides the code to calculate lambda values for SAD populations of the dinosaurs and extant species from the paper.
The structure of this script is very similar to that of the script check_for_SAD_populations_extant_species_dinosaurs.R.

If you like to apply this R-script to your own taxon you must create the identical code as in this previous script. 

The script plots the empirical survivorship curve and considers all five mx models. 
After having found the best lambda for each mx model, lambda together with its lower and upper limit is printed
and the survivorship curve is plotted for each mx model.
