#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SpecfileData object mapped with a stack of EDF images

Description
===========

Utility object to connect a given scan in a SPEC file with a series
(stack) of EDF (ESRF data format) images, usually collected with a
two-dimensional detector (2D detector) during a scan
(e.g. monochromator energy scan).


STATUS
======

The current version is not generic nor stable. It should not be used
as it is, but only considered as an example. Here an elastic peak scan
from a crystal analyzer is evaluated. It permits to make/plot/save an
animation with Matplotlib.

Related
=======

- XRStools

"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = ""
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2015"

import os, sys
import numpy as np

### Matplotlib imports
import matplotlib.pyplot as plt
from matplotlib import cm, animation
from matplotlib import gridspec

### PyMca5 imports
from PyMca5.PyMca import EdfFile
from PyMca5.PyMca import MaskImageWidget

### local imports
from specfiledata import SpecfileData

class SpecWithEdfStack(SpecfileData):
    """scan data as a SPEC file plus a stack of EDF images"""

    def __init__(self, spec_fname, spec_scanno, anim_title=None,\
                 edf_root=None, edf_dir=None, edf_ext=None, **kws):
        """load SPEC and EDF data

        Parameters
        ==========

        spec_fname : string, SPEC file name with path

        spec_scanno : int, the scan number corresponding to the edf stack to load

        anim_title : string, title shown on the animation plot

        edf_root : string, the root name of the images, before the _####.edf
                   if None, {spec_fname}_{spec_scanno} is used by default
        
        edf_dir : string, directory path where EDF images are stored
                  if None, {spec_dirname}/edf is used as default

        edf_ext : string, images extension
                  if None, '.edf' is taken as default

        **kws : as in SpecfileData

        """
        super(SpecWithEdfStack, self).__init__(spec_fname, **kws)

        # init image plot window
        self.miw = MaskImageWidget.MaskImageWidget()

        # animation figure layout
        self.anim_fig = plt.figure(num='SpecWithEdfStack', figsize=(5,5), dpi=150)
        gs = gridspec.GridSpec(3, 2)
        self.anim_img = plt.subplot(gs[:-1, :])
        self.anim_int = plt.subplot(gs[2, :])
        if anim_title is not None:
            self.anim_img.set_title(anim_title)
        self.anim_img.set_xlabel('Sagittal direction (pixel)')
        self.anim_img.set_ylabel('Dispersive direction (pixel)')
        self.anim_int.set_xlabel('Energy (eV)')
        self.anim_int.set_ylabel('Integrated intesity')
        self.anim_int.ticklabel_format(axis='y', style='sci', scilimits=(-2,2))
        plt.ion()
        self.anim = None

        # load scan
        self.sd = self.sf.select(str(spec_scanno))
        self.mots = dict(zip(self.sf.allmotors(), self.sd.allmotorpos()))
        self.x = self.sd.datacol(self.sd.alllabels()[0])
        if self.cmon is not None:
            self.mon = self.sd.datacol(self.cmon)
        if self.csec is not None:
            self.sec = self.sd.datacol(self.csec)

        # load images stack
        if edf_root is None:
            edf_root = '{0}_{1}_'.format(self.fname.split(os.sep)[-1],
                                         spec_scanno)
        if edf_dir is None:
            edf_dir = os.path.join(os.path.dirname(self.fname), 'edf')
        if edf_ext is None:
            edf_ext = '.edf'
        self.imgs = []
        self.imgs_head = []
        self.imgs_int = []
        for idx, x in enumerate(self.x):
            _fname = '{0}{1}{2}{3:04d}{4}'.format(edf_dir, os.sep,
                                                  edf_root, idx, edf_ext)
            #print(_fname)
            edf = EdfFile.EdfFile(_fname, "rb")
            data = edf.GetData(0)
            header = edf.GetHeader(0)
            _int = np.trapz(np.trapz(data))
            self.imgs.append(data)
            self.imgs_head.append(header)
            self.imgs_int.append(_int)
        edf = None
        print('Loaded {0} images'.format(len(self.x)-1))

    def slice_stack(self, rowmin, rowmax, colmin, colmax):
        """crop the stack"""
        for idx, img in enumerate(self.imgs):
            shp = img.shape
            try:
                self.imgs[idx] = img[rowmin:rowmax, colmin:colmax]
                _int = np.trapz(np.trapz(self.imgs[idx]))
                self.imgs_int[idx] = _int
            except:
                print('Error slicing image {0}, shape is {1}'.format(idx, shp))
        
    def plot_image(self, idx, cmap_min=0, cmap_max=10):
        """show given image index"""
        self.miw.setImageData(self.imgs[idx])
        self.miw.colormap = [1, False, cmap_min, cmap_max,\
                           self.imgs[idx].min(), self.imgs[idx].max(), 0]
        self.miw.plotImage(update=True)
        self.miw.show()

    def make_animation(self, cmap_min=0, cmap_max=10, cmap=cm.Blues):
        """animation with matplotlib"""
        self.imgs_mpl = []
        norm = cm.colors.Normalize(vmin=cmap_min, vmax=cmap_max)
        for idx, (img, _x, _int) in enumerate(zip(self.imgs, self.x, self.imgs_int)):
            impl = self.anim_img.imshow(img, norm=norm, cmap=cmap, origin='lower')
            iint_ln, = self.anim_int.plot(self.x*1000, self.imgs_int,\
                                          linestyle='-', linewidth=1.5,\
                                          color='gray')
            iint_mk, = self.anim_int.plot(_x*1000, _int, linestyle='',\
                                          marker='o', markersize=5,\
                                          color='black')
            self.imgs_mpl.append([impl, iint_ln, iint_mk])

    def plot_animation(self):
        """plot the animation"""
        # blit=True updates only what is really changed
        #THIS WILL NOT WORK TO SAVE THE VIDEO!!!
        self.anim = animation.ArtistAnimation(self.anim_fig,\
                                              self.imgs_mpl,\
                                              interval=100,\
                                              blit=False,\
                                              repeat_delay=1000)
        #plt.subplots_adjust()
        plt.show()

    def save_animation(self, anim_save, writer=None, fps=30,\
                       extra_args=['-vcodec', 'libx264']):
        """save the animation to {anim_save}"""

        if writer is None:
            writer = animation.FFMpegWriter()
        print('saving animation... (NOTE: may take a while!)')
        self.anim.save(anim_save, writer=writer, fps=fps, extra_args=extra_args)

if __name__ == '__main__':
    pass