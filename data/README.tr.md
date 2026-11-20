# Sentetik NOKTA veri seti

Bu klasördeki bütün dosyalar `tools/make_synthetic_data.py` tarafından 2026 seed değeriyle üretilmiştir. Değerler uydurmadır. Orta enlemlerde güneşli bir kasım sabahı için akla yatkındır ancak gerçek bir kampüsü anlatmaz ve bulgu olarak aktarılmamalıdır. Bu sayfanın İngilizcesi [README.md](README.md) dosyasındadır.

## Tasarım

Üç kampüsün, yani A (iç kesimde yüksek), B (karasal şehir) ve C (kıyı) kampüslerinin her birinde altı sabit nokta türü vardır. Her kampüste taşınabilir bir istasyon (S1, S2, S3) noktaları yaklaşık 1,5 m yükseklikte iki turda ziyaret eder. 1. tur saat 10:00'da başlar ve P1'den P6'ya gider. 2. tur aynı saatlerde P6'dan P1'e gider. Her ziyaret 15 dakika sürer ve her 10 saniyede bir ölçüm alınır. Ardından sonraki noktaya 10 dakika yürünür.

| Nokta | Tür | Saha formundaki not |
|---|---|---|
| P1 | `shaded` | iki bina arasında dar geçit, doğrudan güneş yok |
| P2 | `traffic` | kampüs yoluna iki metre, yakında otobüs durağı |
| P3 | `reference` | yollardan ve girişlerden uzak çim kenarı |
| P4 | `sunny_hard` | tam güneşte beton meydan, istasyon gövdesi doğrudan güneşte |
| P5 | `crowded` | fakülte girişi, kapının yanında sigara içen bir grup |
| P6 | `green` | ağaç sırasının altı, sabah sulanan çim |

## `nokta_synthetic.csv`, 3.240 satır

| Sütun | Birim | Anlamı |
|---|---|---|
| `sample_id` | | ölçümün sıra numarası |
| `timestamp` | yerel saat | ölçümün tarihi ve saati |
| `campus` | | A, B ya da C |
| `round` | | 1 ya da 2 |
| `point_id`, `point_type` | | P1-P6 ve yukarıdaki tür |
| `visit_order` | | ziyaretin kendi turundaki sırası (1-6) |
| `station` | | S1, S2 ya da S3 |
| `seconds_since_arrival` | s | 0-890 |
| `temperature_c` | °C | hava sıcaklığı |
| `rel_humidity_pct` | % | bağıl nem |
| `pressure_hpa` | hPa | istasyon basıncı (çoğunlukla yükseklik belirler) |
| `pm1_ugm3`, `pm25_ugm3`, `pm10_ugm3` | µg/m³ | optik sensörden partikül kütlesi |
| `co2_ppm` | ppm | karbondioksit |
| `light_lux` | lx | aydınlık düzeyi (16 bitlik sensör 65.535'te durur) |
| `uva_wm2`, `uvb_wm2` | W/m² | morötesi A ve B ışınımı |

## Diğer dosyalar

- `nokta_field_forms_synthetic.csv`: Her ziyaret için bir satır içerir. Sütunları şunlardır: `date`, `start`, `end`, `vehicles_15min`, `people_15min`, `sun_condition` (shade, partial, sun), `sky`, `green_cover_pct`, `station` ve `notes`.
- `nokta_colocation_synthetic.csv`: Üç istasyon 31 Ekim'de 14:00-16:00 arasında yan yana çalıştırılmıştır. Dosya dakikada bir sıcaklık, nem, PM2,5 ve CO₂ ölçümü içerir.
- `nokta_synthetic_qc_truth.csv`: `sample_id` ve `qc_truth`, her ölçüme yerleştirilen sorun (`ok`, `warmup`, `spike_pm25`, `spike_pm10`, `spike_co2`, `flatline_co2`, `gap`, `saturated`, `high_rh`). Gerçek veride böyle bir dosya yoktur.
- `nokta_template.csv`: Ölçüm dosyasının başlık satırıdır ve gerçek NOKTA verisi için kullanılır.

## Değerler nasıl üretildi

Betik, her kampüs ve tur için sabah boyunca ısınan, partikülleri ve CO₂'yi yavaşça seyrelten bir arka plan üretir. Her nokta türü kendi etkisini ekler: Gölge serinletir, güneşli meydan ısınır ve sensör gövdesini ısıtır, trafik kısa partikül ve CO₂ bulutları ekler, girişteki sigara içenler güçlü ve kısa sıçramalar ekler, ağaçlar serinletir, ışığı azaltır ve partikülleri biraz düşürür. Sensör katmanı ise düşük maliyetli cihazların yaptıklarını ekler: Her taşımadan sonra iki dakikalık dengelenme, istasyon sapmaları, nemle şişen partikül ölçümleri (κ = 0,3 ile κ-Köhler büyümesi), donmuş bir CO₂ sensörü, tek kanallı hatalar, kayıt kesintileri ve sınırına ulaşmış bir ışık sensörü.
