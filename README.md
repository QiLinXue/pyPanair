# PyPanair (UTAT)
## Instructions (Linux)
1. `sudo python3 setup.py install`
2. `cd utat`
3. `python3 filename.py` (this will create an `some_name.aux` file)
4. `./panin` (when prompted, type `some_name`)
5. `./panair` (when prompted, type `a502.in`)

An `ffmf` file will be created with aerodynamic data.

6. `python3 analyze.py`

It will create a `vtk` file which can then be opened up in Aerolab. After you are done, delete current files with the command. This step **must** be completed in order to run the next simulation.

7. `sh clean.sh`

## Shortcut (Linux)
Alternatively, I've also written up a bash script shorcut to automate the above steps.
1. `sudo python3 setup.py install`
2. `cd utat`
3. `sh run.sh`

Note that this will only run the main file.

## Current Files
* `mwe.py` A minimal working example of the Agard-B model presented in the original tutorial.
* `main.py` The final product of the NASA-TM-81787 rocket.
