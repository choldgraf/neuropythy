# neuropythy #######################################################################################
A neuroscience library for Python, intended to complement the existing nibabel library.

## Author ##########################################################################################
Noah C. Benson &lt;<nben@nyu.edu>&gt;

## Installation ####################################################################################

The neuropythy library is available on [PyPI](https://pypi.python.org/pypi/neuropythy) and can be
installed via pip:

```bash
pip install neuropythy
```

The dependencies (below) should be installed auotmatically. Alternately, you can check out this
github repository and run setuptools:

```bash
# Clone the repository
git clone https://github.com/noahbenson/neuropythy
# Enter the repo directory
cd neuropythy
# Install the library
python setup.py install

```

## Dependencies ####################################################################################

The neuropythy library depends on a few other libraries, all freely available:
 * [numpy](http://numpy.scipy.org/) >= 1.2
 * [scipy](http://www.scipy.org/) >= 0.7.0
 * [nibabel](https://github.com/nipy/nibabel) >= 1.2
 * [pysistence](https://pythonhosted.org/pysistence/) >= 0.4.0
 * [py4j](https://www.py4j.org/) >= 0.9
 * [python-igraph](http://igraph.org/python/) >= 0.7.1

These libaries should be installed automatically for you if you use pip or setuptools (see above),
and they must be found on your PYTHONPATH in order to use neuropythy.


## Commands ########################################################################################

Currently Neuropythy is undergoing rapid development, but to get started, the neuropythy.commands
package contains functions that run command-interfaces for the various routine included.  Any of
these commands may be invoked by calling Neuropythy's main function and passing the name of the
command as the first argument followed by any additional command arguments. The argument --help may
be passed for further information about each command.

 * **surface_to_ribbon**. This command projects data on the cortical surface into a volume the same
   orientation as the subject's mri/orig.mgz file. The algorithm used tends to be much cleaner than
   that used by FreeSurfer's mri_surf2vol.
 * **benson14_retinotopy**. This command applies the anatomically-defined template of retinotopy
   described Benson *et al.* (2014; see *References* below) to a subject.
 * **register_retinotopy**. This command fits a retinotopic model of V1, V2, and V3 to retinotopy
   data for a subject and saves the predicted retinotopic maps that result. This command is
   currently experimental.

## Docker ##########################################################################################

There is a Docker containing Neuropythy that can be used to run the Neuropythy commands quite easily
without installing Neuropythy itself. If you have [Docker](https://www.docker.com/) installed, you
can use Neuropythy as follows:

```bash
# If your FreeSurfer subject's directory is /data/subjects and you want to
# apply the Benson2014 template to a subject bert:
docker run nben/neuropythy -ti --rm -v /data/subjects:/subjects \
           benson14_retinotopy bert
```


## References ######################################################################################

 * Benson NC, Butt OH, Brainard DH, Aguirre GK (**2014**) Correction of distortion in flattened
   representations of the cortical surface allows prediction of V1-V3 functional organization from
   anatomy. *PLoS Comput. Biol.* **10**(3):e1003538.
   doi:[10.1371/journal.pcbi.1003538](https://dx.doi.org/10.1371/journal.pcbi.1003538).
   PMC:[3967932](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3967932/).
 * Benson NC, Butt OH, Datta R, Radoeva PD, Brainard DH, Aguirre GK (**2012**) The retinotopic
   organization of striate cortex is well predicted by surface topology. *Curr. Biol.*
   **22**(21):2081-5. doi:[10.1016/j.cub.2012.09.014](https://dx.doi.org/10.1016/j.cub.2012.09.014).
   PMC:[3494819](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3494819/).


## License #########################################################################################

This README file is part of the Neuropythy library.

The Neuropythy library is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
