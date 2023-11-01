from django.contrib import admin

from .models import Match, PlannedMatch, Tournament

admin.site.register(Match)
admin.site.register(PlannedMatch)
admin.site.register(Tournament)
