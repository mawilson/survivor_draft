from django import template

register = template.Library() # used to register template tags

@register.simple_tag # registers tag for use within templates
def survivor_points(survivor, season): # allows me to provide parameters within a template
    """Returns survivor's points as evaluated against the season rubric, if that season exists in the Survivor's 'season' ManyToMany relationship"""
    return survivor.points(season)

@register.simple_tag
def tribe_points(tribe, season):
    """Returns sum of points for all survivors within a tribe that belong to the provided season"""
    return tribe.points(season)