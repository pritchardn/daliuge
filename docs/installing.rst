Installation
============

Docker images
-------------

The recommended and easiest way to get started is to use the docker container installation procedures provided to build and run the daliuge-engine and the daliuge-translator. We currently build the system in three images:

* *icrar/daliuge-base* contains all the basic |daliuge| libraries and dependencies.
* *icrar/daliuge-engine* is built on top of the :base image and includes the installation 
  of the DALiuGE execution engine.
* *icrar/daliuge-translator* is also built on top of the :base image and includes the installation 
  of the DALiuGE translator.


This way we try to separate the pre-requirements of the daliuge engine and translator from the rest of the framework, which is more dynamic. The idea is then to rebuild only the daliuge-engine image as needed when new versions of the framework need to be deployed, and not build it from scratch each time.

Most of the dependencies included in :base do not belong to the DALiuGE framework itself, but 
rather to its requirements (mainly to the spead2 communication protocol). Once we move out the spead2 application from this repository (and therefore the dependency of dfms on spead2) we'll re-organize these Dockerfiles to have a base installation of the dfms framework, and then build further images on top of that base image containing specific applications with their own system installation requirements.

The *daliuge-engine* image by default runs a generic daemon, which allows to then start the Master Manager, Node Manager or DataIsland Manager. This approach allows to change the actual manager deployment configuration in a more dynamic way and adjusted to the actual requirements of the environment.

Building the three images is easy, just start with the daliuge-base image by running::

  cd daliuge-common && ./build_common.sh && cd ..

then build the runtime::

  cd daliuge-engine&& ./build_engine.sh && cd ..

and last build the translator::

  cd daliuge-translator && ./build_translator.sh && cd ..

running the engine and the translator is equally simple::

  cd daliuge-engine && ./run_engine.sh && cd ..

and::

  cd daliuge-translator && ./run_translator.sh && cd ..

Note that the commands above will launch the images in interactive mode, which means that the output of the logging is routed to the terminal where the commands are executed. Also note that the containers will be removed after termination.


Direct Installation
-------------------

**NOTE: For most use cases the docker installation described above is recommended.** 

Requirements
############


The |daliuge| framework requires no packages apart from those listed in its

``setup.py``

file, which are automatically retrieved when running it. The spead2 library
(one of the |daliuge| optional requirements) however requires a number of libraries
installed on the system:

* boost-python
* boost-system
* boost-devel
* gcc >= 4.8

Installing
##########

|daliuge| is based on setuptools, and thus it follows the standard python installation
procedures.
The preferred way of installing the latest stable version of |daliuge|
is by using ``pip``::

 pip install --process-dependency-links daliuge

If you want to build from the latest sources you can get them from here::

 git clone https://github.com/ICRAR/daliuge
 cd daliuge

If a system-wide installation is required, then the following
commands can be issued::

 sudo pip --process-dependency-links install .

If ``pip`` is not available, you can also use a different approach with::

 python setup.py build
 sudo python setup.py install

If a virtualenv is loaded, then |daliuge| can be installed on it by simply running::

 pip install --process-dependency-links .

Again, if ``pip`` is not available, you can use the simpler form::

 python setup.py install

There is a known issue in some systems
when installing the ``python-daemon`` dependency,
which **needs** to be installed via ``pip``.

Porting from |daliuge| 0.X
--------------------------

With the release of |daliuge| 1.0.0
the code has been broken down into separate packages
to accommodate leaner and easier installations
when only a subset of the functionality is required.
In doing so we tried to maintain
as much backward compatibility as possible,
but there are some minor exceptions:

 * Code doing ``from dlg import delayed`` or similar must be changed
   to ``from dlg.runtime import delayed``.
 * Scripts finding the include directory path for daliuge headers
   using code like ``python -c 'import dlg; print(dlg.get_include_dir())``
   should switch to invoke ``dlg include_dir`` instead.
