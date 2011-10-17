from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import RequestContext
from rsvp.models import Event, Guest
from rsvp.forms import RSVPForm

def all_events(request):
    events = Event.objects.all()
    return render_to_response('events.html', {'events': events})

def event_view(request, slug, model_class=Event, form_class=RSVPForm, template_name='rsvp/event_view.html'):
    event = get_object_or_404(model_class, slug=slug)
    
    if request.POST:
        form = form_class(request.POST)
        if form.is_valid():
            guest = form.save().guest
            return HttpResponseRedirect(reverse('rsvp_event_thanks', kwargs={'slug': slug, 'guest_id': guest.id}))
    else:
        form = form_class()
    
    return render_to_response(template_name, {
        'event': event,
        'form': form
    }, context_instance=RequestContext(request))


def event_thanks(request, slug, guest_id, model_class=Event, template_name='rsvp/event_thanks.html'):
    event = get_object_or_404(model_class, slug=slug)
    
    try:
        guest = Guest.objects.get(id=guest_id)
    except ObjectDoesNotExist:
        raise Http404
    
    return render_to_response(template_name, {
        'event': event,
        'guest': guest,
    }, context_instance=RequestContext(request))
