# -*- coding: utf-8 -*-
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

#  This module is based on the character statistics system from PARPG

"""The character statistics system manages the character statistics.

.. module:: character_statistics
    :synopsis: Manages the character statistics
.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from builtins import object
import yaml

from fife_rpg.systems import Base
from fife_rpg.entities import RPGEntity
from fife_rpg.components.character_statistics import CharacterStatistics
from fife_rpg.exceptions import AlreadyRegisteredError


def get_stat_cost(offset):
    """Gets and returns the cost to increase stat based on the offset"""

    if offset < 0:
        offset *= -1

    if offset < 22:
        return 1
    elif offset < 29:
        return 2
    elif offset < 32:
        return 3
    elif offset < 35:
        return 4
    elif offset < 36:
        return 5
    elif offset < 38:
        return 6
    elif offset < 39:
        return 7
    elif offset < 40:
        return 8
    elif offset < 41:
        return 9
    else:
        return 10


class NoSuchStatisticError(Exception):

    """Exception that gets raised when a statistic was tried to be accessed
    that does not exist

    Properties:
        name: The name of the statistic
    """

    def __init__(self, name):
        Exception.__init__(self)
        self.name = name

    def __str__(self):
        """Returns the message of the Exception"""
        return "There is no %s statistic" % (self.name)


class NoStatisticComponentError(Exception):

    """Exception that gets raised when an entity does not have a
    character_statistics component

    Properties:
        entity: A :class:`fife_rpg.entities.rpg_entity.RPGEntity`
    """

    def __init__(self, entity):
        Exception.__init__(self)
        self.entity = entity

    def __str__(self):
        """Returns the message of the Exception"""
        return ("The %s entity does not have character statistics" %
                self.entity.identifier)


class Statistic(object):

    """Class to store the data about a statistic

    Properties:
        name: The internal name of the statistic

        view_name: The displayed name of the statistic

        description: The description of the statistic
    """

    def __init__(self, name, view_name, description):
        self.name = name
        self.view_name = view_name
        self.description = description


class CalculatedStatistic(Statistic):

    """Class to store the data about a calculated statistic

    Properties:
        name: The internal name of the statistic

        view_name: The displayed name of the statistic

        influences: The other statistics that influence this

        description: The description of the statistic
    """

    def __init__(self, name, view_name, description, influences):
        Statistic.__init__(self, name, view_name, description)
        self.influences = influences


class CharacterStatisticSystem(Base):

    """The game environment system manages what variables and functions are
    available to scripts.

    Properties:
        primary_statistics: Dictionary holding the primary statistics

        secondary_statistics: Dictionary holfing the secondary statistics

        min_stat_value: Class property that determines the minimum value a
        statistic can have

        default_stat_value: Class property that determines the average value of
        the statistic. This is used for offset calculation.

        max_stat_value: Class property that determines the maximum value a
        statistic can have

        dependencies: List of class this system depends on
    """
    min_stat_value = 0
    default_stat_value = 50
    max_stat_value = 100

    dependencies = [CharacterStatistics]

    @classmethod
    def register(cls, name="character_statistics"):
        """Registers the class as a system

        Args:
            name: The name under which the class should be registered
        Returns:
            True if the system was registered, False if not.
        """
        return super(CharacterStatisticSystem, cls).register(name)

    def __init__(self):
        Base.__init__(self)
        self.primary_statistics = {}
        self.secondary_statistics = {}

    def add_primary_statistic(self, name, view_name, description):
        """Adds a primary statistic to the system

        Args:
            name: Short internal name for the statistic

            view_name: Name that is displayed

            description: Text that describes the statistic
        """
        if name in self.primary_statistics:
            raise AlreadyRegisteredError(name, "Statistic")
        statistic = Statistic(name, view_name, description)
        self.primary_statistics[name] = statistic

    def add_secondary_statistic(self, name, view_name,
                                description, influences):
        """Adds a secondary statistic to the system

        Args:
            name: Short internal name for the statistic

            view_name: Name that is displayed

            description: Text that describes the statistic

            influences: The other statistics that influence this
        """
        if name in self.secondary_statistics:
            raise AlreadyRegisteredError(name, "Statistic")
        statistic = CalculatedStatistic(name, view_name, description,
                                        influences)
        self.secondary_statistics[name] = statistic

    def load_statistics_from_file(self, filename):
        """Clears the statistics and populates them from a file

        Args:
            filename: The path to the file
        """
        statistics_file = open(filename, "r")
        statistics_data = yaml.load(statistics_file)
        for name, primary_data in statistics_data["primary"].items():
            view_name = primary_data["name"]
            desc = primary_data["description"]
            self.add_primary_statistic(name,
                                       view_name,
                                       desc)
        for name, secondary_data in statistics_data["secondary"].items():
            view_name = secondary_data["name"]
            desc = secondary_data["description"]
            influences = secondary_data["influences"]
            self.add_secondary_statistic(name,
                                         view_name,
                                         desc,
                                         influences)

    def get_statistic_value(self, entity, statistic):
        """Get the entities value of the given statistic

        Args:
            entity: An :class:`fife_rpg.entities.rpg_entity.RPGEntity` or the
            name of the entity

            statistic: The internal name of the statistic
        """
        if isinstance(entity, str):
            entity = self.world.get_entity(entity)
        if not getattr(entity, CharacterStatistics.registered_as):
            raise NoStatisticComponentError(entity)
        if statistic in self.primary_statistics:
            statistics = getattr(entity, CharacterStatistics.registered_as)
            try:
                return statistics.primary_stats[statistic]
            except KeyError:
                return 0
        elif statistic in self.secondary_statistics:
            statistics = getattr(entity, CharacterStatistics.registered_as)
            try:
                return statistics.secondary_stats[statistic]
            except KeyError:
                return 0
        else:
            NoSuchStatisticError(statistic)

    def get_primary_statistic_values(self, entity):
        """Collects and returns the values of the primary statitistic values
        of the entity.

        Args:
            entity: An :class:`fife_rpg.entities.rpg_entity.RPGEntity` or the
            name of the entity

        Returns:
            A dictionary containing the statistic short names and the values
            for that entity
        """
        if isinstance(entity, str):
            entity = self.world.get_entity(entity)
        if not getattr(entity, CharacterStatistics.registered_as):
            raise NoStatisticComponentError(entity)
        primary_statistics = {}
        for statistic in self.primary_statistics.keys():
            value = self.get_statistic_value(entity, statistic)
            primary_statistics[statistic] = value
        return primary_statistics

    def get_secondary_statistic_values(self, entity):
        """Collects and returns the values of the secondary statitistic values
        of the entity.

        Args:
            entity: An :class:`fife_rpg.entities.rpg_entity.RPGEntity` or the
            name of the entity

        Returns:
            A dictionary containing the statistic short names and the values
            for that entity
        """
        if isinstance(entity, str):
            entity = self.world.get_entity(entity)
        if not getattr(entity, CharacterStatistics.registered_as):
            raise NoStatisticComponentError(entity)
        secondary_statistics = {}
        for statistic in self.secondary_statistics.keys():
            value = self.get_statistic_value(entity, statistic)
            secondary_statistics[statistic] = value
        return secondary_statistics

    def get_statistic_values(self, entity):
        """Collects and returns the combined values of the primary and
        secondary statitistic values of the entity.

        Args:
            entity: An :class:`fife_rpg.entities.rpg_entity.RPGEntity` or the
            name of the entity

        Returns:
            A dictionary containing the statistic short names and the values
            for that entity
        """
        statistics = {}
        statistics.update(self.get_primary_statistic_values(entity))
        statistics.update(self.get_secondary_statistic_values(entity))
        return statistics

    def get_statistic_points(self, entity):
        """Gets the available statistic points of the entity

        Args:
            entity: An :class:`fife_rpg.entities.rpg_entity.RPGEntity` or the
            name of the entity
        """
        if isinstance(entity, str):
            entity = self.world.get_entity(entity)
        if not getattr(entity, CharacterStatistics.registered_as):
            raise NoStatisticComponentError(entity)
        char_stats = getattr(entity, CharacterStatistics.registered_as)
        return char_stats.stat_points

    def get_statistic_increase_cost(self, entity, statistic):
        """Calculate and return the cost to increase the statistic

        Args:
            entity: An :class:`fife_rpg.entities.rpg_entity.RPGEntity` or the
            name of the entity

            statistic: The internal name of the statistic
        """
        if isinstance(entity, str):
            entity = self.world.get_entity(entity)
        if not getattr(entity, CharacterStatistics.registered_as):
            raise NoStatisticComponentError(entity)
        char_stats = getattr(entity, CharacterStatistics.registered_as)
        cur_value = char_stats.primary_stats[statistic]
        new_value = cur_value + 1
        offset = new_value - self.default_stat_value
        return get_stat_cost(offset)

    def get_statistic_decrease_gain(self, entity, statistic):
        """Calculate and return the gain of decreasing the statistic

        Args:
            entity: An :class:`fife_rpg.entities.rpg_entity.RPGEntity` or
            the name of the entity

            statistic: The internal name of the statistic
        """
        if isinstance(entity, str):
            entity = self.world.get_entity(entity)
        if not getattr(entity, CharacterStatistics.registered_as):
            raise NoStatisticComponentError(entity)
        char_stats = getattr(entity, CharacterStatistics.registered_as)
        cur_value = char_stats.primary_stats[statistic]
        new_value = cur_value - 1
        offset = new_value - self.default_stat_value
        return get_stat_cost(offset)

    def can_increase_statistic(self, entity, statistic):
        """Checks whether the given statistic can be increased or not.

        Args:
            entity: An :class:`fife_rpg.entities.rpg_entity.RPGEntity` or the
            name of the entity

            statistic: The internal name of the statistic

        Returns:
            True if the statistic can be increase, False if not.
        """
        if statistic not in self.primary_statistics:
            return False  # Only primary statistics can be increased
        value = self.get_statistic_value(entity, statistic)
        if value < self.max_stat_value:
            cost = self.get_statistic_increase_cost(entity, statistic)
            return cost <= self.get_statistic_points(entity)
        return False

    def can_decrease_statistic(self, entity, statistic):
        """Checks whether the given statistic can be decreased or not.

        Args:
            entity: An :class:`fife_rpg.entities.rpg_entity.RPGEntity` or the
            name of the entity

            statistic: The internal name of the statistic

        Returns:
            True if the statistic can be decrease, False if not.
        """
        if statistic not in self.primary_statistics:
            return False  # Only primary statistics can be decreased
        statistic = self.get_statistic_value(entity, statistic)
        return statistic > self.min_stat_value

    def increase_statistic(self, entity, statistic):
        """Increase the statistic by one, if possible.

        Args:
            entity: An :class:`fife_rpg.entities.rpg_entity.RPGEntity` or the
            name of the entity

            statistic: The internal name of the statistic
        """
        if not self.can_increase_statistic(entity, statistic):
            return
        if isinstance(entity, str):
            entity = self.world.get_entity(entity)
        if not getattr(entity, CharacterStatistics.registered_as):
            raise NoStatisticComponentError(entity)
        char_stats = getattr(entity, CharacterStatistics.registered_as)
        cost = self.get_statistic_increase_cost(entity, statistic)
        char_stats.primary_stats[statistic] += 1
        char_stats.stat_points -= cost

    def decrease_statistic(self, entity, statistic):
        """Decrease the statistic by one, if possible.

        Args:
            entity: An :class:`fife_rpg.entities.rpg_entity.RPGEntity` or the
            name of the entity

            statistic: The internal name of the statistic
        """
        if not self.can_decrease_statistic(entity, statistic):
            return
        if isinstance(entity, str):
            entity = self.world.get_entity(entity)
        if not getattr(entity, CharacterStatistics.registered_as):
            raise NoStatisticComponentError(entity)
        char_stats = getattr(entity, CharacterStatistics.registered_as)
        gain = self.get_statistic_increase_cost(entity, statistic)
        char_stats.primary_stats[statistic] -= 1
        char_stats.stat_points += gain

    def step(self, time_delta):  # pylint: disable=W0613
        """Execute a time step for the system. Must be defined
        by all system classes.

        Args:
            time_delta: Time elapsed since last step
        """
        comp_name = CharacterStatistics.registered_as
        entity_extent = getattr(self.world[RPGEntity], comp_name)
        for entity in entity_extent:
            stats_component = getattr(entity, comp_name)
            comp_secondary_stats = stats_component.secondary_stats
            for statistic_name, statistic in (
                    iter(self.secondary_statistics.items())):
                total = 0
                for name, influence in statistic.influences.items():
                    value = self.get_statistic_value(entity, name)
                    total += value * influence
                comp_secondary_stats[statistic_name] = total
