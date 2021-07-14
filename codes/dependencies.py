# this part imports dependencies from across the project so that only that can be used as an import header,
# native packages
import os
import datetime as dt
from itertools import combinations
# pip install numpy, pandas, matplotlib, scipy, statsmodels
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress, jarque_bera, probplot, kurtosis, skew, sem, norm
from scipy.optimize import LinearConstraint as slc
from scipy.optimize import minimize
from statsmodels.tsa.stattools import acf
from statsmodels.stats.diagnostic import het_white