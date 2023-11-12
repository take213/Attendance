from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from attendanceapp.models import Attendance


# Create your views here.
class AttendanceList(LoginRequiredMixin, ListView):
    model = Attendance
    context_object_name = 'actions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['actions'] = context['actions'].filter(user=self.request.user)
        context['message'] = self.calc_sum(context['actions'])
        return context

    def calc_sum(self, actions):
        working_time = 0
        item_length = len(actions)
        # 未登録のとき
        if item_length == 0:
            return ''
        error_message = '入力内容に不備があります'
        for i, action in enumerate(actions):
            # 奇数番目のアイテムの状態は、開始でなければならない
            if i % 2 == 0 and i+1 != item_length:
                if action.state != '開始':
                    return error_message
                else:
                    working_time -= action.hour * 60 + action.minute
            # 偶数番目のアイテムでかつ最後でないアイテムの状態は、停止でなければならない
            elif i % 2 == 1 and i+1 != item_length:
                if action.state != '停止':
                    return error_message
                else:
                    working_time += action.hour * 60 + action.minute
            # 最後のアイテムの状態は、終了でなければならない
            elif i % 2 == 1 and i+1 == item_length:
                if action.state != '終了':
                    return error_message
                else:
                    working_time += action.hour * 60 + action.minute
            else:
                return error_message

            working_hour = working_time // 60
            working_minute = working_time % 60
            # densoの勤怠は15分区切りのため、15分以下は切り捨て
            working_minute -= working_minute % 15
            working_minute = str(working_minute).zfill(2)
        return f'本日の勤務時間は{working_hour}時間{working_minute}分です'


class AddItem(LoginRequiredMixin, CreateView):
    model = Attendance
    fields = ['hour', 'minute', 'state']
    # 成功したときのリダイレクト先
    success_url = reverse_lazy('top')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class EditItem(LoginRequiredMixin, UpdateView):
    model = Attendance
    fields = ['hour', 'minute', 'state']
    # 成功したときのリダイレクト先
    success_url = reverse_lazy('top')


class DeleteItem(LoginRequiredMixin, DeleteView):
    model = Attendance
    fields = ['hour', 'minute', 'state']
    # 成功したときのリダイレクト先
    success_url = reverse_lazy('top')
    context_object_name = 'action'


class RegisterAccount(FormView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('top')

    def form_valid(self, form):
        user = form.save()
        if user:
            login(self.request, user)
        return super().form_valid(form)
