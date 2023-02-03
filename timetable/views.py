from django.http import HttpResponse
from django.shortcuts import render
from django.db.utils import IntegrityError
from django.db.models import Q
from django.views.generic import ListView, UpdateView, CreateView, DetailView

from .models import Subject, Teacher, Room, Group, SubjectAppointedGroup, Schedule, TeacherSubject, TeacherSched
import json

from .utils.timetable_splitter import find_free_lessons


def index(request):
    return render(request, 'base.html')


def load_from_json(request):
    file_subj = "./timetable/raw_data/subjects.json"
    f = open(file_subj)
    data = json.load(f)
    i = 1
    while True:
        try:
            obj = Subject(**data[str(i)])
            obj.save()
            i += 1
        except (KeyError, IntegrityError):
            break

    file_teachers = "./timetable/raw_data/teachers.json"
    f = open(file_teachers, encoding="utf-8")
    data = json.load(f)
    i = 1
    while True:
        try:
            obj = Teacher(**data[str(i)])
            obj.save()
            i += 1
        except (KeyError, IntegrityError):
            break

    file_rooms = "./timetable/raw_data/room.json"
    f = open(file_rooms)
    data = json.load(f)
    i = 1
    while True:
        try:
            obj = Room(**data[str(i)])
            obj.save()
            i += 1
        except (KeyError, IntegrityError):
            break

    file_groups = "./timetable/raw_data/groups.json"
    f = open(file_groups)
    data = json.load(f)
    i = 1
    while True:
        try:
            obj = Group(**data[str(i)])
            obj.save()
            i += 1
        except (KeyError, IntegrityError):
            break

    file_sfg = "./timetable/raw_data/SubjectsForGroups.json"
    f = open(file_sfg)
    data = json.load(f)
    i = 1
    while True:
        try:
            data[str(i)]['subject'] = Subject.objects.get(id=data[str(i)]['subject'])
            data[str(i)]['group'] = Group.objects.get(id=data[str(i)]['group'])
            obj = SubjectAppointedGroup(**data[str(i)])
            obj.save()
            i += 1
        except (KeyError, IntegrityError):
            break

    file_ts = "./timetable/raw_data/TeachersSubject.json"
    f = open(file_ts)
    data = json.load(f)
    i = 1
    while True:
        try:
            data[str(i)]['subject'] = Subject.objects.get(id=data[str(i)]['subject'])
            data[str(i)]['teacher'] = Teacher.objects.get(id=data[str(i)]['teacher'])
            obj = TeacherSubject(**data[str(i)])
            obj.save()
            i += 1
        except (KeyError, IntegrityError):
            break
    return HttpResponse(json.dumps(data), content_type="application/json")


def create_sched(request):
    try:
        Schedule.objects.filter(id=1)
        Schedule.objects.all().delete()
        t_sched = TeacherSched.objects.all()
        for t in t_sched:
            t.is_free = True
            t.save()
    except Schedule.DoesNotExist:
        pass
    days = 6
    lessons_per_day = 7
    subjects_per_groups = SubjectAppointedGroup.objects.order_by("?").all()

    for subject in subjects_per_groups:
        try:
            if subject.type == "Lecture":
                sched = Schedule.objects.filter(subject__subject__name=subject.subject.name, subject__type=subject.type, group=subject.group).get()
            else:
                sched = Schedule.objects.filter(subject=subject).get()
        except Schedule.DoesNotExist:
            sched = None
        if sched is None:
            try:
                for teacher in TeacherSubject.objects.filter(subject=subject.subject, type=subject.type).order_by("?"):
                    for room in Room.objects.filter(appointment=subject.type, capacity__gte=subject.group.size).order_by("?"):
                        for day in range(1, days + 1):
                            for lesson in range(1, lessons_per_day + 1):
                                all_groups_free = True
                                if subject.type == "Lecture":
                                    groups = subject.get_lection_groups()
                                else:
                                    groups = [subject.group]
                                for group in groups:
                                    if not group.is_free(day, lesson):
                                        all_groups_free = False
                                        break

                                if all_groups_free and room.is_free(day, lesson) and teacher.teacher.is_free(day,
                                                                                                             lesson):
                                    for group in groups:
                                        sched = Schedule()
                                        sched.group = group
                                        sched.subject = SubjectAppointedGroup.objects.filter(subject=subject.subject, type=subject.type, group=group).get()
                                        sched.week_day = day
                                        sched.lesson = lesson
                                        sched.teacher = teacher.teacher
                                        sched.room = room
                                        sched.save()

                                    t_sched = TeacherSched.objects.filter(teacher=teacher.teacher, lesson=lesson,
                                                                          week_day=day).get()
                                    t_sched.is_free = False
                                    t_sched.save()

                                    raise ZeroDivisionError

                print(f"Не смог найти подходящие условия для ведения {subject.subject.name}")
                break
            except ZeroDivisionError:
                continue  # if saved to db take next subject and try to save it


def create_schedule(request):
    days = 6
    lessons_per_day = 7
    groups = Group.objects.all()

    for group in groups:
        lections = SubjectAppointedGroup.objects.filter(group=group, type="Lecture")
        for lection in lections:
            rooms = Room.objects.filter(appointment="Lecture")
            for _ in range(lection.per_week):
                if len(Schedule.objects.filter(group=group, subject=lection)) < lection.per_week:
                    free_lessons = Schedule.get_free_lessons(groups, int(sum(
                        SubjectAppointedGroup.objects.filter(group=group, type="Lecture").values_list("per_week",
                                                                                                      flat=True)) / lessons_per_day) + 1)
                    lessons_cnt = 0
                    for lesson_union in free_lessons:
                        if lessons_cnt == lection.per_week:
                            break
                        for room in rooms:
                            if room.is_free(lesson_union[0]):
                                for lesson_for_gr in lesson_union:
                                    lesson_for_gr.room = room
                                    lesson_for_gr.subject = SubjectAppointedGroup.objects.filter(
                                        group=lesson_for_gr.group, type="Lecture", subject=lection.subject).first()
                                    lesson_for_gr.save()
                                lessons_cnt += 1
        seminars = SubjectAppointedGroup.objects.filter(group=group).exclude(type="Lecture")
        for seminar in seminars:
            rooms = Room.objects.filter(appointment=seminar.type)
            if len(Schedule.objects.filter(group=group, subject=seminar)) < seminar.per_week:
                free_lessons = Schedule.get_free_lessons([group], int(sum(
                    SubjectAppointedGroup.objects.filter(group=group).values_list("per_week",
                                                                                  flat=True)) / lessons_per_day) + 1)
                seminar_set = 0
                for lesson_union in free_lessons:
                    if seminar_set == seminar.per_week:
                        break
                    for lesson in lesson_union:
                        for room in rooms:
                            if room.is_free(lesson):
                                if seminar.teacher.is_free(lesson):
                                    lesson.subject = SubjectAppointedGroup.objects.exclude(type="Lecture").filter(
                                        group=group, subject=seminar.subject).first()
                                    lesson.room = room
                                    lesson.save()
                                    seminar_set += 1
    return HttpResponse(f"{True}")


def show_schedule(request, group_number):
    res = []
    group = Group.objects.filter(number=group_number).first()
    schedule = Schedule.objects.filter(group=group)
    for lesson in range(1, 8):
        res.append({"less": [less for less in schedule.filter(lesson=lesson).order_by("week_day")], "num": lesson})
    return render(request, "schedule_block.html",
                  {"lessons": res, "groups": Group.objects.all(), "group_selected": group_number})


class GroupList(ListView):
    model = Group
    template_name = 'group/block_groups.html'
    context_object_name = 'groups'


class GroupDetail(DetailView):
    model = Group
    template_name = 'group/block_group_detail.html'
    context_object_name = 'group'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subjects"] = SubjectAppointedGroup.objects.filter(group=context['group'])
        return context


class GroupEdit(UpdateView):
    model = Group
    template_name = 'block_edit.html'
    fields = ['number', 'size']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Изменение группы'
        return context


class GroupCreate(CreateView):
    model = Group
    template_name = 'block_edit.html'
    fields = ['number', 'size']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Добавление группы'
        return context


class SubjectList(ListView):
    model = Subject
    template_name = 'subject/subjects_block.html'
    context_object_name = 'subjects'


class SubjectDetail(DetailView):
    model = Subject
    template_name = 'subject/block_subject_detail.html'
    context_object_name = 'subject'


class SubjectEdit(UpdateView):
    model = Subject
    template_name = 'block_edit.html'
    fields = ['name']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Изменение предмета'
        return context


class SubjectCreate(CreateView):
    model = Subject
    template_name = 'block_edit.html'
    fields = ['name']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Создание предмета'
        return context


class TeacherList(ListView):
    model = Teacher
    template_name = 'teacher/teachers_block.html'
    context_object_name = 'teachers'


class TeacherDetail(DetailView):
    model = Teacher
    template_name = 'teacher/block_teacher_detail.html'
    context_object_name = 'teacher'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        sched = TeacherSched.objects.filter(teacher=context['teacher'])
        context["lessons"] = [[None for _ in range(6)] for _ in range(7)]
        for lesson in sched:
            context['lessons'][lesson.lesson - 1][lesson.week_day - 1] = lesson
        return context


class TeacherEdit(UpdateView):
    model = Teacher
    template_name = 'block_edit.html'
    fields = ['name']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Изменение преподавателя'
        return context


class TeacherCreate(CreateView):
    model = Teacher
    template_name = 'block_edit.html'
    fields = ['name']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Добавление преподавателя'
        return context


class RoomList(ListView):
    model = Room
    template_name = 'room/rooms_block.html'
    context_object_name = 'rooms'


class RoomDetail(DetailView):
    model = Room
    template_name = 'room/block_room_detail.html'
    context_object_name = 'room'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        res = [[None for _ in range(6)] for _ in range(7)]
        sched = Schedule.objects.filter(room=context['room'])
        for lesson in sched:
            res[lesson.lesson - 1][lesson.week_day - 1] = lesson
        context["lessons"] = res
        return context


class RoomEdit(UpdateView):
    model = Room
    template_name = 'block_edit.html'
    fields = ['number', 'capacity', 'appointment']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Изменение аудитории'
        return context


class RoomCreate(CreateView):
    model = Room
    template_name = 'block_edit.html'
    fields = ['number', 'capacity', 'appointment']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Добавление аудитории'
        return context


class SubjAppGroupList(ListView):
    model = SubjectAppointedGroup
    template_name = 'subjappgroups_block.html'
    context_object_name = "subjappgroups"


class SubjAppGroupEdit(UpdateView):
    model = SubjectAppointedGroup
    template_name = 'block_edit.html'
    fields = ['subject', 'group', 'teacher', 'per_week', 'type']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Изменение назначения предмета группе'
        return context


class SubjAppGroupCreate(CreateView):
    model = SubjectAppointedGroup
    template_name = 'block_edit.html'
    fields = ['subject', 'group', 'teacher', 'per_week', 'type']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Добавление назначения предмета группе'
        return context


def schedule(request):
    groups = Group.objects.all()
    return render(request, "schedule_choose_block.html", {"groups": groups})
