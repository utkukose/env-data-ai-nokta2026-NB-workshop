# Workshop guide

This guide is the run sheet for the two-hour session *AI-Based Environmental Data Analysis and Interpretation* of the NOKTA project (ÜNİDES 2026) on 20 November 2026. A Turkish version is in [WORKSHOP_GUIDE.tr.md](WORKSHOP_GUIDE.tr.md). Times are counted from the start of the session, so the sheet fits any starting hour.

The whole session runs from the workshop site, https://utkukose.github.io/env-data-ai-nokta2026-NB-workshop/ (Turkish: `/tr/`). Every part follows the same rhythm. A question comes first, the page then reveals the answer with an animation or a 3D scene, and an orange box opens the matching section of the Colab notebook. The NOKTA Lab closes the session.

## Before the session

On the day before, all seven pages should be opened once on the presenting laptop and once on a phone, in both languages. The 3D scenes need WebGL. On an old projector laptop, the night view (key `T`) and a smaller browser window keep the scenes smooth. The Colab notebook should also be run once from top to bottom. It finishes in about a minute and confirms that the data can be downloaded from GitHub.

The debrief of the NOKTA Lab is built from the answers and steps recorded in the browser that shows it, so a rehearsal leaves its own answers behind. About fifteen minutes before the start, the presenter opens the Debrief tab of the NOKTA Lab and presses *Start a new session*, which clears the earlier records. During the session the presenter then enters the answer of the room in each prediction question, so that the debrief at the end describes this session. The following message can be shared in the chat or on the first slide:

> Workshop site, no installation needed: https://utkukose.github.io/env-data-ai-nokta2026-NB-workshop/tr/
> Colab notebook (Turkish): Orange buttons on every page
> English site: Same address without /tr/ · Repository: https://github.com/utkukose/env-data-ai-nokta2026-NB-workshop

## Presenter controls

On every page the right and left arrow keys move to the next or previous station, and `]` and `[` move to the next or previous part. `T` switches between the paper view and the night view, `F` toggles full screen, `L` switches between English and Turkish, `B` opens a five-minute break with a countdown and `?` lists the keys. Answers and results are kept only in the browser in use, and they feed the debrief of the NOKTA Lab.

## Run sheet

| Time | Block | On screen | Participants |
|---|---|---|---|
| 0:00 | Opening: Measure → Analyze → Share → Turn into action | Start page, the 3D campus twin | open the site and the notebook |
| 0:08 | Part 1 cold open: Which point has the highest PM2.5? | `part1.html`, station 1, play the round | answer, then watch the replay |
| 0:13 | Ten channels · the pressure gap between campuses | station 2 | answer the pressure question |
| 0:16 | The data doctor: Warm-up, frozen CO₂, spikes, missing is not zero | station 3 | answer, then switch visits and channels |
| 0:22 | Three stations, one story · humid air | stations 4 and 5 | align the stations, move the humidity slider |
| 0:26 | The cleaning in code | notebook, Section 1 | run Sections 0 and 1 |
| 0:30 | Part 2 cold open: The last stop looks warm | `part2.html`, station 1 | answer, then step through the rounds |
| 0:38 | Typical values · related or caused? | stations 2 and 3 | answer, toggle the means and the groups |
| 0:45 | Wetter or only colder? | station 4 | move the dew point sliders |
| 0:48 | The fair table in code | notebook, Section 2 | run Section 2, try Exercise 2.A |
| 0:52 | Break | key `B` | answer the question on the break screen |
| 0:57 | Part 3 cold open: How many kinds of place? | `part3.html`, the 3D cloud | answer, color by point type |
| 1:03 | k-means step by step, J and the silhouette | station 2, buttons under the scene | place, assign, move, run |
| 1:09 | Six channels, three axes | station 3 | answer, switch to the components |
| 1:12 | Name the groups · clustering in code | station 4, notebook Section 3 | name the four groups |
| 1:17 | Part 4 cold open: An honest test | `part4.html`, station 1 | answer, compare the two splits |
| 1:22 | What does it rely on? | station 2 | answer, read the importances |
| 1:26 | What if? Fly over the model | stations 3 and 4 | try the presets, rotate the surface |
| 1:33 | The model in code | notebook, Section 4 | run Section 4, try the sliders |
| 1:37 | Part 5 cold open: Spot the errors | `part5.html`, station 1 | mark the sentences, then check |
| 1:44 | A safe prompt · how strong is the claim? | stations 2 and 3 | copy the prompt, classify the claims |
| 1:50 | The solution card | station 4 | write one card per team |
| 1:55 | Debrief, field practice and questions | `lab.html#debrief`, then `lab.html#field` | open the debrief, note the field tasks |

## What to explain in each block

The run sheet gives the order and the timing. The paragraphs below give the message that each block should leave with the participants, together with the numbers of the synthetic data that support it.

**Opening, 0:00 to 0:08.** The opening explains how the data were collected before any analysis starts. On each campus one portable station visits six point types, and each visit lasts 15 minutes. Round 2 repeats the route one week later at the same clock times, but in reverse order from P6 back to P1. The measurement plan on the start page shows this as a table, and it is worth keeping on the screen for a minute. The participants should leave the opening knowing what a visit, a round and the reference point are, because every later comparison rests on these three ideas.

**Part 1, 0:08 to 0:30.** A reading becomes data only after its quality has been checked. The replay shows how the values build up during a round. The pressure question shows that the gap of about 115 hPa between Campus A and Campus C comes mostly from altitude, so pressure describes the location of a campus rather than its air quality. At the data doctor station each fault has its own signature: A drift in the first two minutes after a move, an isolated spike in one channel, the flat line of a frozen sensor and the gaps left by the logger. The gap example deserves a moment. Six empty readings written as zero lower the mean temperature from 10.37 °C to 7.54 °C. The detector catches almost all planted faults but misses two PM2.5 glitches inside real plumes, so the flagged readings still need a human look. Isolation Forest, the first AI method of the session, then gives a second opinion without rules. It flags 65 unusual readings, but most of them are real smoke and exhaust plumes, which shows that unusual does not mean wrong. Part 1 ends with the table of 36 visits × 13 minutes = 468 clean minutes, and every later number comes from this table.

**Part 2, 0:30 to 0:52.** A fair comparison has to control the clock, the outliers and the hidden groups. In Round 1 on Campus A the green area reads 13.9 °C and the road 13.3 °C, but the green area was measured last in a warming morning. Over both rounds the green area is 1.1 °C cooler than the reference point, and the road is 0.6 °C warmer. The box plots show that near the busy entrance short smoke plumes lift the mean above the median. Over all minutes, temperature and pressure correlate with r = +0.81, yet inside each campus and round the correlation lies between −0.41 and −0.64. The campus is the hidden third factor. The dew point station closes the part by separating the water content of the air from its temperature.

**Part 3, 0:57 to 1:17.** Unsupervised learning proposes groups, and people name and check them. k-means places centers, assigns each minute to the nearest center and moves the centers until nothing changes. With four groups it stops after four iterations, with J = 363.0 and a silhouette of 0.499. The silhouette hardly changes between three and six groups, so the choice of four is a decision of the analyst that has to be explained. PCA keeps about 86 % of the variation of six channels in three components. The naming station is the place to stress that a group number becomes a microclimate only after its center and its field forms have been read.

**Part 4, 1:17 to 1:37.** A model should be tested the way it will be used. Before the scores, the first station explains the random forest: Many decision trees, each a chain of yes-or-no questions learned from a different random sample of the minutes, whose answers are averaged. The random forest model reaches R² = 0.66 on its training minutes and 0.54 on random test minutes, but only 0.32 when whole points are held out. Many minutes from the same point are not independent observations, so only the last score tells how the model would do at a new place. The importance ranking puts traffic first, the background PM2.5 of the day second and the people at the door third. Humidity is hardly used by the model, and Exercise 4.A shows that this stays so even with raw PM2.5. The result therefore does not come from the humidity correction of Part 1. The what-if panel and the surface show what the model has learned from the data, not what would happen after a real change on campus.

**Part 5, 1:37 to 1:55.** The numbers come from the analysis, the words may come from the AI, and the judgment stays with the team. The six errors of the AI paragraph are of six kinds: An invented number, a causal claim with an invented share, a short median set against a 24-hour guideline, a ranking of universities, a difference caused by the clock rather than the place and a source that cannot be found. The safe prompt hands the assistant the fact table, the study design and seven rules instead of asking it to know the numbers. The claim ladder separates what was observed from what is only associated, what would need an intervention and what is not supported. Each team then writes a solution card for one of the three tables of 28 November: *Microclimate and green campus*, *Waste and circular economy* or *Water, resource efficiency and youth participation*. The card answers five questions: The problem, the evidence, the solution, its feasibility and the role of young people.

**NOKTA Lab, 1:55 to 2:00.** The debrief turns the session into a field report with the pages visited, the predictions made, the interactive steps taken and the solution card. Its closing note repeats five rules: Keep the raw file, compare points through both rounds, report the averaging time, treat clusters and importances as hypotheses and check every AI-written number. The presenter then opens the *Field practice* tab and explains how its six tasks are used. When the workshop is held in person, the teams do them right after the session. When it is held online, each team does them later on its own campus. The remaining minutes are for questions, with the 3D tools of the lab at hand.

## Questions for a live poll

The pages ask their own questions. The four below can also be put to the room in a poll tool, so that the answers of all participants become visible together.

**0:08, Part 1.** On Campus A in Round 1, where is PM2.5 highest? *Shaded / Traffic / Reference / Sunny / Busy / Green.*

**0:30, Part 2.** The green area reads 13.9 °C and the road 13.3 °C in Round 1. Is the green area warmer? *Yes / No, it was measured later / They are equal.*

**0:52, break.** Which point would look warmest in Round 1, and why might that be misleading? *Open answer.*

**1:17, Part 4.** What happens to the score of the random forest model when whole points are held out? *It rises / It stays / It drops clearly.*

## Fallback plan

If the 3D scenes do not start, the browser lacks WebGL support. Every station still works with its charts, and the night view (`T`) reduces the load. If Colab is slow or a participant cannot sign in, every key number of the notebook is also on the pages. If GitHub Pages does not load, the `docs/` folder of a local copy opens directly from disk. The site has no server side and carries three.js, KaTeX and its font with it. If the data download in Colab fails, the files of the `data/` folder can be uploaded through the Files panel of Colab. If screen sharing fails, the address of the site lets participants follow on their own screens.

## Timing notes

Part 1 is the longest block, because it sets up the data that all later parts use. When time is short, station 2 can be shown in one minute and the co-location station summarized from its table. Part 3 works best with the scene on screen while the stations on the right move on. The scene stays in place on wide screens. In Part 4 the leave-one-point-out animation runs on its own, so the presenter can talk over it. The debrief can only report what was answered in the presenter's browser, so the answers of the room should be entered there as the session goes on.

## Field practice: If the teams can go out

The session itself does not ask anyone to go out and measure, because it is designed to work entirely at the screen. The *Field practice* tab of the NOKTA Lab (`lab.html#field`) adds six short tasks for a real campus. They cover watching the warm-up of a sensor, separating sunshine on the sensor from the heat of the air, measuring light in orders of magnitude, filling a field form, asking ten students and bringing the results back. Each task names the part of the session it belongs to, the time it takes and what it needs.

When the workshop is held in person, the field practice can follow the session directly. Each team shares the tasks among its members, works outside for about forty minutes and spends the last quarter of an hour on the sixth task. When the workshop is held online, the presenter introduces the tab in the closing minutes, and the teams do the tasks on their own campus during the analysis days. Anyone who watches the session later can do them at any time. The results do not replace the measurements of the field rounds, but they give each solution card a first check on site.

## After the session: 21 to 24 November

The analysis days use the same notebook on real data. Each team opens Section 0 and sets `DATA_SOURCE = "own"`. It uploads its readings, field forms and side-by-side test in the columns of `data/nokta_template.csv`, and fills `COLUMN_MAP` when the logger uses other names. Every later cell then runs on the team's own campus. Section 5 prints the fact table, the prompt and the solution card for the congress and the workshop of 28 November.

A short checklist for the teams:

1. Keep the raw logger files untouched and work on copies.
2. Write the visit order, the start and end times and the notes of every field form.
3. Leave the first two minutes after each move out of the visit medians.
4. Report every value with its averaging time, for example "median of two 15-minute visits".
5. Compare points through the two-round mean and the difference from the reference point, and do not rank campuses.
6. Check every AI-written number against the fact table before it goes into a report or a poster.
