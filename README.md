<img src='nearby_exoplanets.pdf'>

To get this figure, run:

```bash
$ python make_figure.py
```

There are also a variety of options:

```bash
$ python make_figure.py -h

usage: python make_figure.py [-h] [-t MAX_TEFF] [-d MAX_DIST] [-o OUTPUT] [-p MAX_PERIOD] [-m MAX_MASS] [-i MAX_INSOL]
                             [-s SIZE] [-a ALPHA] [--mirecle]

Creates a figure of nearby exoplanets.

options:
  -h, --help            show this help message and exit
  -t MAX_TEFF, --max_teff MAX_TEFF
                        Maximum effective temperature in K
  -d MAX_DIST, --max_dist MAX_DIST
                        Maximum distance in parsecs
  -o OUTPUT, --output OUTPUT
                        Output filename
  -p MAX_PERIOD, --max_period MAX_PERIOD
                        Maximum orbital period in days
  -m MAX_MASS, --max_mass MAX_MASS
                        Maximum planet mass in Earth masses
  -i MAX_INSOL, --max_insol MAX_INSOL
                        Maximum planet insolation in Earth fluxes
  -s SIZE, --size SIZE  Marker size scale factor
  -a ALPHA, --alpha ALPHA
                        Transparency
  --mirecle             Include MIRECLE target list

Created by: Ted Johnson (GSFC 693) in Oct 2022, uploaded to Github 2023-04-07
```
