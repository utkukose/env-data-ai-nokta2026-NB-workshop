# Workshop guide

This guide is the run sheet for the two-hour session *AI-Based Environmental Data Analysis and Interpretation* of the NOKTA project (ÜNİDES 2026) on 20 November 2026. A Turkish version is in [WORKSHOP_GUIDE.tr.md](WORKSHOP_GUIDE.tr.md). Times are counted from the start of the session, so the sheet fits any starting hour.

The whole session runs from the workshop site, https://utkukose.github.io/env-data-ai-nokta2026-NB-workshop/ (Turkish: `/tr/`). Every part follows the same rhythm. A question comes first, the page then reveals the answer with an animation or a 3D scene, and an orange box opens the matching section of the Colab notebook. The NOKTA Lab closes the session.

## Before the session

On the day before, all seven pages should be opened once on the presenting laptop and once on a phone, in both languages. The 3D scenes need WebGL. On an old projector laptop the key `T` (night view) and a smaller browser window keep the scenes smooth. The Colab notebook should be run once from top to bottom. It finishes in about a minute and confirms that the data download from GitHub works.

About fifteen minutes before the start, the presenter's browser should open the start page, so that the debrief at the end collects the answers given during the session. The following message can be shared in the chat or on the first slide:

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
| 1:55 | Debrief and questions | `lab.html#debrief` | open the debrief |

## Questions for a live poll

The pages ask their own questions. The four below can also be put to the room in a poll tool, so that the answers of all participants become visible together.

**0:08, Part 1.** On Campus A in Round 1, where is PM2.5 highest? *Shaded / Traffic / Reference / Sunny / Busy / Green.*

**0:30, Part 2.** The green area reads 13.9 °C and the road 13.3 °C in Round 1. Is the green area warmer? *Yes / No, it was measured later / They are equal.*

**0:52, break.** Which point would look warmest in Round 1, and why might that be misleading? *Open answer.*

**1:17, Part 4.** What happens to the score of the forest when whole points are held out? *It rises / It stays / It drops clearly.*

## Fallback plan

If the 3D scenes do not start, the browser lacks WebGL. Every station still works with its charts, and the night view (`T`) reduces the load. If Colab is slow or a participant cannot sign in, every key number of the notebook is also on the pages. If GitHub Pages does not load, the `docs/` folder of a local copy opens directly from disk. The site has no server side and carries three.js, KaTeX and its font with it. If the data download in Colab fails, the files of the `data/` folder can be uploaded through the Files panel of Colab. If screen sharing fails, the address of the site lets participants follow on their own screens.

## Timing notes

Part 1 is the longest block, because it sets up the data that all later parts use. When time is short, station 2 can be shown in one minute and the co-location station summarized from its table. Part 3 works best with the scene on screen while the stations on the right move on. The scene stays in place on wide screens. In Part 4 the leave-one-point-out animation runs on its own, so the presenter can talk over it. The debrief is most useful when the presenter's browser has answered the questions during the session.

## After the session: 21 to 24 November

The analysis days use the same notebook on real data. Each team opens Section 0 and sets `DATA_SOURCE = "own"`. It uploads its readings, field forms and side-by-side test in the columns of `data/nokta_template.csv`, and fills `COLUMN_MAP` when the logger uses other names. Every later cell then runs on the team's own campus. Section 5 prints the fact table, the prompt and the solution card for the congress and the workshop of 28 November.

A short checklist for the teams:

1. Keep the raw logger files untouched and work on copies.
2. Write the visit order, the start and end times and the notes of every field form.
3. Leave the first two minutes after each move out of the visit medians.
4. Report every value with its averaging time, for example "median of two 15-minute visits".
5. Compare points through the two-round mean and the difference from the reference point, and do not rank campuses.
6. Check every AI-written number against the fact table before it goes into a report or a poster.
