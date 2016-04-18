Numerical simulation of the Maxwell-Bloch equations
============

This is a software package that I developed during my PhD to simulate my experiment. I've been translating this code to python during my postdoc as part of my general migration from MATLAB to python. I have been using these codes to simulate a new quantum memory idea we are toying with. I use `Chebyshev spectral method`_ to differentiate the spatial degree of freedom and then use `RK4`_ to integrate over time.

.. _Chebyshev spectral method: https://people.maths.ox.ac.uk/trefethen/8all.pdf
.. _RK4: https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods