#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""shadow_screens: custom wrapper classes of *ShadowOpticalElement*
from ShadowOui_ (was Orange-Shadow_) from SHADOW3_ project

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
if sys.version_info >= (3,2,0): HAS_PY3 = True
HAS_OSHADOW = False
try:
    from orangecontrib.shadow.util.shadow_objects import ShadowOpticalElement
    HAS_OSHADOW = True
except:
    pass

from shadow_oes import SwOE

class SwScreen(SwOE):
    """screen"""

    def __init__(self, slit_width_xaxis, slit_height_zaxis):
        """create a screen (=empty optical element) with a given slit size XZ

        Parameters
        ----------

        slit_width_xaxis : float
                           slith aperture X axis [cm]

        slit_height_zaxis : float
                            slit aperture Z axis [cm]

        """
        super(SwScreen, self).__init__()
        self.sw = self.create_instance()

        self.set_output_files(fwrite=0, f_angle=0) #write all, TODO: remove

        n_screen = 1
        i_screen = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        i_abs = np.zeros(10)
        i_slit = np.zeros(10)
        i_stop = np.zeros(10)
        k_slit = np.zeros(10)
        thick = np.zeros(10)
        file_abs = np.array(['', '', '', '', '', '', '', '', '', ''])
        rx_slit = np.zeros(10)
        rz_slit = np.zeros(10)
        sl_dis = np.zeros(10)
        file_src_ext = np.array(['', '', '', '', '', '', '', '', '', ''])
        cx_slit = np.zeros(10)
        cz_slit = np.zeros(10)

        i_abs[0] = 0 # NO ABSORPTION
        i_slit[0] = 0 # APERTURING
        i_stop[0] = 0 # SLIT
        k_slit[0] = 0 # RECTANGULAR

        rx_slit[0] = slit_width_xaxis
        rz_slit[0] = slit_height_zaxis
        cx_slit[0] = 0.0
        cz_slit[0] = 0.0

        self.sw._oe.set_screens(n_screen,
                                i_screen,
                                i_abs,
                                sl_dis,
                                i_slit,
                                i_stop,
                                k_slit,
                                thick,
                                file_abs,
                                rx_slit,
                                rz_slit,
                                cx_slit,
                                cz_slit,
                                file_src_ext)

    def create_instance(self):
        """template method pattern"""
        #self.sw._oe.FMIRR=5
        #self.sw._oe.F_CRYSTAL = 0
        #self.sw._oe.F_REFRAC=2
        #self.sw._oe.F_SCREEN=1
        #self.sw._oe.N_SCREEN=1
        return ShadowOpticalElement.create_screen_slit()


    def get_instance(self):
        return self.sw

    def set_frame_of_reference(self, p, q):
        """set screen frame of reference

        Parameters
        ----------
        p, q : float
               source, image plane distances [cm]

        """
        self.sw.set_frame_of_reference(p, q, 0.0, 180.0, 0.0)
        
if __name__ == '__main__':
    #t = SwScreen(10., 10.) #OK
    pass
