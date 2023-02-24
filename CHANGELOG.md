### ChangeLog - 23.02.2023

- get rid of pydggrid library and rely on pre-installed SEPAL one. During the generation a metafile is written, that uses the defined projection and resolution. Todos are here to capture errors on available Projections, and introduce minimum resolution, which is possible in dggrid. Also a random offset shall be introduced to the over all function

- we split time-series extraction from running the chage algorithms to make this part more stable.

- date of the time-series are stored as simple list of integeres (YYYMMDD format) instead of DateTimeIndex. That make sit possible to store the file as json, and overcomes problems with pickle because of different versions

- sample size calculation now includes both, theoretical sampling error based on Cochran, and a simulated error on bias and precision base on global GFC data. Todos are here to integrate the envisaged plot size
