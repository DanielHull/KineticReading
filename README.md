# KineticReading
Integration of the Save Data Project, the Tech Dev Python Analytic Tools and the thrombophilia projects to automate analysis and file movement
  * GUI interface layer at KineticReading.py
  * CLI interface layer at kinetic_assay_cli.py
  * KineticAnalysis Class layer for analysis
  * Function Layer not necessary for Object Oriented Programming in KineticAssayTools

# Requirements
* Verbose error logging on GUI
* Automated GUI identification of labels, reducing the need to go into files themselves
* User can name labels whatever they want under fluor_cli.py/abs_cli.py layer
* User can name files whatever they want in whatever location they prefer
* User can analyze this at their desk and on their own computer easily
* Minimal IT help needed due to stable releases
* Tested at every layer in batch scripts and python files

## Versioning
Versions are tagged in git using the "Semantic Versioning 2.0" standard beginning with 0.1.0.
For details, please refer to: [http://semver.org/spec/v2.0.0.html](http://semver.org/spec/v2.0.0.html)

Version is manually updated using a text source file, but also provided automatically at build time by git itself, using it's `git describe` command.

## Summary
A version is of the form MAJOR.MINOR.PATCH, where each gets incremented for the following:

 * MAJOR, for incompatible API changes
 * MINOR, for functionality added in a backwards-compatible manner
 * PATCH, for backwards-compatible bug fixes

 The MAJOR patch will be zero for initial dev.

## Branching Model
Development is intended to follow the Git Flow branching model.

For details, please refer to: [http://nvie.com/posts/a-successful-git-branching-model/](http://nvie.com/posts/a-successful-git-branching-model/)

In summary, development takes place in feature branches (named anything except master, develop, release-\*, or hotfix-\*), then moved into release branches (release-\*), then tagged when released, and merged back into development and master branches.  For our purposes, build artifacts (elf, bin, hex, map files) are included in the release branches so that the build output is available once tagged.

## Install Anaconda 5.0.1 (64 bit), python 2.7.14
https://www.anaconda.com/download/
Anaconda>=5.0.1
python>=2.7.14
## Ensure relevant modules
relevant modules
matplotlib>=2.1.0
numpy>=1.13.3
scikit-learn>=0.19.1
statsmodels>=0.8.0
pyqt
