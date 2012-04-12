# -*- coding: utf-8 -*-
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""This module contains the exceptions from fife-rpg.

.. module:: exceptions
    :synopsis: Contains the exceptions from fife-rpg.

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""


class AlreadyRegisteredError(Exception):
    """Exception that gets raised when an object with the name is already
    registered"""
    def __init__(self, name, type):
        """Constructor
        
        Args:
            name: The name of the action that was already registered
            type: The type of the object
        """
        self.name = name
        self.type = type
    
    def __str__(self):
        """Returns the message of the Exception"""
        return "An %s with the name '%s' already exists" % (self.type,  self.name)

class NoSuchCommandError(Exception):
    """Exception that gets raised when the command is not found"""
    def __init__(self, name):
        """Constructor
        
        Args:
            name: The name of the command that was being tried to execute
        """
        self.name = name
    
    def __str__(self):
        """Returns the message of the Exception"""
        return "There is no '%s' command" % (self.name)
