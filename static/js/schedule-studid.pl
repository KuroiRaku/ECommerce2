team(['40122814', '4000228']).
student_info('40122814', 'John', 'Doe').
student_info('4000228', 'Jane', 'Doe').
takes_course('40122814', 'comp', '348', 'aa').
takes_course('40122814', 'comp', '348', 'aaae').
takes_course('4000228', 'comp', '348', 'ab').
takes_course('4000228', 'comp', '348', 'abaf').
takes_course('4000228', 'comp', '346', 'cc').
course_schedule('comp', '348', 'aa', 'mon', '1445', '1715').
course_schedule('comp', '348', 'aa', 'wed', '1445', '1715').
course_schedule('comp', '348', 'aaae', 'mon', '1345', '1405').
course_schedule('comp', '348', 'aaae', 'wed', '1345', '1405').
course_schedule('comp', '348', 'ab', 'tue', '1315', '1545').
course_schedule('comp', '348', 'ab', 'thu', '1315', '1545').
course_schedule('comp', '348', 'abaf', 'tue', '1615', '1705').
course_schedule('comp', '348', 'abaf', 'thu', '1615', '1705').
course_schedule('comp', '346', 'cc', 'tue', '1830', '2100').
course_schedule('comp', '346', 'cc', 'thu', '1830', '2100').

team(X), member(S, X),
findall(S, takes_course(S, _, _, _), LL),
length(LL, NN),
write(S), write(' has only taken '), write(NN),
write(' courses and tutorials in summer 2020.'), nl, fail.
