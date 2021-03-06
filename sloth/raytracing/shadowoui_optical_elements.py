#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""shadow_oes: custom wrapper classes of *ShadowOpticalElement* from
ShadowOui_ (was Orange-Shadow_) from SHADOW3_ project

.. note:: ShadowOpticalElement is designed as a final class, this is
why the first class, *SwOE* is a wrapper class and does not inherit
from *ShadowOpticalElement*. It is not elegant, but this will keep the
compatibility with the whole (SHADOW3_ project).

.. note:: requires python3.x

.. _SHADOW3: http://forge.epn-campus.eu/projects/shadow3
.. _Orange-Shadow: https://github.com/lucarebuffi/Orange-Shadow
.. _ShadowOui: https://github.com/lucarebuffi/ShadowOui

"""
__author__ = "Mauro Rovezzi"
__credits__ = "Luca Rebuffi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2015"

import sys, os, copy, math
import numpy as np

# requirements for ShadowOpticalElement
HAS_PY3 = False
HAS_OSHADOW = False
if sys.version_info >= (3,2,0): HAS_PY3 = True
try:
    from orangecontrib.shadow.util.shadow_objects import ShadowOpticalElement
    HAS_OSHADOW = True
except:
    pass

class SwOE(object):
    """wrapper to ShadowOpticalElement"""

    def __init__(self):
        if not (HAS_PY3 and HAS_OSHADOW):
            raise ImportError("ShadowOui not found")
        self.sw = self.create_instance()

    def create_instance(self):
        """template method pattern"""
        #self.sw._oe.FMIRR=5
        #self.sw._oe.F_CRYSTAL = 0
        #self.sw._oe.F_REFRAC=2
        #self.sw._oe.F_SCREEN=0
        #self.sw._oe.N_SCREEN=0
        return ShadowOpticalElement.create_empty_oe()

    def get_instance(self):
        return self.sw

    def set_unit(self, length='cm'):
        """set length unit (['cm'], 'mm' or 'm')"""
        if length == 'cm':
            self.sw._oe.DUMMY = 1.0
        elif length == 'mm':
            self.sw._oe.DUMMY = 0.1
        elif length == 'm':
            self.sw._oe.DUMMY = 0.0

    def set_output_files(self, fwrite=1, f_angle=0):
        """optional file output

        Parameters
        ----------

        fwrite : int [1]
                 files to write out
                 0 -> all files
                 1 -> mirror file  only -- mirr [REQUIRED FOR FOOTPRINT]
                 2 -> image file only -- star
                 3 -> none
                 
        f_angle : int [0]
                  write out incident/reflected angles [angle.xx]
                  0 -> no
                  1 -> yes
        """
        self.sw._oe.FWRITE = fwrite
        self.sw._oe.F_ANGLE = f_angle 

    def set_parameters(self, f_ext=0):
        """set internal/calculated (0) parameters vs. external/user
        defined parameters (1)
        """
        self.sw._oe.F_EXT = f_ext
    
    def set_frame_of_reference(self, p, q, deg_inc, deg_refl=None,
                               deg_mirr=0.):
        """set frame of reference

        Parameters
        ----------
        p, q : float
               source, image plane distances [cm]

        deg_inc : float
                  angle of incidence wrt the normal [deg]

        deg_refl : float [None]
                   angle of reflection wrt the normal [deg]
                   if None = deg_inc
        
        deg_mirr : float [0]
                   mirror orientation [deg]
        
        """
        if deg_refl is None: deg_refl = deg_inc
        self.sw._oe.T_SOURCE     = p
        self.sw._oe.T_IMAGE      = q
        self.sw._oe.T_INCIDENCE  = deg_inc
        self.sw._oe.T_REFLECTION = deg_refl
        self.sw._oe.ALPHA        = deg_mirr
 
    def set_infinite(self):
        """set infinite dimensions (fhit_c = 0)"""
        self.sw._oe.FHIT_C = 0

    def set_dimensions(self, fshape=1, params=np.array([0., 0., 0., 0.])):
        """set finite mirror dimensions (fhit_c = 1)

        Parameters
        ----------

        fshape : int [1]
                 1 : rectangular
                 2 : full ellipse
                 3 : ellipse with hole

        params : array of floats, np.array([0., 0., 0., 0.])
                 params[0] : dimension y plus  [cm] 
                 params[1] : dimension y minus [cm] 
                 params[2] : dimension x plus  [cm] 
                 params[3] : dimension x minus [cm] 
                 
        """
        self.sw._oe.FHIT_C = 1
        self.sw._oe.FSHAPE = fshape
        self.sw._oe.RLEN1  = params[0]
        self.sw._oe.RLEN2  = params[1]
        self.sw._oe.RWIDX1 = params[2]
        self.sw._oe.RWIDX2 = params[3]

class PlaneCrystal(SwOE):
    """plane crystal"""
    
    def __init__(self):
        super(PlaneCrystal, self).__init__()
        self.sw = self.create_instance()
        self.set_reflectivity(f_reflec=0, f_refl=0)
        self.set_output_files(fwrite=0, f_angle=0) #write all, TODO: remove

    def create_instance(self):
        """template method pattern"""
        #self.sw._oe.FMIRR=5
        #self.sw._oe.F_CRYSTAL = 1
        #self.sw._oe.FILE_REFL = bytes("", 'utf-8')
        #self.sw._oe.F_REFLECT = 0
        #self.sw._oe.F_BRAGG_A = 0
        #self.sw._oe.A_BRAGG = 0.0
        return ShadowOpticalElement.create_plane_crystal()

    def set_reflectivity(self, f_reflec=0, f_refl=0):
        """set reflectivity of surface

        Parameters
        ----------

        f_reflec : int [0]

                   reflectivity of surface: no reflectivity dependence
                   (0), full polarization dependence (1), no
                   polarization dependence / scalar (2)

        f_refl : int [0]

                 for f_reflec=1,2 - source of optical constants: file
                 generated by PREREFL (0), keyboard (1), multilayers
                 (2).

        """
        self.sw._oe.F_REFLEC = f_reflec
        self.sw._oe.F_REFL = f_refl

    def set_crystal(self, file_refl, a_bragg=0.0, thickness=0.1,\
                    tune_auto=0, tune_units=0, tune_ev=0.0, tune_ang=0.0):
        """set crystal (f_crystal = 1)

        Parameters
        ----------
        
        file_refl : string
                    file containing the crystal parameters
                    for f_reflec=1,2 and f_refl=0: file with optical
                    constants
                    for f_reflec=1,2 and f_refl=2: file with
                    thicknesses and refractive indices for
                    multilayers

        a_bragg : float [0.0]
                  asymmetric angle between crystal planes and surface [deg]

        thickness : float [0.1]
                    crystal thickness (cm)
        
        tune_auto : int [0]
                    flag: auto tune angle of grating or crystal
                    -> yes (1), no (0)
        
        tune_units : int [0]
                     flag: tune to eV (0) or Angstroms (1)
        
        tune_ev : float [0.]
                  energy (eV) to autotune
        
        tune_ang : float [0.]
                   wavelength to autotune

        """
        self.sw._oe.F_CRYSTAL = 1
        self.sw._oe.FILE_REFL = bytes(file_refl, 'utf-8')


        if a_bragg != 0.0: self.set_asymmetric_cut(a_bragg, thickness)

        if tune_auto == 0:
            self.sw._oe.F_CENTRAL = 0
        else:
            self.set_auto_tuning(f_phot_cent=tune_units,
                                 phot_cent=tune_ev,
                                 r_lambda=tune_ang)

    def set_auto_tuning(self, f_phot_cent=0, phot_cent=0.0, r_lambda=0.0):
        """set auto tuning of grating or crystal [f_central = 1]
        
        Parameters
        ----------
        
        f_phot_cent : [0] flag, tune to eV (0) or Angstroms (1)

        phot_cent : [0.0] photon energy (eV) to autotune grating/crystal to.

        r_lambda : [0.0] Angstroms to autotune grating/crystal to.

        """
        self.sw._oe.F_CENTRAL = 1
        self.sw._oe.F_PHOT_CENT = f_phot_cent
        self.sw._oe.PHOT_CENT = phot_cent
        self.sw._oe.R_LAMBDA = r_lambda

    def set_mosaic(self, mosaic_seed=4732093, spread_mos=0.0, thickness=0.1):
        """set mosaic crystal (f_mosaic = 1)

        Parameters
        ----------
        
        mosaic_seed : int [4732094]
        
                      random number seed for mosaic crystal calculations
        
        spread_mos : float [0.0]
        
                     mosaic spread FWHM (degrees)

        thickness : float [0.1]

                    crystal thickness (cm)

        Notes
        -----
        mutually exclusive with asymmetric cut and Johansson
        """
        self.sw._oe.F_MOSAIC = 1
        self.sw._oe.MOSAIC_SEED = mosaic_seed
        self.sw._oe.SPREAD_MOS = spread_mos
        self.sw._oe.THICKNESS = thickness

        #MUTUALLY EXCLUSIVE!
        self.sw._oe.F_BRAGG_A = 0
        self.sw._oe.F_JOHANSSON = 0

    def set_asymmetric_cut(self, a_bragg, thickness, order=-1.):
        """set asymmetric cut (f_bragg_a = 1)

        Parameters
        ----------
        a_bragg : float
                  asymmetric angle between crystal planes and surface [deg]
        
        thickness : float
                    thickness [cm]
        
        order : float [-1]
                diffraction order, negative inside (European convention)
                below (-1.) / onto (1.) Bragg planes


        Notes
        -----
        mutually exclusive with mosaic
        
        """
        self.sw._oe.F_BRAGG_A = 1
        self.sw._oe.F_MOSAIC = 0

        self.sw._oe.A_BRAGG = a_bragg
        self.sw._oe.THICKNESS = thickness
        self.sw._oe.ORDER = order
        
    def set_johansson(self, r_johansson):
        """set Johansson geometry (f_johansson = 1)

        Parameters
        ----------

        r_johansson : float
                      Johansson radius (cm)

        Notes
        -----
        mutually exclusive with mosaic
        """
        self.sw._oe.F_JOHANSSON = 1
        self.sw._oe.F_EXT = 1
        self.sw._oe.R_JOHANSSON = r_johansson
        
        #MUTUALLY EXCLUSIVE!
        self.sw._oe.F_MOSAIC = 0

class SphericalCrystal(PlaneCrystal):
    """spherical (Johann) crystal"""
    
    def __init__(self, convex=False, cyl_ang=None, rmirr=None, **kws):
        """if no keyword arguments given: init a spherical concave crystal

        Parameters
        ----------

        convex : boolean, False
                 is convex?
        cyl_ang : float, None
                  cylinder orientation [deg] CCW from X axis]
                  0 -> meridional
                  90. -> sagittal
        rmirr : float, None
                meridional radius

        """
        super(SphericalCrystal, self).__init__()
        self.sw = self.create_instance()
        self.set_output_files(fwrite=0, f_angle=0) #write all, TODO: remove

        # convex/concave
        if convex:
            f_convex = 1
        else:
            f_convex = 0
        self.set_curvature(f_convex)
        
        # cylindrical
        if cyl_ang is not None:
            self.set_cylindrical(cyl_ang)
            
        # radius of curvature (internal or external)
        if rmirr is None:
            self.set_calculated_shape_params(self, **kws)
        else:
            self.set_radius(rmirr)

    def create_instance(self):
        #self.sw._oe.FMIRR=1
        #self.sw._oe.F_CRYSTAL = 1
        #self.sw._oe.FILE_REFL = bytes("", 'utf-8')
        #self.sw._oe.F_REFLECT = 0
        #self.sw._oe.F_BRAGG_A = 0
        #self.sw._oe.A_BRAGG = 0.0
        #self.sw._oe.F_REFRAC = 0
        return ShadowOpticalElement.create_spherical_crystal()

    def set_radius(self, rmirr):
        """set radius of curvature (rmirr)

        Parameters
        ----------

        rmirr : float
                radius of curvature (cm)

        """
        self.sw._oe.F_EXT = 1
        self.sw._oe.RMIRR = rmirr

    def set_curvature(self, f_convex=0):
        """set curvature (concave is default)"""
        self.sw._oe.F_CONVEX = f_convex

    def set_cylindrical(self, cyl_ang):
        """set cylindrical (fcyl = 1)
        
        cyl_ang : float
                  cylinder orientation [deg] CCW from X axis
                  0 -> meridional curvature
                  90. -> sagittal curvature
        """
        self.sw._oe.FCYL = 1
        self.sw._oe.CIL_ANG = cyl_ang

    def set_auto_focus(self, f_default=0, ssour=0.0, simag=0.0, theta=0.0):
        """set auto focus

        Parameters
        ----------

        f_default : int, 0
                    focii coincident with continuation plane - yes
                    (1), no (0)

         ssour : float, 0.0
                 for f_default=0: distance from object focus to the
                 mirror pole
        
         simag : float, 0.0
                 for f_default=0: distance from mirror pole to image
                 focus
        
        theta : float, 0.0
                for f_default=0: incidence angle (degrees)

        """
        self.set_parameters(f_ext=0)
        if f_default == 0:
            self.sw._oe.SSOUR = ssour
            self.sw._oe.SIMAG = simag
            self.sw._oe.THETA = theta

    def set_calculated_shape_params(self, coincident=True, p_cm=0.,
                                    q_cm=0., inc_deg=0.):
        """internally calculated shape parameters"""
        if self.sw._oe.FCYL and self.sw._oe.CYL_ANG == 90.0:
            # sagittal curvature
            self.sw._oe.F_EXT=1

            # RADIUS = (2 F1 F2 sin (theta)) / (F1+F2)
            if coincident:
                p_cm = self.sw._oe.T_SOURCE
                q_cm = self.sw._oe.T_IMAGE
                inc_deg =  self.sw._oe.T_REFLECTION

            self.sw._oe.RMIRR = ( (2 * p_cm * q_cm) / (p_cm + q_cm) ) * math.sin(math.radians(90-inc_deg))
        else:
            self.sw._oe.F_EXT=0
            if coincident:
                self.set_auto_focus(f_default=1)
            else:
                self.set_auto_focus(f_default=0, ssour=p_cm,
                                    simag=q_cm, theta=inc_deg)


if __name__ == '__main__':
    #temp tests
    #t = SwOE() #OK
    #t = PlaneCrystal() #OK
    t = SphericalCrystal() #OK
    pass
