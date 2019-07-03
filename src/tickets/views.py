from django.shortcuts import get_object_or_404
from django.http import Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Ticket
from .forms import TicketForm
from datetime import datetime


def bug_or_feature(self):
    return 'bug' if 'bug' in self.request.path else 'feature'


class TicketListView(ListView):
    template_name = 'tickets/ticket-list-view.html'
    paginate_by = 8
    extra_context = {}
    allow_empty = True

    def get_queryset(self):
        issue = bug_or_feature(self)
        self.extra_context['issue'] = issue
        self.extra_context['count'] = Ticket.objects.filter(issue=issue).order_by('-updated_on').count()
        return Ticket.objects.filter(issue=issue).order_by('-updated_on')


class TicketDetailView(DetailView):
    template_name = 'tickets/ticket-detail-view.html'
    extra_context = {'issue': 'issue details', 'already_voted': 'false'}

    def get_object(self, queryset=Ticket):
        _id = self.kwargs.get('id')
        instance = Ticket.objects.filter(id=_id).first()
        user = self.request.user

        if instance:
            if user in instance.vote_profiles.all():
                self.extra_context['already_voted'] = 'true'
            else:
                self.extra_context['already_voted'] = 'false'
            return instance
        else:
            raise Http404


class TicketCreateView(CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket-create-update-view.html'
    extra_context = {'issue': 'create new ticket', 'button_text': 'create', 'time': datetime.now()}

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.issue = bug_or_feature(self)
        return super(TicketCreateView, self).form_valid(form)


class TicketUpdateView(UpdateView):
    form_class = TicketForm
    template_name = 'tickets/ticket-create-update-view.html'
    extra_context = {'issue': 'update ticket', 'button_text': 'update'}

    def get_object(self, queryset=Ticket):
        _id = self.kwargs.get('id')
        return get_object_or_404(Ticket, id=_id)

    def form_valid(self, form):
        return super().form_valid(form)
