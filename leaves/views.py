from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
from .models import LeaveRequest

# -------------------
# Mixins
# -------------------

class EmployeeQuerysetMixin(LoginRequiredMixin):
    """Employees see only their own; staff & superuser see all."""
    def get_queryset(self):
        qs = LeaveRequest.objects.all()
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return qs
        return qs.filter(employee=user)

class EmployeeRequiredMixin(UserPassesTestMixin):
    """Only employee, HR, or superuser can access object."""
    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        return user.is_superuser or user.is_staff or obj.employee == user

# -------------------
# CRUD
# -------------------

class LeaveListView(EmployeeQuerysetMixin, ListView):
    model = LeaveRequest
    template_name = "leaves/leave_list.html"
    context_object_name = "leaves"

class LeaveDetailView(EmployeeQuerysetMixin, EmployeeRequiredMixin, DetailView):
    model = LeaveRequest
    template_name = "leaves/leave_detail.html"

class LeaveCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    fields = ["reason"]
    template_name = "leaves/leave_form.html"
    success_url = reverse_lazy("leaves:list")

    def form_valid(self, form):
        form.instance.employee = self.request.user
        return super().form_valid(form)

class LeaveUpdateView(EmployeeQuerysetMixin, EmployeeRequiredMixin, UpdateView):
    model = LeaveRequest
    fields = ["reason"]
    template_name = "leaves/leave_form.html"
    success_url = reverse_lazy("leaves:list")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        # Employees can only edit pending requests
        if not (request.user.is_staff or request.user.is_superuser) and obj.status != "pending":
            return redirect("leaves:detail", pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

class LeaveDeleteView(EmployeeQuerysetMixin, EmployeeRequiredMixin, DeleteView):
    model = LeaveRequest
    template_name = "leaves/leave_confirm_delete.html"
    success_url = reverse_lazy("leaves:list")

# -------------------
# HR Approvals
# -------------------

class ApproveRejectView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = LeaveRequest
    template_name = "leaves/leave_detail.html"

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, *args, **kwargs):
        leave = self.get_object()
        action = request.POST.get("action")
        if action in ["approved", "rejected"]:
            leave.status = action
            leave.save()
        return redirect("leaves:detail", pk=leave.pk)
