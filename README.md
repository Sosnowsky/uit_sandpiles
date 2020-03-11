# Sandpiles - THIS README IS RARELY UP TO DATE

## Config file, inputs and outputs
The config file follows yaml syntax and should include the following:

```
seed: 666
columns: 128
rows: 128
input: 'data/in_map.txt'
probability: 0.005
running: True
output:
  data: 'data/output.txt'
  map: 'data/out_map.txt'
```

`rows` and `columns` are integers respectively descriping the number of rows and columns of the world plane.

`input` and `map` are strings respectively containing the path to an input and output file for the world map. If left empty, the world plane will be initiated with a uniform random distribution, and the final state of the world plane will not be saved. The files are read from and written to with the following format:

```
z[0][0];z[0][1];  ...  ;z[0][j];
z[1][0];z[1][1];  ...  ;z[1][j];
  ...  ;  ...  ;  ...  ;  ...  ;
z[i][0];z[i][1];  ...  ;z[i][j];
```

`data` is a string containing the path to a data output file. Data is appended on the end of each timestep, with the format given in the header.

`running` is a boolean value reflecting whether new grains should be added on each timestep as opposed to only when the plane has stabilized.

`probability` is a float describing the probability of the addition of a grain to each cell when new grains are to be introduced.

The default path to the config file is `./config.yml`. Any change to this should be reflected in `sandpiles.py`.

## Boundary conditions
If a pile along the boundaries of the world plane topples, the function `World.bound(r, c)` is called with the exceeding indecies. The contents of this function can be altered.

## Placement distribution
When new grains are introduced, their position is given by the function `World.rand_pos()`, which can be altered.

## Usage
It is adviced to run `sandpiles.py` interactively with python's `-i` flag. From the interactive terminal, call the `world.drive(n, verbose, animate)` function to simulate `n` timesteps. Verbosity 0 is quiet, 1 shows the current timestep, 2 shows a progress bar and 3 draws the plane in ascii for each timestep.