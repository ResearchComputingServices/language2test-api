INSERT INTO public."student_class"(id, name, display, term, "level", program, instructor_id, unremovable)
VALUES (1, 'level_1_class_1_fall', 'English 101 F', 'Fall 2020', 'Level 1', 'CS', 16, True);

INSERT INTO public."student_class"(id, name, display, term, "level", program, instructor_id, unremovable)
VALUES (2, 'level_1_class_1_winter', 'English 101 W', 'Winter 2021', 'Level 1', 'CS', 16, True);

INSERT INTO public."student_class"(id, name, display, term, "level", program, instructor_id, unremovable)
VALUES (3, 'level_1_class_1_spring', 'English 101 S', 'Spring 2021', 'Level 1', 'CS', 17, True);

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

select add_student_to_class('testtaker1', 'level_1_class_1_fall');
select add_student_to_class('testtaker2', 'level_1_class_1_fall');
select add_student_to_class('testtaker3', 'level_1_class_1_fall');


select add_student_to_class('testtaker2', 'level_1_class_1_winter');
select add_student_to_class('testtaker4', 'level_1_class_1_winter');
select add_student_to_class('testtaker5', 'level_1_class_1_winter');
select add_student_to_class('testtaker7', 'level_1_class_1_winter');

select add_student_to_class('testtaker1', 'level_1_class_1_spring');
select add_student_to_class('testtaker3', 'level_1_class_1_spring');
select add_student_to_class('testtaker6', 'level_1_class_1_spring');
select add_student_to_class('testtaker7', 'level_1_class_1_spring');
