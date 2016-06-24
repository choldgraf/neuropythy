####################################################################################################
# neuropythy/registration/models.py
# Importing and interpreting of flat mesh models for registration.
# By Noah C. Benson

import numpy                as     np
import scipy                as     sp
import scipy.spatial        as     space
import numpy.linalg
import os
import math
from   pysistence           import make_dict

import neuropythy.geometry  as     geo
from   neuropythy.immutable import Immutable
from   neuropythy.java      import (java_link, serialize_numpy,
                                    to_java_doubles, to_java_ints, to_java_array)

class RetinotopyModel:
    '''
    RetinotopyModel is a class designed to be inherited by other models of retinotopy; any class
    that inherits from RetinotopyModel must implement the following methods to work properly with
    the registration system of the neuropythy library.
    '''
    def angle_to_cortex(self, theta, rho):
        '''
        model.angle_to_cortex(theta, rho) yields a (k x 2) matrix in which each row corresponds to
        an area map (e.g. V2 or MT) and the two columns represent x and y coordinates of the
        predicted location in a flattened cortical map at which one would find the visual angle
        values of theta (polar angle) and rho (eccentricity). Theta should be in units of degrees
        between 0 (upper vertical meridian) and 180 (lower vertical meridian).
        If theta and rhos are both vectors of length n, then the result is an (n x k x 2) matrix
        with one entry for each theta/rho pair.
        '''
        raise NotImplementedError(
            'Object with base class RetinotopyModel did not override angle_to_cortex')
    def cortex_to_angle(self, x, y):
        '''
        model.cortex_to_angle(x, y) yields a vector of (polar-angle, eccentricity, id) corresponding
        to the given (x,y) coordinates from a cortical map. The id that is returned is a positive
        integer corresponding to an ROI label (e.g., V1, MT).
        If x and y are vectors of length n then the return value is an (n x 3) matrix in which each
        row corresponds to one (x,y) pair.
        '''
        raise NotImplementedError(
            'Object with base class RetinotopyModel did not override cortex_to_angle')

# How we construct a Schira Model:
class SchiraModel(RetinotopyModel):
    '''
    The SchiraModel class is a class that inherits from RetinotopyModel and acts as a Python wrapper
    around the Java nben.neuroscience.SchiraModel class; it handles conversion from visual field angle
    to cortical surface coordinates and vice versa for the Banded Double-Sech model proposed in the
    following paper:
    Schira MM, Tyler CW, Spehar B, Breakspear M (2010) Modeling Magnification and Anisotropy in the
    Primate Foveal Confluence. PLOS Comput Biol 6(1):e1000651. doi:10.1371/journal.pcbi.1000651.
    '''

    # These are the accepted arguments to the model:
    default_parameters = {
        'A': 0.5,
        'B': 135.0,
        'lambda': 1.0,
        'psi': 0.15,
        'scale': [7.0, 8.0],
        'shear': [[1.0, -0.2], [0.0, 1.0]],
        'center': [-7.0, -2.0],
        'v1size': 1.2,
        'v2size': 0.6,
        'v3size': 0.4,
        'hv4size': 0.9,
        'v3asize': 0.9}
    # This function checks the given arguments to see if they are okay:
    def __check_parameters(self, parameters):
        # we don't care if there are extra parameters; we just make sure the given parameters make
        # sense, then return the full set of parameters
        opts = {
            k: parameters[k] if k in parameters else v
            for (k,v) in SchiraModel.default_parameters.iteritems()}
        return opts

    # This class is immutable: don't change the params to change the model; 
    # don't change the java object!
    def __setattr__(self, name, val):
        raise ValueError('The SchiraModel class is immutable; its objects cannot be edited')

    def __init__(self, **opts):
        # start by getting the proper parameters
        params = self.__check_parameters(opts)
        # Now, do the translations that we need...
        if isinstance(params['scale'], Number):
            params['scale'] = [params['scale'], params['scale']]
        if isinstance(params['shear'], Number) and params['shear'] == 0:
            params['shear'] = [[1, 0], [0, 1]]
        elif params['shear'][0][0] != 1 or params['shear'][1][1] != 1:
            raise RuntimeError('shear matrix [0,0] elements and [1,1] elements must be 1!')
        if isinstance(params['center'], Number) and params['center'] == 0:
            params['center'] = [0.0, 0.0]
        self.__dict__['parameters'] = make_dict(params)
        # Okay, let's construct the object...
        self.__dict__['_java_object'] = java_link().jvm.nben.neuroscience.SchiraModel(
            params['A'],
            params['B'],
            params['lambda'],
            params['psi'],
            params['v1size'],
            params['v2size'],
            params['v3size'],
            params['hv4size'],
            params['v3asize'],
            params['center'][0],
            params['center'][1],
            params['scale'][0],
            params['scale'][1],
            params['shear'][0][1],
            params['shear'][1][0])
    
    def angle_to_cortex(self, theta, rho):
        iterTheta = hasattr(theta, '__iter__')
        iterRho = hasattr(rho, '__iter__')
        if iterTheta and iterRho:
            if len(theta) != len(rho):
                raise RuntimeError('Arguments theta and rho must be the same length!')
            return self._java_object.angleToCortex(to_java_doubles(theta), to_java_doubles(rho))
        elif iterTheta:
            return self._java_object.angleToCortex(to_java_doubles(theta),
                                                   to_java_doubles([rho for t in theta]))
        elif iterRho:
            return self._java_object.angleToCortex(to_java_doubles([theta for r in rho]),
                                                   to_java_doubles(rho))
        else:
            return self._java_object.angleToCortex(theta, rho)
    def cortex_to_angle(self, x, y):
        iterX = hasattr(x, '__iter__')
        iterY = hasattr(y, '__iter__')
        if iterX and iterY:
            if len(x) != len(y):
                raise RuntimeError('Arguments x and y must be the same length!')
            return self._java_object.cortexToAngle(to_java_doubles(x), to_java_doubles(y))
        elif iterX:
            return self._java_object.cortexToAngle(to_java_doubles(x),
                                                   to_java_doubles([y for i in x]))
        elif iterY:
            return self._java_object.cortexToAngle(to_java_doubles([x for i in y]),
                                                   to_java_doubles(y))
        else:
            return self._java_object.cortexToAngle(x, y)

class RetinotopyMeshModel(RetinotopyModel):
    '''
    RetinotopyMeshModel is a class that represents a retinotopic map or set of retinotopic maps on
    the flattened 2D cortex.
    RetinotopyMeshModel(tris, coords, polar_angle, eccen, areas) yields a retinotopy mesh model
    object in which the given triangle and coordinate matrices form the mesh and the polar_angle,
    eccen, and areas give the appropriate data for each vertex in coords. Note that the areas
    parameter should be 0 on any boundary vertex and an integer labelling the roi for any other
    vertex.
    '''

    def __init__(self, triangles, coordinates, angles, eccens, area_ids, transform=None):
        triangles   = np.asarray(triangles)
        coordinates = np.asarray(coordinates)
        triangles   = triangles   if triangles.shape[1] == 3   else triangles.T
        coordinates = coordinates if coordinates.shape[1] == 2 else coordinates.T
        angles      = np.asarray(angles)
        eccens      = np.asarray(eccens)
        area_ids    = np.asarray(map(int, area_ids))
        # The forward model is the projection from cortical map -> visual angle
        self.forward = geo.Mesh(triangles, coordinates)
        # The inverse model is a set of meshes from visual field space to the cortical map
        xs = coordinates[:,0]
        ys = coordinates[:,1]
        zs = eccens * np.exp(1j * (90 - angles)/180*math.pi)
        coords = np.asarray([zs.real, zs.imag]).T
        self.inverse = {
            area: geo.Mesh(np.asarray(tris), coords)
            # Iterate over all the unique areas;
            for area in list(set(area_ids) - set([0]))
            # bind the triangles (0 area_ids indicate borders):
            for tris in [[t for t in triangles if (set(area_ids[t]) - set([0])) == set([area])]]}
        # Note the transform:
        self.transform = np.asarray(transform) if transform is not None else None
        self.itransform = numpy.linalg.inv(transform) if transform is not None else None
        # Save the data:
        self.data = {}
        self.data['x'] = xs
        self.data['y'] = ys
        self.data['polar_angle'] = angles
        self.data['eccentricity'] = eccens
        # we have to fix the area_ids to be the mean of their neighbors when on a boundary:
        boundaryNeis = {}
        for (b,inside) in [(b, set(inside))
                           for t in triangles
                           for (bound, inside) in [([i for i in t if area_ids[i] == 0],
                                                    [i for i in t if area_ids[i] != 0])]
                           if len(bound) > 0 and len(inside) > 0
                           for b in bound]:
            if b not in boundaryNeis: boundaryNeis[b] = inside
            else: boundaryNeis[b] |= inside
        for (b,neis) in boundaryNeis.iteritems():
            area_ids[b] = np.mean(area_ids[list(neis)])
        self.data['id'] = area_ids

    def cortex_to_angle(self, x, y):
        'See RetinotopyModel.cortex_to_angle.'
        if not hasattr(x, '__iter__'):
            return self.cortex_to_angle([x], [y])[0]
        # start by applying the transform to the points
        tx = self.itransform
        xy = np.asarray([x,y]).T if tx is None else np.dot(tx, [x,y,[1 for i in x]])[0:2].T
        # we only need to interpolate from the inverse mesh in this case
        interp = [self.forward.interpolate(xy, self.data[name], smoothing=1)
                  for name in ['polar_angle', 'eccentricity', 'id']]
        return np.asarray(
            [(ang, ecc, area) if area is not None else (0, 0, 0)
             for (ang, ecc, area) in zip(*interp)])

    def angle_to_cortex(self, theta, rho):
        'See RetinotopyModel.angle_to_cortex.'
        if not hasattr(theta, '__iter__'):
            return self.angle_to_cortex([theta], [rho])[:,0]
        theta = np.asarray(theta)
        rho = np.asarray(rho)
        zs = rho * np.exp(1j * (90 - theta)/180*math.pi)
        coords = np.asarray([zs.real, zs.imag]).T
        # we step through each area in the forward model and return the appropriate values
        tx = self.transform
        xvals = self.data['x']
        yvals = self.data['y']
        res = np.asarray(
            [[self.inverse[area].interpolate(coords, xvals, smoothing=1),
              self.inverse[area].interpolate(coords, yvals, smoothing=1)]
             for area in map(int, sorted(list(set(self.data['id']))))
             if area != 0]
        ).transpose((0,2,1))
        if tx is not None:
            res = np.asarray(
                [[np.dot(tx, [xy[0], xy[1], 1])[0:2] if xy[0] is not None else [None, None]
                  for xy in adat]
                 for adat in res])
        # there's a chance that the coords are outside the triangle mesh; we want to make sure
        # that these get handled correctly...
        for (i,adat) in enumerate(res):
            for (k,row) in enumerate(adat):
                if None in set(row.flatten()) and rho[k] > 86 and rho[k] <= 90:
                    # we try to get a fixed version by reducing rho slightly
                    res[i] = angle_to_cortex(theta[k], rho[k] - 0.5);
        return res

             
        
