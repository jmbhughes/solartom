# solartom: a solar tomography package

🚧🚧🚧 This package is under heavy development and will likely change dramatically. 🚧🚧🚧

🚧🚧🚧 New features are on the way. 🚧🚧🚧

## What is solartom ?

Tomography is the task of reconstructing a model based on observations. In this case, we use many 2D solar images to construct a 3D model of the solar environment.

This is a parallelized tomography projector and backprojector. It originates from solar tomography applications but could be used for other applications. It uses the [Siddon algorithm](https://aapm.onlinelibrary.wiley.com/doi/abs/10.1118/1.595715) as its core. The parallelization is done with Rust's Rayon library.

A similar package called [TomograPy](https://github.com/nbarbey/TomograPy) was originally authored by [Nicolas Barbey](https://github.com/nbarbey). This is the second generation of that package. It is now updated and maintained by [Marcus Hughes](https://github.com/jmbhughes).

![example](solar_example.png)

Above you can see an example input with its reconstruction from a solartom derived model cube. It's not perfect but shows the promise of this package.

## Status

This package still needs some features and much documentation to improve ease of use for solar physics settings. If you're interested in using it, please contact Marcus Hughes <marcus.hughes@swri.org> for more information on a timeline.

## Installation

Until the code is released on PyPI (coming soon!), you have to clone the repo and then install using pip. I always recommend creating a virtual environment for each project.

```bash
git@github.com:jmbhughes/solartom.git
python -m venv venv
source venv/bin/activate
pip install .
```

## Basic Use

Right now a simple toy example is available in `example.py`. More guidance is coming on how to use with STEREO and other data!

## Extended Documentation

Coming soon!

## Collaborations and questions

Please reach out to Marcus Hughes at <marcus.hughes@swri.org>. I'd love to have your input and use case in mind when developing this software.
