from django.contrib import admin
from django.http import HttpResponseRedirect

from .models import *

admin.site.register(Season)
admin.site.register(Rubric)
admin.site.register(Team)
admin.site.register(Tribe)


class SurvivorAdmin(admin.ModelAdmin):
    list_display = ["name", "status"]
    ordering = ["-id"]
    actions = ["associate_survivors"]

    @admin.action(description="Bulk associate Survivors to Seasons")
    def associate_survivors(self, request, queryset):
        selected = queryset.values_list("pk", flat=True)
        survivors_querystring = ",".join(str(pk) for pk in selected)
        return HttpResponseRedirect(
            "/admin/survivor_season_associate?survivors=%s" % survivors_querystring
        )


admin.site.register(Survivor, SurvivorAdmin)
