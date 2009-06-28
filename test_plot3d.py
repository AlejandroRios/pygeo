# =============================================================================
# Standard Python modules
# =============================================================================
import os, sys, string, pdb, copy, time

# =============================================================================
# External Python modules
# =============================================================================
from numpy import linspace, cos, pi, hstack, zeros, ones, sqrt, imag, interp, \
    array, real, reshape, meshgrid, dot, cross

# =============================================================================
# Extension modules
# =============================================================================

#pyOPT
sys.path.append(os.path.abspath('../../../../pyACDT/pyACDT/Optimization/pyOpt/'))

# pySpline
sys.path.append('../pySpline/python')

#pyOPT
sys.path.append(os.path.abspath('../../pyACDT/pyACDT/Optimization/pyOpt/'))

#pySNOPT
sys.path.append(os.path.abspath('../../pyACDT/pyACDT/Optimization/pyOpt/pySNOPT'))

#pyGeo
import pyGeo

#aircraft = pyGeo.pyGeo('plot3d',file_name='full_aircraft.xyz')
#aircraft = pyGeo.pyGeo('iges',file_name='plot3d_example.igs')
aircraft  = pyGeo.pyGeo('iges',file_name='sailplane_split.igs')
#aircraft.surfs[0].coef[0,0,1] +=  ~2
aircraft.writeTecplot('sailplane_split.dat')

#aircraft.writeIges('plot3d_example.igs')

