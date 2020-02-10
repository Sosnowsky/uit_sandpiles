# Sandpiles

## Config file, inputs and outputs
The config file follows yaml syntax and should include the following:

```
criticality: 4
rows: 10
columns: 10
input: ''
output: 
  map: 'out_map.txt'
  data: 'output.txt'
seed: 666
```

`criticality` is an integer describing the number of grains a cell can hold before toppling. This is normally 4.

`rows` and `cols` are integers respectively descriping the number of rows and columns of the world plane.

`input` and `map` are strings respectively containing the path to an input and output file. If left empty, the world plane will be initiated with a uniform random distribution, and the final state of the world plane will not be saved. The files are read from and written to with the following format:

```
z[0][0];z[0][1];  ...  ;z[0][j];
z[1][0];z[1][1];  ...  ;z[1][j];
  ...  ;  ...  ;  ...  ;  ...  ;
z[i][0];z[i][1];  ...  ;z[i][j];
```

`data` is a string containing the path to a data output file. Data is appended on the end of each timestep, with the format given in the header, which reads as follows:

```
========================================================
t; topples; grains; flux; last insertion;
```

The default path to the config file is `./config.yml`. Any change to this should be reflected in `sandpiles.py`.

## Boundary conditions
If a pile along the boundaries of the world plane topples, the function `World.boundary(r, c)` is called with the exceeding indecies. The contents of this function can be altered.