# from dal import autocomplete
# from results.models import Race
# from django.http import HttpResponse


# def index(request):
#     return HttpResponse("Hello, world. You're at the results index. You probably want to access the API at /v1/api for test or prod directly or /v1 for the CDN.")


# class RaceAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         if not self.request.user.is_authenticated():
#             return Race.objects.none()

#         qs = Race.objects.all()

#         if self.q:
#             qs = qs.filter(name__istartswith=self.q)

#         return qs