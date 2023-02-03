from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


class Room(models.Model):
    number = models.CharField(max_length=10, unique=True, verbose_name='Номер')
    capacity = models.PositiveIntegerField(verbose_name='Вместимость чел.')
    appointment = models.CharField(max_length=15, choices=[("Seminars", "Семинар"), ("Lectures", "Лекция"),
                                                           ("Laboratory", "Лаборатория"), ("Terminal", "Терминал")], verbose_name='Тип ауд.')

    def is_free(self, week_day, lesson):
        lessons = Schedule.objects.filter(week_day=week_day, lesson=lesson,
                                          subject__isnull=False)
        for lesson in lessons:
            if lesson.room == self:
                return False
        return True

    def get_absolute_url(self):
        return reverse('room', kwargs={"pk": self.pk})


class Teacher(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="ФИО")

    def is_free(self, week_day, lesson):
        lessons = TeacherSched.objects.filter(week_day=week_day, lesson=lesson,
                                          is_free=True, teacher=self)
        for _ in lessons:
            return True
        return False

    def get_absolute_url(self):
        return reverse('teacher', kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')

    def get_absolute_url(self):
        return reverse('subject', kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class Group(models.Model):
    number = models.CharField(max_length=5, unique=True, verbose_name="Номер группы")
    size = models.PositiveIntegerField(verbose_name='Кол-во учеников')

    def is_free(self, week_day, lesson):
        lessons = Schedule.objects.filter(week_day=week_day, lesson=lesson,
                                          subject__isnull=False)
        for lesson in lessons:
            if lesson.group == self:
                return False
        return True

    def get_absolute_url(self):
        return reverse('group', kwargs={"pk": self.pk})

    def __str__(self):
        return self.number


class SubjectAppointedGroup(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.RESTRICT)
    group = models.ForeignKey(Group, on_delete=models.RESTRICT)
    type = models.CharField(max_length=15,
                            choices=[("Seminars", "Семинар"), ("Lectures", "Лекция"), ("Terminal", "Терминал")])

    class Meta:
        unique_together = ('subject', 'group', 'type')

    def __str__(self):
        return self.subject.name

    def get_lection_groups(self):
        subjects = SubjectAppointedGroup.objects.filter(subject=self.subject)
        groups = []
        for subject in subjects:
            if subject.group not in groups:
                groups.append(subject.group)
        return groups

    def get_absolute_url(self):
        return reverse('subjappgroup', kwargs={"pk": self.pk})


class Schedule(models.Model):
    subject = models.ForeignKey(SubjectAppointedGroup, on_delete=models.RESTRICT, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.RESTRICT)
    lesson = models.IntegerField()
    teacher = models.ForeignKey(Teacher, on_delete=models.RESTRICT)
    week_day = models.IntegerField()
    room = models.ForeignKey(Room, on_delete=models.RESTRICT, null=True, blank=True)

    class Meta:
        unique_together = ('subject', 'group', 'lesson', 'week_day')

    def to_psresence(self):
        if self.subject:
            res = {"name": self.subject.subject.name, "teacher": self.teacher, "type": self.subject.type,
                   "room": self.room.number}
            return res
        else:
            return self

    @staticmethod
    def get_free_lessons(groups: [Group], lessons_per_day: int):
        lessons = Schedule.objects.filter(group__in=groups, subject__isnull=True)
        res = []
        for day in range(1, 7):
            for lesson_cnt in range(1, 8):
                lessons_per_groups = lessons.filter(week_day=day, lesson=lesson_cnt)
                add = True
                if 7 - len(lessons.filter(week_day=day, group=groups[0])) < lessons_per_day:
                    if len(lessons_per_groups) == len(groups):
                        res.append(lessons_per_groups)
        return res


# @receiver(post_save, sender=Group)
# def group_save_handler(sender, **kwargs):
#     for day in range(1, 7):
#         for lesson in range(1, 8):
#             sched = Schedule()
#             sched.group = kwargs["instance"]
#             sched.lesson = lesson
#             sched.week_day = day
#             sched.save()


class University(models.Model):
    lessons_per_day = models.IntegerField()
    break_time = models.IntegerField(null=True, blank=True)


class TeacherSubject(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.RESTRICT)
    teacher = models.ForeignKey(Teacher, on_delete=models.RESTRICT)
    type = models.CharField(max_length=15,
                            choices=[("Seminars", "Семинар"), ("Lectures", "Лекция")])


class TeacherSched(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.RESTRICT)
    week_day = models.IntegerField()
    lesson = models.IntegerField()
    is_free = models.BooleanField(default=True)


@receiver(post_save, sender=Teacher)
def teacher_save_handler(sender, **kwargs):
    for day in range(1, 7):
        for lesson in range(1, 8):
            sched = TeacherSched()
            sched.teacher = kwargs["instance"]
            sched.lesson = lesson
            sched.week_day = day
            sched.save()