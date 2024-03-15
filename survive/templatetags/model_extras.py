from django import template

register = template.Library() # used to register template tags

@register.simple_tag # registers tag for use within templates
def survivor_points(survivor, season): # allows me to provide parameters within a template
    return survivor.points(season) # returns survivor's points as evaluated against the season rubric, if that season exists in the Survivor's 'season' ManyToMany relationship