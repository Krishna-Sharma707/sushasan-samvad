from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .forms import RegistrationForm, UploadMeetingForm, SuggestionForm
from .models import Meeting, MeetingSuggestion, District, Village
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse


VILLAGER = 2
VILLAGE_ADMIN = 1
DISTRICT_ADMIN = 3


def is_role(user, role):
    return user.groups.filter(id=role).exists()


def is_district_admin(user):
    return is_role(user, DISTRICT_ADMIN)


def is_village_admin(user):
    return is_role(user, VILLAGE_ADMIN)


# Create your views here.
def register(request):
    if request.method == 'GET':
        form = RegistrationForm()
        return render(request, 'register.html', {'form': form})
    elif request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.errors:
            return render(request, 'register.html', {'form': form})
        user = form.save()
        user.save()
        login(request, user)
        if is_role(user, DISTRICT_ADMIN):
            return HttpResponseRedirect(reverse('district', args=[user.district_id]))
        else:
            return HttpResponseRedirect(reverse('village', args=[user.village_id]))


def upload_meeting(request):
    if request.method == 'GET':
        form = UploadMeetingForm()
        return render(request, 'upload_meeting.html', {'form': form})
    elif request.method == 'POST':
        form = UploadMeetingForm(request.POST, request.FILES)
        meeting = form.save(commit=False)
        meeting.village = request.user.village
        meeting.save()
        if not form.is_valid():
            return render(request, 'upload_meeting.html', {'form': form})


def meeting(request, meeting_id):
    if request.method == 'GET':
        m = Meeting.objects.get(id=meeting_id)
        print(is_role(request.user, VILLAGE_ADMIN))
        if is_role(request.user, VILLAGE_ADMIN) or is_role(request.user, DISTRICT_ADMIN):
            return render(request, 'meeting.html',
                          {'meeting': m, 'suggestions': MeetingSuggestion.objects.filter(meeting_id=m.pk)})
        else:
            form = SuggestionForm()
            return render(request, 'meeting.html', {'meeting': m, 'form': form})
    elif request.method == 'POST':
        form = SuggestionForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, 'meeting.html', {'meeting': Meeting.objects.get(id=meeting_id), 'form': form})
        suggestion = form.save(commit=False)
        suggestion.meeting = Meeting.objects.get(id=meeting_id)
        suggestion.made_by = request.user
        suggestion.save()
        return HttpResponse('Suggestion recorded')


@user_passes_test(is_district_admin)
def district(request, dist_id):
    dist = District.objects.get(id=dist_id)
    return render(request, 'district.html', {'district': dist, 'villages': Village.objects.filter(district_id=dist_id)})


def village(request, village_id):
    meetings = Meeting.objects.filter(village_id=village_id)
    return render(request, 'village.html', {'meetings': meetings, 'village': Village.objects.get(id=village_id)})
