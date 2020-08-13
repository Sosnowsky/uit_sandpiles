# Sandpiles - THIS README IS RARELY UP TO DATE

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
