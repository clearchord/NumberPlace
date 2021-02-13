# NumberPlace Solver

This program generates and solves Number Place problems.

A problem is to be saved in a problem file whose format is given as below.

<pre>
000607000
010598070
009010500
780020015
051704390
390060084
005030100
060452030
000901000
</pre>

Every digit 0 indicates a cell whose number is not fixed yet.

Usage:

To generate a problem:

`python NumberPlace.py generate path_to_problem sprawl_ratio`

To solve a problem:

`python NumberPlace.py solve path_to_problem`

Have fun!
