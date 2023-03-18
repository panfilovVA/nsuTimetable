:- dynamic(schedule/7).
addSchedule(subject(SubjectID, SubjectName), Type, teacher(TeacherID, TeacherName), room(RoomNum, RoomCapacity, RoomType), group(Number, StudCnt), WeekDay, Lesson) :- assert(schedule(subject(SubjectID, SubjectName), Type, teacher(TeacherID, TeacherName), room(RoomNum, RoomCapacity, RoomType), group(Number, StudCnt), WeekDay, Lesson)).

:- dynamic(group/2).
addGroup(number, students_cnt) :- assert(group(number, students_cnt)).

/* check that group is free at specific day and lesson*/
group_free(Group, WeekDay, Lesson) :- not(schedule(_, _, _, _, Group, WeekDay, Lesson)).

/* group(number, cnt of students)
group(1, 15).*/
:- include("groups.pl").


:- dynamic(room/3).
addRoom(Number, Capacity, Appointment) :- assert(room(Number, Capacity, Appointment)).

/* check that room is free at specific day and lesson */
room_free(Room, WeekDay, Lesson) :- not(schedule(_, _, _, Room, _, WeekDay, Lesson)).

:- include("rooms.pl").

/* get list of rooms by type */
get_rooms_by_type(Type, Rooms) :- findall(room(Num, Capacity, Type), room(Num, Capacity, Type), Rooms).

/* subject(id, name) */
:- dynamic(subject/2).
addSubject(Id, Name) :- assert(subject(Id, Name)).


/* teacher(id, name) */
:- dynamic(teacher/2).
addTeacher(Id, Name) :- assert(teacher(Id, Name)).

/* check that teacher is free at specific day and lesson*/
teacher_free(Teacher, WeekDay, Lesson) :- not(schedule(_, _, Teacher, _, _, WeekDay, Lesson)).



/* teacher_subject(subjectID, subjectName, teacherID, teacherName, type) */
:- dynamic(teacher_subject/3).
addTeacherSubject(subjectID, subjectName, teacherID, teacherName, type) :- assert(teacher_subject(subject(subjectID, subjectName), teacher(teacherID, teacherName), type)).
:- include("teacher_subject.pl").



get_teachers_by_subject(subject(SubID, SubName), Type, Res) :- setof(teacher(TeacherID, TeacherName), teacher_subject(subject(SubID, SubName), teacher(TeacherID, TeacherName), Type), Res).

/* group_subject(id, subjectID, groupID, type) */
:- dynamic(group_subject/4).
addGroupSubject(id, subjectID, subjectName, groupID, groupNumber, type) :- assert(group_subject(id, subject(id, subjectName), group(groupID, groupNumber), type)).
:- include("group_subject.pl").





/* genearate empty schedule */
generate_empty_schedule([group(GrNum, GrCup)]) :- generator_empty_schedule(group(GrNum, GrCup), 6, 7).
generate_empty_schedule([group(GrNum, GrCup)|Tail]) :- generator_empty_schedule(group(GrNum, GrCup), 6, 7), generate_empty_schedule(Tail).
generator_empty_schedule([]).

generator_empty_schedule(group(GrNum, GrCup), WeekDay, Lesson) :- WeekDay > 0, Lesson > 0, assert(schedule(0, 0, 0, 0, group(GrNum, GrCup), WeekDay, Lesson)), LessonM is Lesson - 1,  generator_empty_schedule(group(GrNum, GrCup), WeekDay, LessonM).
generator_empty_schedule(group(GrNum, GrCup), WeekDay, Lesson) :- WeekDay > 0, Lesson < 1, WeekDayM is WeekDay - 1, generator_empty_schedule(group(GrNum, GrCup), WeekDayM, 7).
generator_empty_schedule(_, WeekDay, _) :- WeekDay < 1.

get_freetime_in_schedule_by_group(group(GrNum, GrCup), Lessons) :- findall(schedule(0, 0, 0, 0, group(GrNum, GrCup), WeekDay, Lesson), schedule(0, 0, 0, 0, group(GrNum, GrCup), WeekDay, Lesson), Lessons).

get_schedule(Res) :- findall(group(GrNum, GrSize), group(GrNum, GrSize), Groups), generate_empty_schedule(Groups), findall(lesson(subject(SubID, SubName), group(GrNum, GrSize), Type), group_subject(_, subject(SubID, SubName), group(GrNum, GrSize), Type), Lessons), pred_a(Lessons, Res).


check_teachers_rooms_lessons(Lesson, Teachers, Rooms, Lessons, Res) :- check_controller(Lesson, Teachers, Rooms, Lessons, Res).

check_controller(Lesson, Teachers, Rooms, Lessons, Res) :- 
	check_teacher_free(Teachers, Lessons, LessonsTFree), 
	check_room_free(Rooms, Lessons, LessonsRFree), 
	get_same_lessons(Lesson, LessonsTFree, LessonsRFree, Res).

check_teacher_free(Teachers, Lessons, LessonsTFree) :- check_teacher_free(Teachers, Lessons, Lessons, [], LessonsTFree).

check_teacher_free([Teacher], [schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson)], Lessons, Buff, Res) :- 
	teacher_free(Teacher, WeekDay, Lesson),
	append(Buff, [schedule(0, 0, Teacher, 0, group(GrNum, GrSize), WeekDay, Lesson)], Res).

check_teacher_free([Teacher], [schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson)], Lessons, Buff, Res) :- 
	not(teacher_free(Teacher, WeekDay, Lesson)).

check_teacher_free([Teacher|TeachersTail], [schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson)], Lessons, Buff, Res) :- 
	teacher_free(Teacher, WeekDay, Lesson),
	append(Buff, [schedule(0, 0, Teacher, 0, group(GrNum, GrSize), WeekDay, Lesson)], NewBuff),
	check_teacher_free(TeachersTail, Lessons, Lessons, NewBuff, Res).

check_teacher_free([Teacher|TeachersTail], [schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson)], Lessons, Buff, Res) :- 
	not(teacher_free(Teacher, WeekDay, Lesson)),
	check_teacher_free(TeachersTail, Lessons, Lessons, Buff, Res).

check_teacher_free([Teacher|TeachersTail], [schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson)|LessonsTail], Lessons, Buff, Res) :- 
	teacher_free(Teacher, WeekDay, Lesson),
	append(Buff, [schedule(0, 0, Teacher, 0, group(GrNum, GrSize), WeekDay, Lesson)], NewBuff),
	check_teacher_free([Teacher|TeachersTail], LessonsTail, Lessons, NewBuff, Res).

check_teacher_free([Teacher|TeachersTail], [schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson)|LessonsTail], Lessons, Buff, Res) :- 
	not(teacher_free(Teacher, WeekDay, Lesson)),
	check_teacher_free([Teacher|TeachersTail], LessonsTail, Lessons, Buff, Res).


/* Get rooms that free */

check_room_free(Rooms, Lessons, LessonsTFree) :- check_room_free(Rooms, Lessons, Lessons, [], LessonsTFree).

check_room_free([Room], [schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson)], Lessons, Buff, Res) :- 
	room_free(Room, WeekDay, Lesson),
	append(Buff, [schedule(0, 0, 0, Room, group(GrNum, GrSize), WeekDay, Lesson)], Res).

check_room_free([Room], [schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson)], Lessons, Buff, Res) :- 
	not(room_free(Room, WeekDay, Lesson)).
	
check_room_free([Room|RoomsTail], [schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson)], Lessons, Buff, Res) :- 
	room_free(Room, WeekDay, Lesson),
	append(Buff, [schedule(0, 0, 0, Room, group(GrNum, GrSize), WeekDay, Lesson)], NewBuff),
	check_room_free(RoomsTail, Lessons, Lessons, NewBuff, Res).

check_room_free([Room|RoomsTail], [schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson)], Lessons, Buff, Res) :- 
	not(room_free(Room, WeekDay, Lesson)),
	check_room_free(RoomsTail, Lessons, Lessons, Buff, Res).

check_room_free([Room|RoomsTail], [schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson)|LessonsTail], Lessons, Buff, Res) :- 
	room_free(Room, WeekDay, Lesson),
	append(Buff, [schedule(0, 0, 0, Room, group(GrNum, GrSize), WeekDay, Lesson)], NewBuff),
	check_room_free([Room|RoomsTail], LessonsTail, Lessons, NewBuff, Res).

check_room_free([Room|RoomsTail], [schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson)|LessonsTail], Lessons, Buff, Res) :- 
	not(room_free(Room, WeekDay, Lesson)),
	check_room_free([Room|RoomTail], LessonsTail, Lessons, Buff, Res).

get_same_lessons(Lesson, TeacherSched, RoomsSched, Res) :- get_same_lessons(Lesson, TeacherSched, RoomsSched, RoomsSched, [], Res).

get_same_lessons(_, [schedule(0, 0, Teacher, 0, Group, TWeekDay, TLesson)], [schedule(0, 0, 0, Room, Group, RWeekDay, RLesson)], RoomsSched, Buff, Res) :- 
	not(
		(TWeekDay = RWeekDay,
			TLesson = RLesson)).

get_same_lessons(lesson(Subject, _, Type), [schedule(0, 0, Teacher, 0, Group, TWeekDay, TLesson)], [schedule(0, 0, 0, Room, Group, RWeekDay, RLesson)], RoomsSched, Buff, Res) :- 
	TWeekDay = RWeekDay,
	TLesson = RLesson,
	append(Buff, [schedule(Subject, Type, Teacher, Room, Group, TWeekDay, TLesson)], Res).

get_same_lessons(lesson(Subject, _, Type), [schedule(0, 0, Teacher, 0, Group, TWeekDay, TLesson)|TSchedTail], [schedule(0, 0, 0, Room, Group, RWeekDay, RLesson)], RoomsSched, Buff, Res) :- 
	TWeekDay = RWeekDay,
	TLesson = RLesson,
	append(Buff, [schedule(Subject, Type, Teacher, Room, Group, TWeekDay, TLesson)], NewBuff),
	get_same_lessons(lesson(Subject, _, Type), TSchedTail, RoomsSched, RoomsSched, NewBuff, Res).

get_same_lessons(lesson(Subject, _, Type), [schedule(0, 0, Teacher, 0, Group, TWeekDay, TLesson)|TSchedTail], [schedule(0, 0, 0, Room, Group, RWeekDay, RLesson)], RoomsSched, Buff, Res) :- 
	not(
		(TWeekDay = RWeekDay,
			TLesson = RLesson)),
	get_same_lessons(lesson(Subject, _, Type), TSchedTail, RoomsSched, RoomsSched, Buff, Res).

get_same_lessons(lesson(Subject, _, Type), [schedule(0, 0, Teacher, 0, Group, TWeekDay, TLesson)|TSchedTail], [schedule(0, 0, 0, Room, Group, RWeekDay, RLesson)|RSchedTail], RoomsSched, Buff, Res) :- 
	TWeekDay = RWeekDay,
	TLesson = RLesson,
	append(Buff, [schedule(Subject, Type, Teacher, Room, Group, TWeekDay, TLesson)], NewBuff),
	get_same_lessons(lesson(Subject, _, Type), [schedule(0, 0, Teacher, 0, Group, TWeekDay, TLesson)|TSchedTail], RSchedTail, RoomsSched, NewBuff, Res).

get_same_lessons(lesson(Subject, _, Type), [schedule(0, 0, Teacher, 0, Group, TWeekDay, TLesson)|TSchedTail], [schedule(0, 0, 0, Room, Group, RWeekDay, RLesson)|RSchedTail], RoomsSched, Buff, Res) :- 
	not(
		(TWeekDay = RWeekDay,
			TLesson = RLesson)),
	get_same_lessons(lesson(Subject, _, Type), [schedule(0, 0, Teacher, 0, Group, TWeekDay, TLesson)|TSchedTail], RSchedTail, RoomsSched, Buff, Res).


b(A, [X|Y], Z) :- b(A, [X|Y], [], Z).
b(A, [X], Buff, Z) :- append(A, [X], C), write_res(C).
b(A, [X|Y], Buff, Z) :- append(A, [X], C), write_res(C), b(A, Y, B, Z).

retract_old(schedule(subject(SubID, SubName), Type,  teacher(Tid, Tname), room(RoomNum, RoomCapacity, RoomType), group(GrNum, GrSize), WeekDay, Lesson)) :-
	retract(schedule(subject(SubID, SubName), Type,  teacher(Tid, Tname), room(RoomNum, RoomCapacity, RoomType), group(GrNum, GrSize), WeekDay, Lesson)),
	assert(schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson)).

retract_old(schedule(subject(SubID, SubName), Type,  teacher(Tid, Tname), room(RoomNum, RoomCapacity, RoomType), group(GrNum, GrSize), WeekDay, Lesson)) :-
	not(retract(schedule(subject(SubID, SubName), Type,  teacher(Tid, Tname), room(RoomNum, RoomCapacity, RoomType), group(GrNum, GrSize), WeekDay, Lesson))),
	schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson).

assert_new(schedule(subject(SubID, SubName), Type,  teacher(Tid, Tname), room(RoomNum, RoomCapacity, RoomType), group(GrNum, GrSize), WeekDay, Lesson)) :-
	retract(schedule(0, 0, 0, 0, group(GrNum, GrSize), WeekDay, Lesson)),
	assert(schedule(subject(SubID, SubName), Type,  teacher(Tid, Tname), room(RoomNum, RoomCapacity, RoomType), group(GrNum, GrSize), WeekDay, Lesson)).

get_variants_by_lesson(lesson(subject(SubID, SubName), group(GrNum, GrSize), Type), Res) :-
	get_teachers_by_subject(subject(SubID, SubName), Type, Teachers),
	get_rooms_by_type(Type, Rooms),
	get_freetime_in_schedule_by_group(group(GrNum, GrSize), Lessons),
	check_teachers_rooms_lessons(lesson(subject(SubID, SubName), group(GrNum, GrSize), Type), Teachers, Rooms, Lessons, Res).

pred_a([lesson(subject(SubID, SubName), group(GrNum, GrSize), Type)|LTail], Res) :-
	get_variants_by_lesson(lesson(subject(SubID, SubName), group(GrNum, GrSize), Type),
	[Sched|TailS]),
	assert_new(Sched),
	a(TailS, LTail, Sched, Res).

a([Sched], [Lesson], LastAsserted, Res) :-
	get_variants_by_lesson(Lesson, [SchedChecked|TailS]),
	length([SchedChecked|TailS], LenVars),
	LenVars > 0,
	get_filled_schedule(Filled, Deleted),
	b(Filled, [SchedChecked|TailS], FirstNew),
	write_res(FirstNew),
	assert_back(Deleted),
	retract_old(LastAsserted),

	assert_new(Sched),
	get_variants_by_lesson(Lesson, [SchedCheckedd|TailSS]),
	length([SchedCheckedd|TailSS], LenVars),
	LenVars > 0,
	get_filled_schedule(Filledd, Deletedd),
	b(Filledd, [SchedCheckedd|TailSS], SecondNew),
	write_res(SecondNew),
	assert_back(Deletedd),
	retract_old(Sched).

a([Sched|VarTail], [Lesson], LastAsserted, Res) :-
	get_variants_by_lesson(Lesson, [SchedChecked|TailS]),
	length([SchedChecked|TailS], LenVars),
	LenVars > 0,
	get_filled_schedule(Filled, Deleted),
	b(Filled, [SchedChecked|TailS], Ress),
	/*
	append(Res, Ress, NewRes),
	*/
	write_res(Ress),
	assert_back(Deleted),
	retract_old(LastAsserted),
	assert_new(Sched),
	a(VarTail, [Lesson], Sched, NewRes).

a([Sched|VarTail], [Lesson], LastAsserted, Res) :-
	get_variants_by_lesson(Lesson, [SchedChecked|TailS]),
	length([SchedChecked|TailS], LenVars),
	=<(LenVars, 0),
	retract_old(LastAsserted),
	assert_new(Sched),
	a(VarTail, [Lesson], Sched, Res).

a([Sched], [Lesson|LTail], LastAsserted, Res) :-
	get_variants_by_lesson(Lesson, [SchedChecked|TailS]),
	length([SchedChecked|TailS], LenVars),
	LenVars > 0,
	assert_new(SchedChecked),
	a(TailS, LTail, SchedChecked, Res),

	retract_old(SchedChecked),
	retract_old(LastAsserted),
	assert_new(Sched),
	get_variants_by_lesson(Lesson, [SchedChecked|TailS]),
	length([SchedChecked|TailS], LenVars),
	LenVars > 0,
	assert_new(SchedChecked),
	a(TailS, LTail, SchedChecked, Res).

a([Sched], [Lesson|LTail], LastAsserted, Res) :-
	get_variants_by_lesson(Lesson, [SchedChecked|TailS]),
	length([SchedChecked|TailS], LenVars),
	=<(LenVars, 0),

	retract_old(LastAsserted),
	assert_new(Sched),
	get_variants_by_lesson(Lesson, [SchedChecked|TailS]),
	length([SchedChecked|TailS], LenVars),
	LenVars > 0,
	assert_new(SchedChecked),
	a(TailS, LTail, SchedChecked, Res).

a([Sched], [Lesson|LTail], LastAsserted, Res) :-
	get_variants_by_lesson(Lesson, [SchedChecked|TailS]),
	length([SchedChecked|TailS], LenVars),
	LenVars > 0,
	assert_new(SchedChecked),
	a(TailS, LTail, SchedChecked, Res),

	retract_old(SchedChecked),
	retract_old(LastAsserted),
	assert_new(Sched),
	get_variants_by_lesson(Lesson, [SchedChecked|TailS]),
	length([SchedChecked|TailS], LenVars),
	=<(LenVars, 0),
	retract_old(Sched).

a([Sched], [Lesson|LTail], LastAsserted, Res) :-
	get_variants_by_lesson(Lesson, [SchedChecked|TailS]),
	length([SchedChecked|TailS], LenVars),
	=<(LenVars, 0),

	retract_old(LastAsserted),
	assert_new(Sched),
	get_variants_by_lesson(Lesson, [SchedChecked|TailS]),
	length([SchedChecked|TailS], LenVars),
	=<(LenVars, 0),
	retract_old(Sched).

a([Sched|VarTail], [Lesson|LTail], LastAsserted, Res) :-
	get_variants_by_lesson(Lesson, [SchedChecked|TailS]),
	length([SchedChecked|TailS], LenVars),
	LenVars > 0,
	assert_new(SchedChecked),
	a(TailS, LTail, SchedChecked, Res),
	retract_old(SchedChecked),
	retract_old(LastAsserted),
	assert_new(Sched),
	a(VarTail, [Lesson|LTail], Sched, Res).


a([Sched|VarTail], [Lesson|LTail], LastAsserted, Res) :-
	get_variants_by_lesson(Lesson, [SchedChecked|TailS]),
	length([SchedChecked|TailS], LenVars),
	=<(LenVars, 0),
	retract_old(LastAsserted),
	assert_new(Sched),
	a(VarTail, [Lesson|LTail], Sched, Res).


write_res(Res) :-
	working_directory(_, "D:/Projects/"),
	open("out.txt", append, Out),
    write(Out,Res),
    write(Out, "\n"),
    close(Out).

get_filled_schedule(Lessons, Deleted) :- findall(schedule(0, 0, 0, 0, group(GrNum, GrCup), WeekDay, Lesson), schedule(0, 0, 0, 0, group(GrNum, GrCup), WeekDay, Lesson), Deleted), retractall(schedule(0, 0, 0, 0, _, _, _)), findall(schedule(Subject, Type, Teacher, Room, group(GrNum, GrCup), WeekDay, Lesson), schedule(Subject, Type, Teacher, Room, group(GrNum, GrCup), WeekDay, Lesson), Lessons).

assert_back([Sched]) :- assert(Sched).
assert_back([Sched|SchedTail]) :- assert(Sched), assert_back(SchedTail).

