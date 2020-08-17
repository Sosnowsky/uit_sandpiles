# Investigating power laws in sandpile models

## Models

The two models that currently are implemented are the BTW sandpile model (also known as the Abelian sandpile model) and the Zhang sandpile model. Both take place on a plane of individual cells.

### BTW model

Each cell has an integer value representing the number of grains at that cell. If the number of grains at a cell is greater than or equal to 4, 4 grains are removed from this cell and equally distributed between its four neighboring cells (both in the next timestep). This process is referred to as toppling of a critical site.

At the beginning of a timestep, new grains are added to the plane. By default these new grains are uniformly randomly distributed amongst all cells, but this can be modified. The number of grains added is another modifiable parameter; It can among other things be a constant (1 is often used), or a number drawn from a distribution.

If the simulation is configured as `running`, this introduction of new grains happens at every $\Delta t$ timesteps - otherwise it only happens when there were no critical cells in the previous timestep.

More info available on [Wikipedia](https://en.wikipedia.org/wiki/Abelian_sandpile_model).

<p>
  <figure style='display: inline-block; text-align: center'>
  <img src='https://github.com/AFNordal/uit_sandpiles/raw/master/documentation/btw.gif' alt='btw-gif'>
  <figcaption> The BTW model (not "running") </figcaption>
  </figure>
  <figure style='display: inline-block; text-align: center'>
  <img src='https://github.com/AFNordal/uit_sandpiles/raw/master/documentation/btw_running.gif' alt='btw-running-gif'>
  <figcaption> The "running" BTW model </figcaption>
  </figure>
</p>

### The Zhang model

Here, the number of grains is no longer discrete - each cell has a continuous value. If this grain value is greater than or equal to some threshold, this value is multiplied by some constant $\epsilon$. The ammount it is reduced by is equally distributed among the four neighboring cells.

The introduction of new grains is similar to in the BTW model with the only exception that the number of grains added to cells is uniformely ditributed between 0 and the toppling threshold.

The details around this model are unclear; [This](https://www.researchgate.net/publication/226038042_A_Probabilistic_Approach_to_Zhang's_Sandpile_Model) paper describes it a little differently than [Martin Rypdal's PhD thesis](https://hdl.handle.net/10037/1851), which provided the description for this implementation.

## Directory structure

The data generated and analysed in this project is exchanged between scripts in the shape of text files. This is rather impractical, so implementing some database (maybe hdf5?) would be a significant improvement.

Nevertheless, as is, raw data from the simulation is temporarily stored in `.txt` files. These are periodically backed up as `.d` and `.m` files, containing simulation time series and a serialized map of the simultion plane respectively.

In initial anlysis, the following files are generated for each `*.d` file:

* `*.e` - a file containing a list durations and areas/magnitudes of each topple event, categorized in thresholds.
  * Format: `[threshold index];[duration];[area]`
* `*.q` - a file containing a list of quiet-times between each topple event, categorized in thresholds.
  * Format: `[threshold index];[quiet-time]`
* `*.f` - a file containing a spectral density estimation, calculated by whelch's method.
  * Format: `[frequency];[spectral density]`
* `*.t` - a file containing the thresholds used in the analysis of `*.d`.
  * Format: `[threshold 0];...;[threshold n]`

In the [next analysis step](#blups), five new files are generated; `a_pdf.c`, `dur_pdf.c`, `dur_a.c`, `q_pdf.c` and `freq.c`.

* All these files contain exponents for correlations in the data. All but `freq.c` are categorized in thresholds.
  * Format of all except `freq.c` (f stands for 'file' and t for 'thresholds'. There are n files and m thresholds):

  ```text
  [f 0, t 0];...;[f n, t 0]
  ...
  [f 0, t m];...;[f n, t m]
  ```

  * `freq.c` has each file's coefficient on a new line

## API / technical documentation

I don't have a lot of experience with projects of this magnitude, and this may have turned out a liiiittle messy. I hope this documentation can help compensate for this.

### Data generation

All data is generation is centered through the [`world`](#world) module. This can be driven through [`sandpiles.py`](#sandpiles), [`testrun.py`](#testrun) and [`prof.py`](#prof). All of these take config options from [`config.yml`](#config).

#### `world.pyx` (Module) <a id="world"></a>

**This file is written for cython, and needs to be [built/compiled](#setup) to be run!**

This module provides one class, `World`, which is interacted with through the following methods:

* `__init__(self,`**`dict`**`config)`
  
  Initiates the object.

  * `config`: A dictionary with the parameters outlined in the section on `config.yml`. Not that all parameters must be present, even if not used.

* `drive(self,`**`int`**`n,`**`int`**`verbose=2,`**`bool`**`animate=False,`**`bool`**`graph=False,`**`bool`**`nest_tqdm=False)`

  Drives the simulation, saves simulation data, optionally plots data and/or animates the simulation plane in real time, and saves a serialization of the plane after driving.

  * `n`: Number of timesteps to simulate

  * `verbose`: Verbosity level.
    * 0: Quiet
    * 1: Prints what timestep is currently being simulated.
    * 2: Prints a [tqdm](https://github.com/tqdm/tqdm) progress bar
  
  * `animate`: Whether the simulation plane should be animated. This slows the simulation down and is therefore `False` by default.

  * `graph`: Whether the simulation data should be plotted in real time. This slows the simulation down and is therefore `False` by default.

  * `nest_tqdm`: Whether the progress bar is part of nested [tqdm](https://github.com/tqdm/tqdm) progress bars Only relevant for verbosity level 2.

* `drive_to_stable(self)`

  Drives the simulation for a minimum of 20000 timesteps **without** saving data. The method returns when the total number of grains at each timestep flattens out and more than 20000 steps are simulated. Saves a serialization of the plane before returning.

#### `config.yml` (Config file) <a id="config"></a>

A config file in yaml syntax. The following parameters should always be included:

```yaml
seed: Seed for the random number generators (int)
columns: Width of simulation plane (int)
rows: Height of simulation plane (int)
probability: Probability per cell of adding grains (float)
d_probability: An incrementation value for driving multiple World instances in sandpiles.py (float)
n_runs: Number of instances to run in sandpiles.py
delta_t: Period for adding new grains in running sandpile (int)
running: Whether the sandpile is running (bool)
input: Path to input map file (str)
zhang: Whether the sandpile should be run in "Zhang mode" (bool)
z_threshold: The toppling threshold for "Zhang mode" (float)
z_epsilon: The epsilon value for "Zhang mode" (float)
output:
  data: The path to output data file (str)
  map: The path to output map file (str)
```

#### `sandpiles.py` (Script) <a id="sandpiles"></a>

Drives several [`World`](#world) instances simultaneously with multiprocessing.

#### `setup.py` (Script) <a id="setup"></a>

Compiles/builds the [`world.pyx`](#world) file. To compile, run `python3 setup.py build_ext --inplace`. It generates some warnings (especially in python 3.8), but these can most of the time be ignored.

#### `prof.py` (Script) <a id="prof"></a>

A file driving and profiling a [`World`](#world) instance, and saving the profile data in `profile.prof`.

#### `testrun.py` (Script) <a id="testrun"></a>

A simple and compact script to drive a [`World`](#world) instance.

### Data anlysis and graphing

All graphics are handled by [pyqtgraph](https://github.com/pyqtgraph/pyqtgraph). It's a good fit as it wraps a lot of convenient GUI features. If you're exepriencing issues with this module, be sure to check the [dependency test matrix](https://github.com/pyqtgraph/pyqtgraph#qt-bindings-test-matrix).

Raw data from the simulations is first analysed in [`analysis.py`](#analysis). The output from here is analysed for exponential coerrelations/power laws in [`lite_graphs.py`](#lite-graphs). The exponents found here can be displayed in [`graph_coeffs.py`](#graph-coeffs-graphs).

#### `definitions.py` (Module)

A small module providing some globally available functions and constants:

* `thresholds_gen(`**`float`**`std)`

  Generates threshold values for data analysis.

  * `std`: The standard deviation of the time series of number of critical cells.

#### `analysis.py` (Script) <a id="analysis"></a>

Fully automated analysis of raw simulation data. See the [Directory structure](#directory-structure) section for the outputs of this script.

#### `lite_graphs.py` (Script) <a id="lite-graphs"></a>

A GUI used to set the bounds inscribing the data to perform regression over. Automatically runs the regression and saves the coefficients to file.

#### `graph_coeffs.py` (Script) <a id="graph-coeffs"></a>

A script to display the coefficients/exponents found when running [`graph_coeffs.py`](#graph-coeffs). The plots are a little overwelming at first, but the legend window helps you make more sense out of them.
