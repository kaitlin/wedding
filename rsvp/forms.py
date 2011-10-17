from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rsvp.models import ATTENDING_CHOICES, Guest, Event, RSVP


VISIBLE_ATTENDING_CHOICES = [choice for choice in ATTENDING_CHOICES if choice[0] != 'no_rsvp']


class RSVPForm(forms.Form):
    email = forms.EmailField()
    name = forms.CharField(max_length=128)
    attending = forms.ChoiceField(choices=VISIBLE_ATTENDING_CHOICES, initial='yes', widget=forms.RadioSelect)
    number_of_guests = forms.IntegerField(initial=0)
    comment = forms.CharField(max_length=255, required=False, widget=forms.Textarea)
    event_id = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        if 'guest_class' in kwargs:
            self.guest_class = kwargs['guest_class']
            del(kwargs['guest_class'])
        else:
            self.guest_class = Guest
        super(RSVPForm, self).__init__(*args, **kwargs)
    
    #def clean_email(self):
     #   try:
      #      guest = self.guest_class._default_manager.get(email=self.cleaned_data['email'])
       # except ObjectDoesNotExist:
        #    raise forms.ValidationError, 'That e-mail is not on the guest list.'
        
        #if hasattr(guest, 'attending_status') and guest.attending_status != 'no_rsvp':
         #   raise forms.ValidationError, 'You have already provided RSVP information.'
        
        #return self.cleaned_data['email']
    def clean(self):
        cleaned_data = self.cleaned_data
        name = cleaned_data.get('name')
        event_id = cleaned_data.get('event_id')

        guest = Guest.objects.filter(name__contains=name.strip())
        event = Event.objects.filter(id=event_id)
        if len(guest) > 0 and len(event) > 0:
            guest = guest[0]
            event = event[0]
            
            r = RSVP.objects.filter(guest=guest, event=event)
            if len(r) > 0:
                raise forms.ValidationError, "You have already RSVP'd for this event"
            
            return cleaned_data
        else:
            raise forms.ValidationError, self.cleaned_data['name'] + " is not on the guest list"
    
    
    def clean_number_of_guests(self):
        if self.cleaned_data['number_of_guests'] < 0:
            raise forms.ValidationError, "The number of guests you're bringing can not be negative."
        return self.cleaned_data['number_of_guests']
        
    def save(self):
        #guest = self.guest_class._default_manager.get(email=self.cleaned_data['email'])
        event = Event.objects.get(id=self.cleaned_data['event_id'])
        guest = Guest.objects.get(name__contains=self.cleaned_data['name'].strip())
       
        r = RSVP(guest=guest, event=event)
        r.attending_status = self.cleaned_data['attending']
        r.number_of_guests = self.cleaned_data['number_of_guests']
        r.comment = self.cleaned_data['comment']
        r.save()
        return r
