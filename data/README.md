# The synthetic NOKTA dataset

All files of this folder are produced by `tools/make_synthetic_data.py` with the seed value 2026. The values are invented. They are plausible for a sunny November morning at mid-latitudes, but they describe no real campus and must not be quoted as findings. The dataset exists so that the workshop can show every step of the analysis, including the faults that real low-cost sensors produce. A Turkish version of this page is in [README.tr.md](README.tr.md).

## Design

The dataset follows the NOKTA field protocol on three campuses. Campus A is an inland highland campus at about 1000 m above sea level, Campus B a continental city campus and Campus C a coastal campus. Each campus has the same six fixed point types, P1 to P6, which are described in the table below. One portable station per campus (S1, S2 or S3) visits the points and measures at a height of about 1.5 m.

Each campus is measured in two rounds held one week apart. Round 1 took place on 10, 11 and 12 November for Campus C, A and B, and Round 2 on 17, 18 and 19 November in the same order. Round 1 starts at 10:00 and visits the points from P1 to P6. Round 2 starts at the same clock time but visits them from P6 back to P1. Each visit lasts 15 minutes with a reading every 10 seconds, and the station then needs 10 minutes to reach the next point. A round therefore lasts about two hours and twenty minutes, and every point is measured once early and once late in the morning.

| Point | Type | Description from the field form |
|---|---|---|
| P1 | `shaded` | A narrow passage between two buildings that gets no direct sun during the visit. |
| P2 | `traffic` | A point two meters from the campus road, where buses stop nearby. |
| P3 | `reference` | The edge of an open lawn far from roads and entrances, used as the calm baseline of the campus. |
| P4 | `sunny_hard` | A concrete square in full sun, where the housing of the station is also in direct sun. |
| P5 | `crowded` | A faculty entrance with many passing students and a group smoking near the door. |
| P6 | `green` | A path under a row of trees, next to grass that is irrigated in the morning. |

## `nokta_synthetic.csv`, 3,240 rows

| Column | Unit | Meaning |
|---|---|---|
| `sample_id` | | running number of the reading |
| `timestamp` | local time | date and time of the reading |
| `campus` | | A, B or C |
| `round` | | 1 or 2 |
| `point_id`, `point_type` | | P1 to P6 and the type above |
| `visit_order` | | position of the visit in its round (1 to 6) |
| `station` | | S1, S2 or S3 |
| `seconds_since_arrival` | s | 0 to 890 |
| `temperature_c` | °C | air temperature |
| `rel_humidity_pct` | % | relative humidity |
| `pressure_hpa` | hPa | station air pressure (set mostly by altitude) |
| `pm1_ugm3`, `pm25_ugm3`, `pm10_ugm3` | µg/m³ | particle mass from an optical sensor |
| `co2_ppm` | ppm | carbon dioxide |
| `light_lux` | lx | illuminance (a 16-bit sensor stops at 65,535) |
| `uva_wm2`, `uvb_wm2` | W/m² | ultraviolet A and B irradiance |

## The other files

`nokta_field_forms_synthetic.csv` has one row per visit, 36 rows in total. It gives the date, the start and end times, the vehicles and people counted in 15 minutes, the sun condition (shade, partial or sun), the sky, the green cover in percent, the station and the notes of the team. The random forest of Part 4 takes its traffic, people, green cover and sunshine inputs from this file.

`nokta_colocation_synthetic.csv` holds the side-by-side test. The three stations ran next to each other on 31 October from 14:00 to 16:00 and recorded temperature, relative humidity, PM2.5 and CO₂ once per minute. Since they measured the same air, their differences are offsets of the devices, and Part 1 removes these offsets before the analysis.

`nokta_synthetic_qc_truth.csv` gives, for each `sample_id`, the problem planted in that reading: `ok`, `warmup`, `spike_pm25`, `spike_pm10`, `spike_co2`, `flatline_co2`, `gap`, `saturated` or `high_rh`. It is used only to score the quality control of Part 1. Real data have no such file.

`nokta_template.csv` contains the header of the readings file. Teams that analyze their own NOKTA data bring their files into these columns.

## Using real NOKTA files

Section 0 of the Colab notebook reads the synthetic files by default. A team that wants to analyze its own campus sets `DATA_SOURCE = "own"` and uploads its readings, field forms and side-by-side test in the columns of `nokta_template.csv`. When its logger uses other column names, the team fills `COLUMN_MAP` with the pairs of old and new names. Every later cell then runs on the team's own data.

## How the values were made

The script first draws a background for each campus and round. During the morning this background warms and slowly dilutes particles and CO₂, as happens on a real morning when the lowest layer of the atmosphere mixes more deeply. Each point type then adds its own effect. Shade cools the air, while the sunny square warms it and heats the housing of the sensor. Traffic adds short plumes of particles and CO₂, and the smokers at the entrance add strong, short spikes. Trees cool the air, dim the light and lower the particles slightly. Finally, a sensor layer adds what low-cost devices do in the field: A two-minute settling after every move, small offsets between the stations, particle readings inflated by humidity (κ-Köhler growth with κ = 0.3), a frozen CO₂ sensor, single-channel glitches, logger dropouts and a light sensor at its 16-bit limit.
