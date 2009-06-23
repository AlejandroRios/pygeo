#!/usr/local/bin/python
'''
pyGeo

pyGeo performs the routine task of reading cross sectional information 
about a wind turbine blade or aircraft wing and producing the data 
necessary to create a surface with pySpline. 

Copyright (c) 2009 by G. Kenway
All rights reserved. Not to be used for commercial purposes.
Revision: 1.0   $Date: 26/05/2009$


Developers:
-----------
- Gaetan Kenway (GKK)

History
-------
	v. 1.0 - Initial Class Creation (GKK, 2009)
'''

__version__ = '$Revision: $'


# =============================================================================
# Standard Python modules
# =============================================================================
import os, sys, string, copy, pdb

# =============================================================================
# External Python modules
# =============================================================================
import numpy
from numpy import sin, cos, linspace, pi, zeros, where, hstack, mat, array, \
    transpose, vstack, max, dot, sqrt, append, mod

# =============================================================================
# Extension modules
# =============================================================================

sys.path.append(os.path.abspath('../pySpline/python'))
import pySpline2

# =============================================================================
# pyGeo class
# =============================================================================
class pyGeo():
	
    '''
    Geo object class
    '''

    def __init__(self,file_name,ref_axis=None,le_loc=None,chord=None,af_list=None,N=15):

        
        '''Create an instance of the geometry object. Input is through simple
        arrays. Most error checking is left to the user making an instance of
        this class. 
        
        Input: 
        
        ref_axis, array, size(naf,3): List of points in space defining the 
        the reference  axis for the geometry. Units are consistent with the
        remainder of the geometry. For wind turbine blades, this
        will be the pitch axis. For aircraft this will usually be the 1/4 
        chord. The twist is defined about this axis. 

        le_loc, array, size(naf) : Location of the LE point ahead of the 
        reference axis. Typically this will be 1/4. United scaled by chord

        chord, array, size(naf) : Chord lengths in consistent units
        
        twist, array, size(naf) : Twist of each section about the reference
        axis. Given in units of deg. 

        af_list, list, size(naf) : List of the filenames  to be read for each
        cross section.

        Output:

        x,y,z, array, size(naf,2N-1) : Coordinates of the surface for input to 
        pySpline.

        u, array, size(naf): parametric (spanwise) u coordinates for 
        input to pySpline 
        
        v, array, size(2*N-1): parametric (chordwise) v coordinates for 
        input to pySpline'''

        self.loadPlot3D(file_name)

#         # Save the data to the class
#         assert (ref_axis.N==len(le_loc) == len(chord)== len(af_list)),\
#             "All the input data must contain the same number of records"

#         naf = len(chord)
#         self.naf = naf
#         self.ref_axis = ref_axis
     
#         self.le_loc   = le_loc
#         self.chord    = chord
#         self.af_list  = af_list
#         self.N        = N
#         self.DVlist   = {}
      
#         # This is the standard cosine distribution in x (one sided)
#         s_interp = 0.5*(1-cos(linspace(0,pi,N)))
#         self.s = s_interp
        
#         X = zeros([2,N,naf,3])
#         for i in xrange(naf):

#             X_u,Y_u,X_l,Y_l = self.__load_af(af_list[i],N)

#             X[0,:,i,0] = (X_u-le_loc[i])*chord[i]
#             X[0,:,i,1] = Y_u*chord[i]
#             X[0,:,i,2] = 0
            
#             X[1,:,i,0] = (X_l-le_loc[i])*chord[i]
#             X[1,:,i,1] = Y_l*chord[i]
#             X[1,:,i,2] = 0
            
#             for j in xrange(N):
#                 for isurf in xrange(2):
#                     X[isurf,j,i,:] = self.__rotz(X[isurf,j,i,:],ref_axis.rot[i,2]*pi/180) # Twist Rotation
#                     X[isurf,j,i,:] = self.__rotx(X[isurf,j,i,:],ref_axis.rot[i,0]*pi/180) # Dihediral Rotation
#                     X[isurf,j,i,:] = self.__roty(X[isurf,j,i,:],ref_axis.rot[i,1]*pi/180) # Sweep Rotation
#             #end for
           
#             # Finally translate according to axis:
#             X[:,:,i,:] += ref_axis.x[i,:]
#         #end for
        
#         self.X = X
        return

    def createSurface(self,fit_type='interpolate',ku=4,kv=4):

        '''Create the splined surface based on the input geometry'''

        print 'creating surfaces:'
        u = zeros([2,self.N])
        v = zeros([2,self.naf])

        u[:] = self.s
        v[:] = self.ref_axis.sloc
               
        print 'creating surfaces...'
        self.surf = pySpline2.spline(2,u,v,self.X,fit_type=fit_type,ku=ku,kv=kv)
       
        return

    def __load_af(self,filename,N=35):
        ''' Load the airfoil file from precomp format'''

        # Interpolation Format
        s_interp = 0.5*(1-cos(linspace(0,pi,N)))

        f = open(filename,'r')

        aux = string.split(f.readline())
        npts = int(aux[0]) 
        
        xnodes = zeros(npts)
        ynodes = zeros(npts)

        f.readline()
        f.readline()
        f.readline()

        for i in xrange(npts):
            aux = string.split(f.readline())
            xnodes[i] = float(aux[0])
            ynodes[i] = float(aux[1])
        # end for
        f.close()

        # -------------
        # Upper Surfce
        # -------------

        # Find the trailing edge point
        index = where(xnodes == 1)
        te_index = index[0]
        n_upper = te_index+1   # number of nodes on upper surface
        n_lower = int(npts-te_index)+1 # nodes on lower surface

        # upper Surface Nodes
        x_u = xnodes[0:n_upper]
        y_u = ynodes[0:n_upper]

        # Now determine the upper surface 's' parameter

        s = zeros(n_upper)
        for j in xrange(n_upper-1):
            s[j+1] = s[j] + sqrt((x_u[j+1]-x_u[j])**2 + (y_u[j+1]-y_u[j])**2)
        # end for
        s = s/s[-1] #Normalize s

        # linearly interpolate to find the points at the positions we want
        X_u = numpy.interp(s_interp,s,x_u)
        Y_u = numpy.interp(s_interp,s,y_u)

        # -------------
        # Lower Surface
        # -------------
        x_l = xnodes[te_index:npts]
        y_l = ynodes[te_index:npts]
        x_l = hstack([x_l,0])
        y_l = hstack([y_l,0])

        # Now determine the lower surface 's' parameter

        s = zeros(n_lower)
        for j in xrange(n_lower-1):
            s[j+1] = s[j] + sqrt((x_l[j+1]-x_l[j])**2 + (y_l[j+1]-y_l[j])**2)
        # end for
        s = s/s[-1] #Normalize s

        # linearly interpolate to find the points at the positions we want
        X_l = numpy.interp(s_interp,s,x_l)
        Y_l = numpy.interp(s_interp,s,y_l)

        return X_u,Y_u,X_l,Y_l

    def __rotx(self,x,theta):
        ''' Rotate a set of airfoil coodinates in the local x frame'''
        M = [[1,0,0],[0,cos(theta),-sin(theta)],[0,sin(theta),cos(theta)]]
        return dot(M,x)

    def __roty(self,x,theta):
        '''Rotate a set of airfoil coordiantes in the local y frame'''
        M = [[cos(theta),0,sin(theta)],[0,1,0],[-sin(theta),0,cos(theta)]]
        return dot(M,x)

    def __rotz(self,x,theta):
        '''Roate a set of airfoil coordinates in the local z frame'''
        'rotatez:'
        M = [[cos(theta),-sin(theta),0],[sin(theta),cos(theta),0],[0,0,1]]
        return dot(M,x)

  
#     def getRotations(self,s):
#         '''Return a (linearly) interpolated list of the twist, xrot and
#         y-rotations at a span-wise position s'''
        
#         twist = numpy.interp([s],self.sloc,self.twist)
#         rot_x = numpy.interp([s],self.sloc,self.rot_x)
#         rot_y = numpy.interp([s],self.sloc,self.rot_y)

#         return twist[0],rot_x[0],rot_y[0]

#     def getLocalVector(self,s,x):
#         '''Return the vector x, rotated by the twist, rot_x, rot_y as 
#         linearly interpolated at span-wise position s. 
#         For example getLocalVecotr(0.5,[1,0,0]) will return the vector 
#         defining the local section direction at a span position of 0.5.'''

#         twist,rot_x,rot_y = self.getRotations(s)
#         x = self.__rotz(x,twist*pi/180) # Twist Rotation
#         x = self.__rotx(x,rot_x*pi/180) # Dihedral Rotation
#         x = self.__roty(x,rot_y*pi/180) # Sweep Rotation

#         return x

#     def getLocalChord(self,s):
#         '''Return the linearly interpolated chord at span-wise postiion s'''

#         return numpy.interp([s],self.sloc,self.chord)[0]
        
#     def getLocalLe_loc(self,s):
#         return numpy.interp([s],self.sloc,self.le_loc)[0]


#     def getRefPt(self,s):
#         '''Return the linearly interpolated reference location at a span-wise
#         position s. '''
        
#         x = zeros(3);
#         x[2] = s*self.L
#         x[0] = numpy.interp([s],self.sloc,self.ref_axis[:,0])[0]
#         x[1] = numpy.interp([s],self.sloc,self.ref_axis[:,1])[0]

#         return x


    def createAssociations(self):
        '''Create the associated links between control pt sections and the
        reference axis'''

        assert self.ref_axis_reference.shape[0] == self.surf.Nctlv,\
            'Must have the same number of control points in v (span-wise) as spanwise-stations'
        #self.ctl_deltas = 


    def addVar(self,dv_name,value,mapping,lower=0,upper=1):

        '''Add a single (scalar) variable to the dv list. '''

        if dv_name in self.DVlist.keys():
            print 'Error: dv_name is already in the list of keys. Please use a unique deisgn variable name'
            sys.exit(0)
        # end if
        
        self.DVlist[dv_name] = geoDV(dv_name,value,mapping,lower,upper)
        
        
        return
    
    def updateDV(self):
        '''Update the B-spline control points from the Design Varibales'''

        for key in self.DVlist.keys():
            self.DVlist[key].applyValue(self.surf,self.ref_axis.sloc)

        return

    def loadPlot3D(self,file_name):

        '''Load a plot3D file and create the splines to go with each patch'''
        print 'Loading plot3D file: %s ...'%(file_name)

        f = open(file_name,'r')

        # First load the number of patches
        nPatch = int(f.readline())
        
        print 'nPatch = %d'%(nPatch)

        patchSizes = zeros(nPatch*3,'intc')

        # We can do 24 sizes per line 
        nHeaderLines = 3*nPatch / 24 
        if 3*nPatch% 24 != 0: nHeaderLines += 1

        counter = 0

        for nline in xrange(nHeaderLines):
            aux = string.split(f.readline())
            for i in xrange(len(aux)):
                patchSizes[counter] = int(aux[i])
                counter += 1

        patchSizes = patchSizes.reshape([nPatch,3])
      
        # Total points
        nPts = 0
        for i in xrange(nPatch):
            nPts += patchSizes[i,0]*patchSizes[i,1]*patchSizes[i,2]

        print 'Number of Surface Points = %d'%(nPts)

        nDataLines = int(nPts*3/6)
        if nPts*3%6 !=0:  nDataLines += 1

        dataTemp = zeros([nPts*3])
        counter = 0
     
        for i in xrange(nDataLines):
            aux = string.split(f.readline())
            for j in xrange(len(aux)):
                dataTemp[counter] = float(aux[j])
                counter += 1
            # end for
        # end for
        
        f.close() # Done with the file

        # Post Processing
        patches = []
        counter = 0

        for ipatch in xrange(nPatch):
            patches.append(zeros([patchSizes[ipatch,0],patchSizes[ipatch,1],3]))
            for idim in xrange(3):
                for j in xrange(patchSizes[ipatch,1]):
                    for i in xrange(patchSizes[ipatch,0]):
                        patches[ipatch][i,j,idim] = dataTemp[counter]
                        counter += 1
                    # end for
                # end for
            # end for
        # end for

        # Create the list of u and v coordinates
        
        u = []
        for ipatch in xrange(nPatch):
            u.append(zeros([patchSizes[ipatch,0]]))
            singular_counter = 0
            for j in xrange(patchSizes[ipatch,1]): #loop over each v, and average the 'u' parameter 
                temp = zeros(patchSizes[ipatch,0])
                for i in xrange(patchSizes[ipatch,0]-1):
                    temp[i+1] = temp[i] + sqrt((patches[ipatch][i+1,j,0]-patches[ipatch][i,j,0])**2 +\
                                               (patches[ipatch][i+1,j,1]-patches[ipatch][i,j,1])**2 +\
                                               (patches[ipatch][i+1,j,2]-patches[ipatch][i,j,2])**2)
                # end for
                if temp[-1] == 0: # We have a singular point
                    singular_counter += 1
                    temp[:] = 0.0
                else:
                    temp /= temp[-1]
                # end if

                u[ipatch] += temp #accumulate the u-parameter calcs for each j
            # end for 
            u[ipatch]/=(patchSizes[ipatch,1]-singular_counter) #divide by the number of 'j's we had
        # end for 

        v = []
        for ipatch in xrange(nPatch):
            v.append(zeros([patchSizes[ipatch,1]]))
            singular_counter = 0
            for i in xrange(patchSizes[ipatch,0]): #loop over each v, and average the 'u' parameter 
                temp = zeros(patchSizes[ipatch,1])
                for j in xrange(patchSizes[ipatch,1]-1):
                    temp[j+1] = temp[j] + sqrt((patches[ipatch][i,j+1,0]-patches[ipatch][i,j,0])**2 +\
                                               (patches[ipatch][i,j+1,1]-patches[ipatch][i,j,1])**2 +\
                                               (patches[ipatch][i,j+1,2]-patches[ipatch][i,j,2])**2)
                # end for
                if temp[-1] == 0: #We have a singular point
                    singular_counter += 1
                    temp[:] = 0.0
                else:
                    temp /= temp[-1]
                #end if 

                v[ipatch] += temp #accumulate the u-parameter calcs for each j
            # end for 
            v[ipatch]/=(patchSizes[ipatch,0]-singular_counter) #divide by the number of 'j's we had
        # end for

        # Now create a list of spline objects:

        surfs = []

        for ipatch in xrange(nPatch):
            surfs.append(pySpline2.spline(u[ipatch],v[ipatch],patches[ipatch],task='lms',ku=4,kv=4))
        
        self.surfs = surfs
        self.nPatch = nPatch
        return


class geoDV(object):
     
    def __init__(self,dv_name,value,DVmapping,lower,upper):
        
        '''Create a geometic desing variable with specified mapping

        Input:
        
        dv_name: Design variable name. Should be unique. Can be used
        to set pyOpt variables directly

        DVmapping: One or more mappings which relate to this design
        variable

        lower: Lower bound for the variable. Again for setting in
        pyOpt

        upper: Upper bound for the variable. '''

        self.name = dv_name
        self.value = value
        self.lower = lower
        self.upper = upper
        self.DVmapping = DVmapping

        return

    def applyValue(self,surf,s):
        '''Set the actual variable. Surf is the spline surface.'''
        
        self.DVmapping.apply(surf,s,self.value)
        

        return


class ref_axis(object):

    def __init__(self,x,y,z,rot_z,rot_x,rot_y):

        ''' Create a generic reference axis. This object bascally defines a
        set of points in space (x,y,z) each with three rotations
        associated with it. The purpose of the ref_axis is to link
        groups of b-spline controls points together such that
        high-level planform-type variables can be used as design
        variables
        
        Input:

        x: list of x-coordinates of axis
        y: list of y-coordinates of axis
        z: list of z-coordinates of axis

        rot_z: list of z-axis rotations
        rot_y: list of y-axis rotations
        rot_x: list of z-axis rotations

        Note: Rotations are performed in the order: Z-Y-X
        '''

        assert len(x)==len(y)==len(z)==len(rot_z)==len(rot_y)==len(rot_x),\
            'The length of x,y,z,rot_z,rot_y,rot_x must all be the same'

        self.N = len(x)
        self.x = zeros([self.N,3])
        self.x[:,0] = x
        self.x[:,1] = y
        self.x[:,2] = z
        
        self.rot = zeros([self.N,3])
        self.rot[:,0] = rot_x
        self.rot[:,1] = rot_y
        self.rot[:,2] = rot_z

        self.x0 = copy.deepcopy(x)
        self.rot0 = copy.deepcopy(x)
        self.sloc = zeros(self.N)
        self.updateSloc()


    def updateSloc(self):
        
        for i in xrange(self.N-1):
            self.sloc[i+1] = self.sloc[i] +sqrt( (self.x[i+1,0]-self.x[i,0])**2 + \
                                                 (self.x[i+1,1]-self.x[i,1])**2 +
                                                 (self.x[i+1,2]-self.x[i,2])**2  )
        #Normalize
        self.sloc/=self.sloc[-1]

class DVmapping(object):

    def __init__(self,sec_start,sec_end,apply_to,formula):

        '''Create a generic mapping to apply to a set of b-spline control
        points.

        Input:
        
        sec_start: j index (spanwise) where mapping function starts
        sec_end : j index (spanwise) where mapping function
        ends. Python-based negative indexing is allowed. eg. -1 is the last element

        apply_to: literal reference to select what planform variable
        the mapping applies to. Valid litteral string are:
                'x'  -> X-coordinate of the reference axis
                'y'  -> Y-coordinate of the reference axis
                'z'  -> Z-coordinate of the reference axis
                'twist' -> rotation about the z-axis
                'x-rot' -> rotation about the x-axis
                'y-rot' -> rotation about the x-axis

        formula: is a string which contains a python expression for
        the mapping. The value of the mapping is assigned as
        'val'. Distance along the surface is specified as 's'. 

        For example, for a linear shearing sweep, the formula would be 's*val'
        '''
        self.sec_start = sec_start
        self.sec_end   = sec_end
        self.apply_to  = apply_to
        self.formula   = formula

        return

    def apply(self,surf,s,val):
        '''apply mapping to surface'''

        if self.apply_to == 'x':
#             print 'ceofs'
#             print surf.coef[0,0,self.sec_start:self.sec_end,0]
#             print surf.coef[0,0,:,0]
#             print 'formula'
#             print eval(self.formula)

            surf.coef[:,:,:,0] += eval(self.formula)

#            surf.coef[:,:,self.sec_start:self.sec_end,0]+= eval(self.formula)
#             print 'formula:',self.formula
#             print 's:',s
#             print 'val:',val
            print eval(self.formula).shape
            print 'done x'

#==============================================================================
# Class Test
#==============================================================================
if __name__ == '__main__':
	
    # Run a Simple Test Case
    print 'Testing pyGeo...'
    print 'No tests implemented yet...'



