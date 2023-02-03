
def find_free_lessons(schedule: [[[None]]], lections_per_day:int) -> [(int, int)]:
    res = []
    groups_cnt = len(schedule)
    for day in range(len(schedule[0])):
        for lesson in range(len(schedule[0][0])):
            fl = True
            for group in range(groups_cnt):
                if schedule[group][day][lesson] is not None:
                    fl = False
                    break
            if fl:
                have_lecture_today = 0
                for i in range(len(schedule[group][day])):
                    if schedule[group][day][i] is not None:
                        if schedule[group][day][i].type == "Lecture":
                            have_lecture_today += 1
                if have_lecture_today < lections_per_day:
                    res.append((day, lesson))
    return res # [(day, lesson)]

