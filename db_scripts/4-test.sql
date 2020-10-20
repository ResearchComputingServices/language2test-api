INSERT INTO public."test"(id, name, immutable, unremovable)
VALUES (1, 'Beginner', False, True);

INSERT INTO public."test"(id, name, immutable, unremovable)
VALUES (2, 'Intermediate', False, True);

INSERT INTO public."test"(id, name, immutable, unremovable)
VALUES (3, 'Advanced', False, True);

CREATE OR REPLACE  FUNCTION add_test_vocabulary (text, text) RETURNS timestamp with time zone AS '
DECLARE
  test_name ALIAS FOR $1;
  vocabulary_word ALIAS FOR $2;
  right_now timestamp;
  test_id integer;
  vocabulary_id integer;

BEGIN
  right_now := ''now'';

  test_id := (SELECT t.id FROM test as t WHERE t.name=$1);
  vocabulary_id := (SELECT v.id FROM vocabulary as v WHERE v.word=$2);

  INSERT INTO test_vocabulary(test_id, vocabulary_id)
  VALUES (test_id, vocabulary_id);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

select add_test_vocabulary('Advanced', 'keen');
select add_test_vocabulary('Advanced', 'ratiocination');
select add_test_vocabulary('Advanced', 'proclivity');
select add_test_vocabulary('Advanced', 'inscrutable');
select add_test_vocabulary('Advanced', 'progenitor');
select add_test_vocabulary('Advanced', 'emaciated');
select add_test_vocabulary('Advanced', 'entice');
select add_test_vocabulary('Advanced', 'privy');
select add_test_vocabulary('Advanced', 'dupe');
select add_test_vocabulary('Advanced', 'innocuous');
select add_test_vocabulary('Intermediate', 'likelihood');
select add_test_vocabulary('Intermediate', 'reject');
select add_test_vocabulary('Intermediate', 'pick');
select add_test_vocabulary('Intermediate', 'energy');
select add_test_vocabulary('Intermediate', 'adjourn');
select add_test_vocabulary('Intermediate', 'advocate');
select add_test_vocabulary('Intermediate', 'value');
select add_test_vocabulary('Intermediate', 'mutual');
select add_test_vocabulary('Intermediate', 'result');
select add_test_vocabulary('Intermediate', 'dawn');
select add_test_vocabulary('Beginner', 'instructor');
select add_test_vocabulary('Beginner', 'forbid');
select add_test_vocabulary('Beginner', 'composition');
select add_test_vocabulary('Beginner', 'caution');
select add_test_vocabulary('Beginner', 'monotonous');
select add_test_vocabulary('Beginner', 'settle down');
select add_test_vocabulary('Beginner', 'fix');
select add_test_vocabulary('Beginner', 'scares');
select add_test_vocabulary('Beginner', 'potential');
select add_test_vocabulary('Beginner', 'ceremony');

CREATE OR REPLACE  FUNCTION add_test_rc (text, text) RETURNS timestamp with time zone AS '
DECLARE
  test_name ALIAS FOR $1;
  rc_name ALIAS FOR $2;
  right_now timestamp;
  test_id integer;
  rc_id integer;

BEGIN
  right_now := ''now'';

  test_id := (SELECT t.id FROM test as t WHERE t.name=$1);
  rc_id := (SELECT rc.id FROM rc WHERE rc.name=$2);

  INSERT INTO test_rc(test_id, rc_id)
  VALUES (test_id, rc_id);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

select add_test_rc('Beginner', 'RC-1');
select add_test_rc('Intermediate', 'RC-1');
select add_test_rc('Advanced', 'RC-1');

CREATE OR REPLACE  FUNCTION add_test_cloze (text, text) RETURNS timestamp with time zone AS '
DECLARE
  test_name ALIAS FOR $1;
  cloze_name ALIAS FOR $2;
  right_now timestamp;
  test_id integer;
  cloze_id integer;

BEGIN
  right_now := ''now'';

  test_id := (SELECT t.id FROM test as t WHERE t.name=$1);
  cloze_id := (SELECT cloze.id FROM cloze WHERE cloze.name=$2);

  INSERT INTO test_cloze(test_id, cloze_id)
  VALUES (test_id, cloze_id);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

select add_test_cloze('Beginner', 'Cloze-1');
select add_test_cloze('Intermediate', 'Cloze-1');
select add_test_cloze('Advanced', 'Cloze-1');

CREATE OR REPLACE  FUNCTION add_test_writing (text, text) RETURNS timestamp with time zone AS '
DECLARE
  test_name ALIAS FOR $1;
  writing_name ALIAS FOR $2;
  right_now timestamp;
  test_id integer;
  writing_id integer;

BEGIN
  right_now := ''now'';

  test_id := (SELECT t.id FROM test as t WHERE t.name=$1);
  writing_id := (SELECT w.id FROM writing as w WHERE w.name=$2);

  INSERT INTO test_writing(test_id, writing_id)
  VALUES (test_id, writing_id);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

select add_test_writing('Advanced', 'Weather');
select add_test_writing('Advanced', 'Football');

CREATE OR REPLACE  FUNCTION add_test_user_field_category (text, text) RETURNS timestamp with time zone AS '
DECLARE
  test_name ALIAS FOR $1;
  user_field_category_name ALIAS FOR $2;
  right_now timestamp;
  test_id integer;
  user_field_category_id integer;

BEGIN
  right_now := ''now'';

  test_id := (SELECT t.id FROM test as t WHERE t.name=$1);
  user_field_category_id := (SELECT ufc.id FROM user_field_category as ufc WHERE ufc.name=$2);

  INSERT INTO test_user_field_category(test_id, user_field_category_id)
  VALUES (test_id, user_field_category_id);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

select add_test_user_field_category('Beginner', 'student_id');
select add_test_user_field_category('Beginner', 'first_language');
select add_test_user_field_category('Beginner', 'email');
select add_test_user_field_category('Beginner', 'phone');
select add_test_user_field_category('Beginner', 'address');
select add_test_user_field_category('Beginner', 'education');

select add_test_user_field_category('Intermediate', 'student_id');
select add_test_user_field_category('Intermediate', 'first_language');
select add_test_user_field_category('Intermediate', 'email');
select add_test_user_field_category('Intermediate', 'phone');
select add_test_user_field_category('Intermediate', 'address');
select add_test_user_field_category('Intermediate', 'education');

select add_test_user_field_category('Advanced', 'student_id');
select add_test_user_field_category('Advanced', 'first_language');
select add_test_user_field_category('Advanced', 'email');
select add_test_user_field_category('Advanced', 'phone');
select add_test_user_field_category('Advanced', 'address');
select add_test_user_field_category('Advanced', 'education');

CREATE OR REPLACE  FUNCTION add_mandatory_test_user_field_category (text, text) RETURNS timestamp with time zone AS '
DECLARE
  test_name ALIAS FOR $1;
  user_field_category_name ALIAS FOR $2;
  right_now timestamp;
  test_id integer;
  user_field_category_id integer;

BEGIN
  right_now := ''now'';

  test_id := (SELECT t.id FROM test as t WHERE t.name=$1);
  user_field_category_id := (SELECT ufc.id FROM user_field_category as ufc WHERE ufc.name=$2);

  INSERT INTO mandatory_test_user_field_category(test_id, user_field_category_id)
  VALUES (test_id, user_field_category_id);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

select add_mandatory_test_user_field_category('Beginner', 'student_id');
select add_mandatory_test_user_field_category('Intermediate', 'student_id');
select add_mandatory_test_user_field_category('Advanced', 'student_id');

CREATE OR REPLACE  FUNCTION add_student_class (text, text) RETURNS timestamp with time zone AS '
DECLARE
  test_name ALIAS FOR $1;
  student_class_name ALIAS FOR $2;
  right_now timestamp;
  test_id integer;
  student_class_id integer;

BEGIN
  right_now := ''now'';

  test_id := (SELECT t.id FROM test as t WHERE t.name=$1);
  student_class_id := (SELECT sc.id FROM student_class as sc WHERE sc.name=$2);

  INSERT INTO test_student_class(test_id, student_class_id)
  VALUES (test_id, student_class_id);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

select add_student_class('Beginner', 'level_1_class_1_fall');
select add_student_class('Beginner', 'level_1_class_2_fall');
select add_student_class('Intermediate', 'level_1_class_1_fall');
select add_student_class('Advanced', 'level_1_class_2_fall');
