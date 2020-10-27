INSERT INTO public."student_class"(id, name, display, term, "level", program, instructor_id, unremovable)
VALUES (1, 'level_1_class_1_fall', 'English 101', 'Fall 2020', 'Level 1', 'CS', 1, True);

INSERT INTO public."student_class"(id, name, display, term, "level", program, instructor_id, unremovable)
VALUES (2, 'level_1_class_1_winter', 'English 101', 'Winter 2021', 'Level 1', 'CS', 1, True);

INSERT INTO public."student_class"(id, name, display, term, "level", program, instructor_id, unremovable)
VALUES (3, 'level_1_class_1_spring', 'English 101', 'Spring 2021', 'Level 1', 'CS', 1, True);

INSERT INTO public."student_class"(id, name, display, term, "level", program, instructor_id, unremovable)
VALUES (4, 'level_1_class_1_summer', 'English 101', 'Spring 2021', 'Level 1', 'CS', 1, False);

INSERT INTO public."student_class"(id, name, display, term, "level", program, instructor_id, unremovable)
VALUES (5, 'level_1_class_2_fall', 'English 102', 'Fall 2020', 'Level 2', 'CS', 2, False);

INSERT INTO public."student_class"(id, name, display, term, "level", program, instructor_id, unremovable)
VALUES (6, 'level_1_class_2_winter', 'English 102', 'Winter 2021', 'Level 2', 'CS', 2, False);

CREATE OR REPLACE  FUNCTION add_student_to_class (text, text) RETURNS timestamp with time zone AS '
DECLARE
  student_name ALIAS FOR $1;
  student_class_name ALIAS FOR $2;
  right_now timestamp;
  student_class_id integer;
  student_id integer;

BEGIN
  right_now := ''now'';

  student_id := (SELECT u.id FROM public."user" as u WHERE u.name=$1);
  student_class_id := (SELECT sc.id FROM student_class as sc WHERE sc.name=$2);

  INSERT INTO student_student_class(student_id, student_class_id)
  VALUES (student_id, student_class_id);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

select add_student_to_class('sergiubuhatel', 'level_1_class_1_fall');
select add_student_to_class('tanvirislam', 'level_1_class_1_fall');
select add_student_to_class('jazminromero', 'level_1_class_1_fall');
select add_student_to_class('andrewschoenrock', 'level_1_class_1_fall');
select add_student_to_class('hanqingzhou', 'level_1_class_1_fall');

select add_student_to_class('sergiubuhatel', 'level_1_class_1_winter');
select add_student_to_class('tanvirislam', 'level_1_class_1_winter');
select add_student_to_class('jazminromero', 'level_1_class_1_winter');
select add_student_to_class('andrewschoenrock', 'level_1_class_1_winter');
select add_student_to_class('hanqingzhou', 'level_1_class_1_winter');