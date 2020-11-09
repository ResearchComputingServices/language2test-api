INSERT INTO public."test_assignation"(id, test_id, start_datetime, end_datetime)
VALUES (1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '3 day');

INSERT INTO public."test_assignation"(id, test_id, start_datetime, end_datetime)
VALUES (2, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '3 day');

INSERT INTO public."test_assignation"(id, test_id, start_datetime, end_datetime)
VALUES (3, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '3 day');

CREATE OR REPLACE  FUNCTION add_student_class_to_test_assignation (text, integer) RETURNS timestamp with time zone AS '
DECLARE
  student_class_name ALIAS FOR $1;
  test_assignation_id ALIAS FOR $2;
  right_now timestamp;
  student_class_id integer;


BEGIN
  right_now := ''now'';

  student_class_id := (SELECT sc.id FROM student_class as sc WHERE sc.name=$1);

  INSERT INTO test_assignation_student_class(test_assignation_id, student_class_id)
  VALUES (test_assignation_id, student_class_id);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

select add_student_class_to_test_assignation('level_1_class_1_fall', 1);
select add_student_class_to_test_assignation('level_1_class_1_winter', 2);
select add_student_class_to_test_assignation('level_1_class_1_spring', 3);