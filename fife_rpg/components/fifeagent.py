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

"""The FifeAgent component and functions

.. module:: fifeagent
    :synopsis: The FifeAgent component and functions

.. moduleauthor:: Karsten Bock <KarstenBock@gmx.net>
"""
from fife import fife

from fife_rpg.components.base import Base
from fife_rpg.components.moving import Moving
from fife_rpg.components import ComponentManager
from fife_rpg.behaviours import AGENT_STATES

class FifeAgent(Base):
    """Component that stores the values for a fife agent
    
    Fields:
        layer: The layer the agent is on
        
        behaviour: The behaviour object of this agent
        
        instance: The FIFE instance of this agent. 
    """

    def __init__(self):
        Base.__init__(self, layer=object, behaviour=object, instance=object)

    @property
    def saveable_fields(self):
        """Returns the fields of the component that can be saved."""
        fields = self.fields.keys()
        fields.remove("layer")
        fields.remove("behaviour")
        fields.remove("instance")
        return fields

    @classmethod
    def register(cls, name="fifeagent", auto_register=True):
        """Registers the class as a component

        Args:
            name: The name under which the class should be registered
            
            auto_register: This sets whether components this component
            derives from will have their registered_as property set to the same
            name as this class.

        Returns:
            True if the component was registered, False if not.
        """
        return (super(FifeAgent, cls).register(name, auto_register))

def setup_behaviour(agent):
    """Attach the behaviour to the layer
    
    Args:
        agent: A :class:`fife_rpg.components.fifeagent.FifeAgent` instance
    """
    if agent.behaviour:
        agent.behaviour.attach_to_agent(agent)
        
def approach(entity, target_or_location, run_agent=True, next_action=None):
    """Move the entity to the given location, or follow the given target

    Args:
        entity: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a 
        fifeagent and a moving component
        
        target_or_location: A location to move to or another entity to follow
        
        run_agent: If true the run_action will be performed otherwise
        the walk_action. 
        
        next_action: The action the agent will perform when it reached
        its target.
    """    
    fifeagent_name = FifeAgent.registered_as
    moving_name = Moving.registered_as
    if fifeagent_name is None or moving_name is None:
        return
    fifeagent = getattr(entity, fifeagent_name)
    fifeagent.behaviour.state = AGENT_STATES.APPROACH
    moving = getattr(entity, moving_name)

    action = moving.run_action if run_agent else moving.walk_action
    speed = moving.run_speed if run_agent else moving.run_speed
    if isinstance(target_or_location, fife.Instance):
        agent = target_or_location
        fifeagent.instance.follow(action, 
                                  agent, 
                                  speed)
    else:
        location = target_or_location
        boxLocation = tuple([int(float(i)) for i in location])
        location = fife.Location(fifeagent.behaviour.getLocation())
        location.setLayerCoordinates(fife.ModelCoordinate(*boxLocation))
        fifeagent.instance.move(action, 
                                location, 
                                speed)

def run(entity, location):
    """Makes the entity run to a certain location
    
    Args:
        entity: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a 
        fifeagent and a moving component
        
        location: Screen position to run to.
    """
    fifeagent_name = FifeAgent.registered_as
    moving_name = Moving.registered_as
    if fifeagent_name is None or moving_name is None:
        return
    fifeagent = getattr(entity, fifeagent_name)
    fifeagent.behaviour.state = AGENT_STATES.RUN
    moving = getattr(entity, moving_name)
    fifeagent.behaviour.clear_animations()
    fifeagent.behaviour.next_action = None
    fifeagent.instance.move(moving.run_action, 
                            location, 
                            moving.run_speed)

def walk(entity, location):
    """Makes the entity walk to a certain location
    
    Args:
        entity: A :class:`fife_rpg.entities.rpg_entity.RPGEntity` with a 
        fifeagent and a moving component
        
        location: Screen position to run to.
    """
    fifeagent_name = FifeAgent.registered_as
    moving_name = Moving.registered_as
    if fifeagent_name is None or moving_name is None:
        return
    fifeagent = getattr(entity, fifeagent_name)
    fifeagent.behaviour.state = AGENT_STATES.WALK
    moving = getattr(entity, moving_name)
    fifeagent.behaviour.clear_animations()
    fifeagent.behaviour.next_action = None
    fifeagent.instance.move(moving.walk_action,
                            location,
                            moving.walk_speed)

def register_script_commands():
    """Register commands for this module"""
    ComponentManager.register_script_command("approach", approach)
    ComponentManager.register_script_command("walk", walk)
    ComponentManager.register_script_command("run", run)
    