CREATE OR REPLACE  FUNCTION add_user (integer, text, text, text) RETURNS timestamp with time zone AS '
DECLARE
  id ALIAS FOR $1;
  name ALIAS FOR $2;
  first_name ALIAS FOR $3;
  last_name ALIAS FOR $4;
  right_now timestamp;

BEGIN
  right_now := ''now'';
  INSERT INTO public."user"(id, name, first_name, last_name)
  VALUES (id, name, first_name, last_name);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

select add_user(1, 'sergiubuhatel', 'Sergiu', 'Buhatel');
select add_user(2, 'tanvirislam', 'Tanvir', 'Islam');
select add_user(3, 'jazminromero', 'Jazmin', 'Romero');
select add_user(4, 'andrewschoenrock', 'Andrew', 'Schoenrock');
select add_user(5, 'admin', 'Admin', 'User');
select add_user(6, 'hanqingzhou', 'Hanqing', 'Zhou');
select add_user(7, 'geoffpinchbeck', 'Geoff', 'Pinchbeck');
select add_user(8, 'geoffpin', 'Geoff', 'Pinchbeck');

CREATE OR REPLACE  FUNCTION add_user_field (text, text, text, text) RETURNS timestamp with time zone AS '
DECLARE
  user_name ALIAS FOR $1;
  name ALIAS FOR $2;
  type ALIAS FOR $3;
  value ALIAS FOR $4;
  right_now timestamp;
  user_id integer;

BEGIN
  right_now := ''now'';

  user_id := (SELECT u.id FROM public."user" as u WHERE u.name=$1);

  INSERT INTO user_field(name, type, value, user_id)
  VALUES (name, type, value, user_id);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

select add_user_field('sergiubuhatel', 'student_id', 'text', '1234567');
select add_user_field('sergiubuhatel', 'first_language', 'text', 'Romanian');
select add_user_field('sergiubuhatel', 'email', 'text', 'sergiu.buhatel@gmail.com');
select add_user_field('sergiubuhatel', 'phone', 'text', '(613) 724-8815');

select add_user_field('tanvirislam', 'student_id', 'text', '7654321');
select add_user_field('tanvirislam', 'first_language', 'text', 'English');
select add_user_field('tanvirislam', 'email', 'text', 'tanvir.islam@carleton.com');
select add_user_field('tanvirislam', 'phone', 'text', '(613) 111-9999');

CREATE OR REPLACE  FUNCTION add_user_role (text, text) RETURNS timestamp with time zone AS '
DECLARE
  user_name ALIAS FOR $1;
  role_name ALIAS FOR $2;
  right_now timestamp;
  user_id integer;
  role_id integer;

BEGIN
  right_now := ''now'';

  user_id := (SELECT u.id FROM public."user" as u WHERE u.name=$1);
  role_id := (SELECT r.id FROM role as r WHERE r.name=$2);

  INSERT INTO user_role(user_id, role_id)
  VALUES (user_id, role_id);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

select add_user_role('admin', 'Administrator');
select add_user_role('sergiubuhatel', 'Administrator');
select add_user_role('tanvirislam', 'Administrator');
select add_user_role('jazminromero', 'Administrator');
select add_user_role('andrewschoenrock', 'Administrator');
select add_user_role('hanqingzhou', 'Administrator');
select add_user_role('geoffpinchbeck', 'Administrator');
select add_user_role('geoffpin', 'Administrator');