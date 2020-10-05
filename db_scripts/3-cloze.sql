CREATE OR REPLACE FUNCTION add_cloze_question (text, text, text, text, text, text, text, integer, integer) RETURNS timestamp with time zone AS '
DECLARE
  text ALIAS FOR $1;
  cloze_name ALIAS FOR $2;
  option_1_text ALIAS FOR $3;
  option_2_text ALIAS FOR $4;
  option_3_text ALIAS FOR $5;
  option_4_text ALIAS FOR $6;
  option_5_text ALIAS FOR $7;
  correct ALIAS FOR $8;
  difficulty ALIAS FOR $9;
  right_now timestamp;
  cloze_question_id integer;
  cloze_id integer;

BEGIN
  right_now := ''now'';

  cloze_question_id := (SELECT COALESCE(MAX(id) + 1, 1) FROM cloze_question);

  cloze_id := (SELECT cloze.id FROM cloze WHERE cloze.name=$2);

  INSERT INTO cloze_question(id, text, cloze_id, correct, difficulty)
  VALUES(cloze_question_id, text, cloze_id, correct, difficulty);

  INSERT INTO cloze_question_option(text, cloze_question_id)
  VALUES (option_1_text, cloze_question_id);

  INSERT INTO cloze_question_option(text, cloze_question_id)
  VALUES (option_2_text, cloze_question_id);

  INSERT INTO cloze_question_option(text, cloze_question_id)
  VALUES (option_3_text, cloze_question_id);

  INSERT INTO cloze_question_option(text, cloze_question_id)
  VALUES (option_4_text, cloze_question_id);

  INSERT INTO cloze_question_option(text, cloze_question_id)
  VALUES (option_5_text, cloze_question_id);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

INSERT INTO public."cloze"(name, text, type, filename, test_category_id, time_limit, immutable, unremovable)
VALUES ('Cloze-1', 'Can we see *that* the earth is a globe? Yes, we can, when we watch a ship that sails out to sea. If we watch closely, we see that the ship begins *to disappear* . The bottom of the ship disappears first, and then the ship seems to sink lower and lower, *until* we can only see the top of the ship, and then we see nothing at all. What is hiding the ship from us? It is the earth. Stick a pin most of the way into an orange, and *passionately* turn the orange away from you. You will see the pin disappear, *similar to* a ship does on the earth.
', 'text', '', 3, 600, False, True);

select add_cloze_question('that',
                       'Cloze-1',
                       'if',
                       'where',
                       'that',
                       'whether',
                       'when',
                       3, 1);
select add_cloze_question('to disappear',
                       'Cloze-1',
                       'being disappeared',
                       'to be disappeared',
                       'to have disappeared',
                       'to disappear',
                       'having disappeared',
                       4, 1);

select add_cloze_question('until',
                       'Cloze-1',
                       'until',
                       'since',
                       'after',
                       'by the time',
                       'unless',
                       1, 1);

select add_cloze_question('slowly',
                       'Cloze-1',
                       'reluctantly',
                       'accidentally',
                       'slowly',
                       'passionately',
                       'carefully',
                       3, 1);

select add_cloze_question('just as',
                       'Cloze-1',
                       'the same',
                       'alike',
                       'just as',
                       'by the way',
                       'similar to',
                       3, 1);

/* Correct */
INSERT INTO public."cloze_question_correctly_typed"(id, text, cloze_question_id)
VALUES (1, 'that', 1);

INSERT INTO public."cloze_question_correctly_typed"(id, text, cloze_question_id)
VALUES (2, 'as', 1);


/* Incorrect */
INSERT INTO public."cloze_question_incorrectly_typed"(id, text, cloze_question_id)
VALUES (1, 'if', 1);

INSERT INTO public."cloze_question_incorrectly_typed"(id, text, cloze_question_id)
VALUES (2, 'where', 1);

INSERT INTO public."cloze_question_incorrectly_typed"(id, text, cloze_question_id)
VALUES (3, 'whether', 1);

INSERT INTO public."cloze_question_incorrectly_typed"(id, text, cloze_question_id)
VALUES (4, 'when', 1);


/* Pending */
INSERT INTO public."cloze_question_pending_typed"(id, text, cloze_question_id)
VALUES (1, 'what if', 1);

INSERT INTO public."cloze_question_pending_typed"(id, text, cloze_question_id)
VALUES (2, 'where from', 1);

INSERT INTO public."cloze_question_pending_typed"(id, text, cloze_question_id)
VALUES (3, 'from', 1);

INSERT INTO public."cloze_question_pending_typed"(id, text, cloze_question_id)
VALUES (4, 'to', 1);

INSERT INTO public."cloze_question_pending_typed"(id, text, cloze_question_id)
VALUES (5, 'as it is', 1);