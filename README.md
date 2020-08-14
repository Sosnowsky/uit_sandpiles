# Investigating power laws in sandpile models

## Models

The two models that currently are implemented are the BTW sandpile model (also known as the Abelian sandpile model) and the Zhang sandpile model. Both take place on a plane of individual cells.

### BTW model

Each cell has an integer value representing the number of grains at that cell. If the number of grains at a cell is greater than or equal to 4, 4 grains are removed from this cell and equally distributed between its four neighboring cells (both in the next timestep). This process is referred to as toppling of a critical site.

At the beginning of a timestep, new grains are added to the plane. By default these new grains are uniformly randomly distributed amongst all cells, but this can be modified. The number of grains added is another modifiable parameter; It can among other things be a constant (1 is often used), or a number drawn from a distribution.

If the simulation is configured as `running`, this introduction of new grains happens at each timestep - otherwise it only happens when there were no critical cells in the previous timestep.

More info available on [Wikipedia](https://en.wikipedia.org/wiki/Abelian_sandpile_model).

### The Zhang model

Here, the number of grains is no longer discrete - each cell has a continuous value. If this grain value is greater than or equal to some constant, this value is multiplied by some constant $\epsilon$. The ammount it is reduced by is equally distributed among the four neighboring cells.

The introduction of new grains is similar to in the BTW model

## Directory structure

The data generated and analysed in this project is exchanged between scripts in the shape of text files. This is rather impractical, so implementing some database (maybe hdf5?) would be a significant improvement.

Nevertheless, as is, raw data from the simulation is temporarily stored in `.txt` files. These are periodically backed up as `.d` and `.m` files, containing simulation time series and a serialised map of the simultion plane respectively.

When analysed, the following files are generated for each `*.d` file:

* `*.e` - a file containing the durations and areas/magnitudes of each topple event, categorized in thresholds.
  * Format: `[threshold index];[duration];[area]`

## Config file, inputs and outputs

The config file follows yaml syntax and should include the following:

```yaml
seed: [seed - int]
columns: [number of columns of world plane - int]
rows: [number of rows of world plane - int]
input: [path to input map file - str]
probability: [probability of adding a grain to an individual cell - float]
running: [whether to continuously add grains or wait for stable config first - bool]
output:
  data: [path to output file for data from the model]
  map: [path to output file for world map]
```

The `input` file is read when a new instance of thw `World` class is created. The `map` file is written to at the end of the `World.drive` function. Both files should be of the following format:

```text
z[0][0];z[0][1];  ...  ;z[0][j];
z[1][0];z[1][1];  ...  ;z[1][j];
  ...  ;  ...  ;  ...  ;  ...  ;
z[i][0];z[i][1];  ...  ;z[i][j];
```

The `data` file is appended to on the end of each timestep, with the format given in the file's first few lines.

If you intend to use `sandpiles.py` as a 'driver' file, the path to the config file should be `./config.yml`. This can be modified in `sandpiles.py`.

## Boundary conditions

If a pile along the boundaries of the world plane topples, the function `World.bound(r, c)` is called with the exceeding indecies. The default is to simply void the grains, but this function can be altered.

## Placement distribution

When a new grain is introduced, its position is given by the function `World.rand_pos()`, which can be altered.

## Usage

It is adviced to run `sandpiles.py` interactively with python's `-i` flag. From the interactive terminal, call the `world.drive(n, verbose, animate)` function to simulate `n` timesteps. Verbosity 0 is quiet, 1 shows the current timestep, 2 shows a progress bar and 3 draws the plane in ascii for each timestep.
