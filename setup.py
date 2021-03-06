#!/usr/bin/env python

from distutils.core import setup

setup(name='fife-rpg',
      version='0.3',
      description='RPG framework using the FIFEngine',
      author='Karsten Bock',
      author_email='KarstenBock@gmx.net',
      url='http://fife-rpg.github.com/',
      packages=['fife_rpg', 'fife_rpg.components', 'fife_rpg.entities',
                'fife_rpg.systems', 'fife_rpg.actions', 'fife_rpg.behaviours',
                'fife_rpg.rpg_application', ],
      )
