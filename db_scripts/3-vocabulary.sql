CREATE OR REPLACE  FUNCTION add_vocabulary (text, text, integer, integer, text, text, text, text) RETURNS timestamp with time zone AS '
DECLARE
  word ALIAS FOR $1;
  type ALIAS FOR $2;
  difficulty ALIAS FOR $3;
  correct ALIAS FOR $4;
  option_1 ALIAS FOR $5;
  option_2 ALIAS FOR $6;
  option_3 ALIAS FOR $7;
  option_4 ALIAS FOR $8;
  right_now timestamp;
  vocabulary_id integer;

BEGIN
  right_now := ''now'';
  INSERT INTO vocabulary(word, type, difficulty, correct, time_limit, test_category_id)
  VALUES(word, type, difficulty, correct, 20, 1);

  vocabulary_id := (SELECT v.id FROM vocabulary as v WHERE v.word=$1);

  INSERT INTO vocabulary_option(text, vocabulary_id)
  VALUES (option_1, vocabulary_id);

  INSERT INTO vocabulary_option(text, vocabulary_id)
  VALUES (option_2, vocabulary_id);

  INSERT INTO vocabulary_option(text, vocabulary_id)
  VALUES (option_3, vocabulary_id);

  INSERT INTO vocabulary_option(text, vocabulary_id)
  VALUES (option_4, vocabulary_id);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

select add_vocabulary('keen', 'synonym', 5, 3, 'broken', 'fluffy', 'sharp', 'thin');
select add_vocabulary('ratiocination', 'synonym', 10, 1, 'logic', 'kindness', 'envy', 'stupidity');
select add_vocabulary('proclivity', 'synonym', 10, 3, 'rumor', 'load', 'tendency', 'damage');
select add_vocabulary('inscrutable', 'synonym', 10, 1, 'mysterious', 'invisible', 'fixed', 'quiet');
select add_vocabulary('progenitor', 'synonym', 10, 3, 'flavour', 'bias', 'ancestor', 'setback');
select add_vocabulary('emaciated', 'synonym', 10, 4, 'clammy', 'active', 'nauseating', 'scrawny');
select add_vocabulary('entice', 'synonym', 10, 2, 'fight', 'tempt', 'slip', 'relax');
select add_vocabulary('privy', 'synonym', 10, 3, 'obtainable', 'absent', 'admitted', 'original');
select add_vocabulary('dupe', 'synonym', 10, 3, 'lock', 'defeat', 'trick', 'decide');
select add_vocabulary('innocuous', 'synonym', 10, 1, 'harmless', 'unavailable', 'sudden', 'upbeat');
select add_vocabulary('likelihood', 'synonym', 4, 4, 'enjoyment', 'loyalty', 'childhood', 'probability');
select add_vocabulary('reject', 'synonym', 2, 3, 'check on', 'cut down', 'turn around', 'turn down');
select add_vocabulary('pick', 'synonym', 1, 3, 'help', 'send', 'choose', 'receive');
select add_vocabulary('energy', 'synonym', 2, 3, 'activity', 'wound', 'power', 'base');
select add_vocabulary('adjourn', 'synonym', 6, 2, 'upgrade', 'end', 'return', 'promote');
select add_vocabulary('advocate', 'synonym', 3, 3, 'opponent', 'trainer', 'defender', 'judge');
select add_vocabulary('value', 'synonym', 1, 2, 'exchange', 'importance', 'wave', 'opinion');
select add_vocabulary('mutual', 'synonym', 1, 3, 'forced', 'prepared', 'shared', 'displayed');
select add_vocabulary('result', 'synonym', 1, 4, 'refuse', 'reply', 'success', 'effect');
select add_vocabulary('dawn', 'synonym', 1, 2, 'sudden movement', 'early morning', 'late evening', 'quick thought');
select add_vocabulary('instructor', 'synonym', 1, 2, 'nurse', 'teacher', 'farmer', 'builder');
select add_vocabulary('forbid', 'synonym', 3, 4, 'dare', 'continue', 'cease', 'prohibit');
select add_vocabulary('composition', 'synonym', 7, 4, 'notebook', 'diagram', 'board', 'essay');
select add_vocabulary('caution', 'synonym', 2, 2, 'security deposit', 'careful behavior', 'brief introduction', 'strong prospect');
select add_vocabulary('monotonous', 'synonym', 1, 4, 'colorful', 'magical', 'indirect', 'boring');
select add_vocabulary('settle down', 'synonym', 3, 1, 'become calm', 'descend', 'step over', 'swallow');
select add_vocabulary('fix', 'synonym', 3, 2, 'keep', 'repair', 'introduce', 'circle around');
select add_vocabulary('scares', 'synonym', 1, 3, 'elegant and polite', 'terrified', 'rare', 'raw');
select add_vocabulary('potential', 'synonym', 6, 4, 'patterns', 'standards', 'model', 'possibilities');
select add_vocabulary('ceremony', 'synonym', 2, 1, 'formal event', 'round surface', 'part of the brain', 'bank account');

