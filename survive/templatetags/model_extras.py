from django import template
from survive.models import Team

register = template.Library() # used to register template tags

@register.simple_tag # registers tag for use within templates
def survivor_points(survivor, season): # allows me to provide parameters within a template
    """Returns survivor's points as evaluated against the season rubric, if that season exists in the Survivor's 'season' ManyToMany relationship"""
    return survivor.points(season)

@register.simple_tag
def tribe_points(tribe, season):
    """Returns sum of points for all survivors within a tribe that belong to the provided season"""
    return tribe.points(season)

@register.simple_tag
def team_can_pick(team):
    """Returns a two element tuple containing a Boolean indicating whether a team can draft &, if not, a string for why"""
    if isinstance(team, Team):
        return team.can_pick()
    else: # an unprovided team cannot pick & has no feedback to give
        return (False, "")