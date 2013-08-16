#-*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.forms import CharField, HiddenInput

try:
    from django.views.generic.base import ContextMixin
except ImportError:
    mixin_base = object

__all__ = ('FilterFormMixin','PreviousRedirectMixin',)


class FilterFormMixin(ContextMixin):
    """
    Mixin that adds filtering behaviour for list-based views.
    Changed in a way that can play nicely with other CBV simply by overriding the get_queryset(self) and
    get_context_data(self, **kwargs) method.
    """
    filter_form_cls = None
    use_filter_chaining = False

    def get_filter(self):
        return self.filter_form_cls(self.request.GET,
                                    runtime_context=self.get_runtime_context(),
                                    use_filter_chaining=self.use_filter_chaining)

    def get_queryset(self):
        qs = super(FilterFormMixin, self).get_queryset()
        qs = self.get_filter().filter(qs).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super(FilterFormMixin, self).get_context_data(**kwargs)
        context['filterform'] = self.get_filter()
        return context

    def get_runtime_context(self):
        return {'user': self.request.user}


class PreviousRedirectMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        ctx = super(PreviousRedirectMixin, self).get_context_data(**kwargs)
        ctx['form'].fields['_success_url'] = CharField(widget=HiddenInput,
                                                       required=False,
                                                       initial=self.request.META.get('HTTP_REFERER', '/')
                                                       )
        return ctx
    def get_success_url(self):
        return self.request.POST.get('_success_url','/')
