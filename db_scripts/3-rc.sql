CREATE OR REPLACE FUNCTION add_rc_question (text, text, text, text, text, text, integer, integer) RETURNS timestamp with time zone AS '
DECLARE
  text ALIAS FOR $1;
  rc_name ALIAS FOR $2;
  option_1_text ALIAS FOR $3;
  option_2_text ALIAS FOR $4;
  option_3_text ALIAS FOR $5;
  option_4_text ALIAS FOR $6;
  correct ALIAS FOR $7;
  difficulty ALIAS FOR $8;
  right_now timestamp;
  rc_question_id integer;
  rc_id integer;


BEGIN
  right_now := ''now'';

  rc_question_id := (SELECT COALESCE(MAX(id) + 1, 1) FROM rc_question);

  rc_id := (SELECT rc.id FROM rc WHERE rc.name=$2);

  INSERT INTO rc_question(id, text, rc_id, correct, difficulty)
  VALUES(rc_question_id, text, rc_id, correct, difficulty);

  INSERT INTO rc_question_option(text, rc_question_id)
  VALUES (option_1_text, rc_question_id);

  INSERT INTO rc_question_option(text, rc_question_id)
  VALUES (option_2_text, rc_question_id);

  INSERT INTO rc_question_option(text, rc_question_id)
  VALUES (option_3_text, rc_question_id);

  INSERT INTO rc_question_option(text, rc_question_id)
  VALUES (option_4_text, rc_question_id);

  RETURN right_now;
END;
' LANGUAGE 'plpgsql';

INSERT INTO public."rc"(name, text, type, filename, test_category_id, time_limit)
VALUES ('RC-1', 'Deep in the Sierra Nevada, the famous General Grant giant sequoia tree is suffering its loss of stature in silence. What once was the world''s No. 2 biggest tree has been supplanted thanks to the most comprehensive measurements taken of the largest living things on Earth.


The new No. 2 is The President, a 54,000-cubic-foot gargantuan not far from the Grant in Sequoia National Park. After 3,240 years, the giant sequoia still is growing wider at a consistent rate, which may be what most surprised the scientists examining how the sequoias and coastal redwoods will be affected by climate change and whether these trees have a role to play in combating it.


"I consider it to be the greatest tree in all of the mountains of the world," said Stephen Sillett, a redwood researcher whose team from Humboldt State University is seeking to mathematically assess the potential of California''s iconic trees to absorb planet-warming carbon dioxide.


The researchers are a part of the 10-year Redwoods and Climate Change Initiative funded by the Save the Redwoods League in San Francisco. The measurements of The President, reported in the current National Geographic, dispelled the previous notion that the big trees grow more slowly in old age.



It means, the experts say, the amount of carbon dioxide they absorb during photosynthesis continues to increase over their lifetimes.


In addition to painstaking measurements of every branch and twig, the team took 15 half-centimeter-wide core samples of The President to determine its growth rate, which they learned was stunted in the abnormally cold year of 1580 when temperatures in the Sierra hovered near freezing even in the summer and the trees remained dormant.


But that was an anomaly, Sillett said. The President adds about one cubic meter of wood a year during its short six-month growing season, making it one of the fastest-growing trees in the world. Its 2 billion leaves are thought to be the most of any tree on the planet, which would also make it one of the most efficient at transforming carbon dioxide into nourishing sugars during photosynthesis.


"We''re not going to save the world with any one strategy, but part of the value of these great trees is this contribution and we''re trying to get a handle on the math behind that," Sillett said.


After the equivalent of 32 working days dangling from ropes in The President, Sillett''s team is closer to having a mathematical equation to determine its carbon conversion potential, as it has done with some less famous coastal redwoods. The team has analyzed a representative sample that can be used to model the capacity of the state''s signature trees.


More immediately, however, the new measurements could lead to a changing of the guard in the land of giant sequoias. The park would have to update signs and brochures - and someone is going to have to correct the Wikipedia entry for "List of largest giant sequoias," which still has The President at No. 3.


Now at 93 feet in circumference and with 45,000 cubic feet of trunk volume and another 9,000 cubic feet in its branches, the tree named for President Warren G. Harding is about 15 percent larger than Grant, also known as America''s Christmas Tree. Sliced into one-foot by one-foot cubes, The President would cover a football field.


Giant sequoias grow so big and for so long because their wood is resistant to the pests and disease that dwarf the lifespan of other trees, and their thick bark makes them impervious to fast-moving fire.


It''s that resiliency that makes sequoias and their taller coastal redwood cousin worthy of intensive protections and even candidates for cultivation to pull carbon from an increasingly warming atmosphere, Sillett said. Unlike white firs, which easily die and decay to send decomposing carbon back into the air, rot-resistant redwoods stay solid for hundreds of years after they fall.


Though sequoias are native to California, early settlers traveled with seedlings back to the British Isles and New Zealand, where a 15-foot diameter sequoia that is the world''s biggest planted tree took root in 1850. Part of Sillett''s studies involves modeling the potential growth rate of cultivated sequoia forests to determine over time how much carbon sequestering might increase.


All of that led him to a spot 7,000 feet high in the Sierra and to The President, which he calls "the ultimate example of a giant sequoia." Compared to the other giants whose silhouettes are bedraggled by lightning strikes, The President''s crown is large with burly branches that are themselves as large as tree trunks.


The world''s biggest tree is still the nearby General Sherman with about 2,000 cubic feet more volume than the President, but to Sillett it''s not a contest.


"They''re all superlative in their own way," Sillett said.
', 'text', '', 2, 600);

select add_rc_question('The word "supplanted" in paragraph 1',
                       'RC-1',
                       'inquisitive',
                       'Has a double-meaning both as a pun on the topic of plants and a literal meaning of "to replace"',
                       'Is a synonym for "to plant again"',
                       'Has the same meaning as "to plant," with extra emphasis',
                       1,
                       1);

select add_rc_question('One common myth about trees that The President helps disprove is',
                       'RC-1',
                       'That giant sequoias are more resilient than other tree species',
                       'That old trees are as productive at photosynthesis as younger ones',
                       'That only giant sequoias may be named after historical figures',
                       'That large trees grow more slowly as they age',
                       3,
                       1);

select add_rc_question('What is the primary benefit that Sillett and other researchers suggest that giant sequoias may have?',
                       'RC-1',
                       'Their natural beauty can have health benefits for those who travel to wildlife preserves to see them',
                       'They represent centuries of natural history that no other living things do',
                       'Because of their size, they can process more carbon dioxide than other trees, which can have significant benefits for the atmosphere',
                       'Their resilient bark may have eventual uses in human medicine.',
                       2,
                       1);

select add_rc_question('The giant sequoias are compared to white firs to demonstrate that?',
                       'RC-1',
                       'Even when the sequoias fall, they do not decay and so send less carbon into the air',
                       'White firs are more plentiful because they grow and decay more quickly than sequoias',
                       'The giant sequoias are completely resistant to death',
                       'White firs are essential because when they decompose they emit necessary nutrients',
                       3,
                       1);

select add_rc_question('The President has grown every year EXCEPT',
                       'RC-1',
                       '1850',
                       '2012',
                       '1580',
                       'The President has grown every year of its life',
                       2,
                       1);

select add_rc_question('All of the following contribute to the lifespan of the giant sequoia EXCEPT',
                       'RC-1',
                       'They are resistant to diseases that can affect other tree species',
                       'Their size makes them less vulnerable to animal attacks',
                       'They are resistant to pests that commonly inhabit trees',
                       'Their thick bark protects them from wildfires.',
                       1,
                       1);

select add_rc_question('The term "changing of the guard" in Paragraph 10 means',
                       'RC-1',
                       'The size rankings of various large sequoias is being reevaluated',
                       'Human security will be employed to protect these valuable trees',
                       'Wildlife parks will bring in new equipment to ensure the safety of the trees',
                       'A new schedule of shifts will be made for studying the trees',
                       1,
                       1);

select add_rc_question('What does the term "cultivated sequoia forests" in Paragraph 14 imply?',
                       'RC-1',
                       'Current sequoia reserves will be altered to grow in particular patterns',
                       'That sequoias may be specially grown in the future for the sole purpose of filtering carbon from the air',
                       'New forests may be grown globally to promote the beauty of the species',
                       'Wildlife parks will make more of an effort in the future to direct visitors to the sequoia forests',
                       1,
                       1);

select add_rc_question('Giant sequoias are native to California, but can also be found in',
                       'RC-1',
                       'New Zealand',
                       'France',
                       'South America',
                       'Australia',
                       1,
                       1);

select add_rc_question('In the final sentence, the word "superlative" is closest in meaning to',
                       'RC-1',
                       'Best of a species',
                       'Most beautiful',
                       'The winner of a contest',
                       'Having individual, unique merit',
                       3,
                       1);


