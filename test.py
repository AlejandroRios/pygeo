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

#Lets start setting things we know we will need
naf = 10
bl_length = 21.15

# Wind Turbine Blade Example

tw_aero = array([0.0,20.3900,16.0200,11.6500,\
                6.9600,1.9800,-1.8800,-3.4100,-3.4500,-3.4700])
#tw_aero = zeros(naf)
chord = array([.6440,1.0950,1.6800,\
         1.5390,1.2540,0.9900,0.7900,0.4550,0.4540,0.4530])
#chord = ones(naf)
sloc = array([0.0000,0.1141,\
        0.2184,0.3226,0.4268,0.5310,0.6352,0.8437,0.9479,1.0000])
le_loc = array([0.5000,0.3300,\
          0.2500,0.2500,0.2500,0.2500,0.2500,0.2500,0.2500,0.2500])
#le_loc = 0.25*ones(naf)
airfoil_list = ['af1-6.inp','af-07.inp','af8-9.inp','af8-9.inp','af-10.inp',\
                    'af-11.inp','af-12.inp', 'af-14.inp',\
                    'af15-16.inp','af15-16.inp']
# airfoil_list = ['af15-16.inp','af15-16.inp','af15-16.inp','af15-16.inp',
#                  'af15-16.inp','af15-16.inp','af15-16.inp','af15-16.inp',
#                  'af15-16.inp','af15-16.inp']

#airfoil_list = ['af-11.inp','af-11.inp','af-11.inp','af-11.inp',
#                 'af-11.inp','af-11.inp','af-11.inp','af-11.inp',
#                 'af-11.inp','af-11.inp','af-11.inp']

ref_axis = zeros((naf,3))
ref_axis[:,2] = sloc*bl_length
ref_axis[:,1] = 0
ref_axis[:,0] = 0

#rot_x = -arctan(3*sloc/bl_length)*180/pi
#rot_y = arctan(2*sloc/bl_length)*180/pi
rot_x = zeros(naf)
rot_y = zeros(naf)

geobj = pyGeo.pyGeo(bl_length,ref_axis,le_loc,chord,tw_aero,rot_x,rot_y,airfoil_list,N=13)

geobj.createSurface()
geobj.joinSurfaces()

geobj.writeSurfaceTecplot(50,150,'output.dat')


