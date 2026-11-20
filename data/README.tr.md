# Sentetik NOKTA veri seti

Bu klasördeki bütün dosyalar `tools/make_synthetic_data.py` tarafından 2026 seed değeriyle üretilmiştir. Değerler uydurmadır. Orta enlemlerde güneşli bir kasım sabahı için akla yatkındır, ancak gerçek bir kampüsü anlatmaz ve bulgu olarak aktarılmamalıdır. Veri seti, atölyenin analizin her adımını, gerçek düşük maliyetli sensörlerin ürettiği hatalar dâhil, gösterebilmesi için hazırlanmıştır. Bu sayfanın İngilizcesi [README.md](README.md) dosyasındadır.

## Tasarım

Veri seti NOKTA saha protokolünü üç kampüste izlemektedir. Kampüs A deniz seviyesinden yaklaşık 1000 m yükseklikte, iç bölgede bir kampüstür. Kampüs B karasal iklimli bir şehir kampüsü, Kampüs C ise bir kıyı kampüsüdür. Her kampüste aşağıdaki tabloda tanımlanan aynı altı sabit nokta türü (P1-P6) bulunur. Her kampüste taşınabilir bir istasyon (S1, S2 ya da S3) noktaları ziyaret eder ve yaklaşık 1,5 m yükseklikte ölçüm yapar.

Her kampüs, aralarında bir hafta bulunan iki turda ölçülmüştür. 1. tur Kampüs C, A ve B için sırasıyla 10, 11 ve 12 Kasım'da, 2. tur ise aynı sırayla 17, 18 ve 19 Kasım'da yapılmıştır. 1. tur saat 10:00'da başlar ve noktaları P1'den P6'ya doğru ziyaret eder. 2. tur aynı saatte başlar, ancak noktaları P6'dan P1'e doğru dolaşır. Her ziyaret 15 dakika sürer ve her 10 saniyede bir ölçüm alınır. İstasyon ardından sonraki noktaya 10 dakikada ulaşır. Böylece bir tur yaklaşık iki saat yirmi dakika sürer ve her nokta sabahın bir kez erken, bir kez de geç bir saatinde ölçülmüş olur. Aşağıdaki tablo ziyaretlerin saatlerini ve sırasını göstermektedir.

| Saat | 1. tur | 2. tur, bir hafta sonra |
|---|---|---|
| 10:00-10:15 | P1 `shaded` | P6 `green` |
| 10:25-10:40 | P2 `traffic` | P5 `crowded` |
| 10:50-11:05 | P3 `reference` | P4 `sunny_hard` |
| 11:15-11:30 | P4 `sunny_hard` | P3 `reference` |
| 11:40-11:55 | P5 `crowded` | P2 `traffic` |
| 12:05-12:20 | P6 `green` | P1 `shaded` |

Her ziyaretin ilk iki dakikası sensörlerin ısınma süresidir ve analizde kullanılmaz. Bu yüzden her ziyaretten 13 dakika, toplamda 36 × 13 = 468 temiz dakika kalır.

| Nokta | Tür | Saha formundaki tanım |
|---|---|---|
| P1 | `shaded` | İki bina arasında, ziyaret boyunca doğrudan güneş almayan dar bir geçit. |
| P2 | `traffic` | Kampüs yolundan iki metre uzakta, yakınında otobüslerin durduğu bir nokta. |
| P3 | `reference` | Yollardan ve girişlerden uzak, açık bir çim alanın kenarı. Kampüsün sakin karşılaştırma noktası olarak kullanılır. |
| P4 | `sunny_hard` | Tam güneş alan, istasyon gövdesinin de doğrudan güneşte kaldığı beton bir meydan. |
| P5 | `crowded` | Öğrencilerin yoğun geçtiği, kapısının yanında sigara içen bir grubun bulunduğu fakülte girişi. |
| P6 | `green` | Bir ağaç sırasının altında, sabah sulanan çimlerin yanından geçen bir yol. |

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

`nokta_field_forms_synthetic.csv` her ziyaret için bir satır, toplam 36 satır içerir. Dosyada tarih, başlangıç ve bitiş saatleri, 15 dakikada sayılan araç ve kişi sayısı, güneş durumu (gölge, kısmi ya da güneş), gökyüzü, yüzde olarak yeşil örtü, istasyon ve ekibin notları yer almaktadır. 4. Bölümdeki rastgele orman trafik, insan, yeşil örtü ve güneşlenme girdilerini bu dosyadan alır.

`nokta_colocation_synthetic.csv` yan yana testi içerir. Üç istasyon 31 Ekim'de 14:00-16:00 arasında yan yana çalıştırılmış ve sıcaklık, bağıl nem, PM2,5 ve CO₂ değerlerini dakikada bir kaydetmiştir. İstasyonlar aynı havayı ölçtüğü için aralarındaki farklar cihazların kendi sapmalarıdır. 1. Bölüm bu sapmaları analizden önce giderir.

`nokta_synthetic_qc_truth.csv` her `sample_id` için o ölçüme bilerek yerleştirilen sorunu verir: `ok`, `warmup`, `spike_pm25`, `spike_pm10`, `spike_co2`, `flatline_co2`, `gap`, `saturated` ya da `high_rh`. Dosya yalnızca 1. Bölümdeki kalite kontrolünü puanlamak için kullanılır. Gerçek veride böyle bir dosya bulunmaz.

`nokta_template.csv` ölçüm dosyasının başlık satırını içerir. Kendi NOKTA verisini analiz eden ekipler dosyalarını bu sütunlara göre hazırlar.

## Gerçek NOKTA dosyalarının kullanılması

Python notebook'un 0. kısmı varsayılan olarak sentetik dosyaları okur. Kendi kampüsünü analiz etmek isteyen bir ekip `DATA_SOURCE = "own"` ayarını yapar ve ölçümlerini, saha formlarını ve yan yana testini `nokta_template.csv` sütunlarıyla yükler. Kayıt cihazı başka sütun adları kullanıyorsa ekip `COLUMN_MAP` sözlüğüne eski ve yeni adları eşleştirerek yazar. Böylece sonraki her hücre ekibin kendi verisiyle çalışır.

## Değerler nasıl üretildi

Betik önce her kampüs ve tur için bir arka plan üretir. Bu arka plan sabah boyunca ısınır, partikülleri ve CO₂'yi de yavaşça seyreltir. Gerçek bir sabahta da atmosferin en alt katmanı giderek daha derin karıştığı için benzer bir seyrelme görülmektedir. Ardından her nokta türü kendi etkisini ekler. Gölge havayı serinletir, güneşli meydan ise havayı ısıtır ve sensörün gövdesini de ısıtır. Trafik kısa süreli partikül ve CO₂ bulutları ekler, girişteki sigara içenler de güçlü ve kısa sıçramalar oluşturur. Ağaçlar havayı serinletir, ışığı azaltır ve partikülleri biraz düşürür. Son olarak bir sensör katmanı, düşük maliyetli cihazların sahada yaptıklarını ekler: Her taşımadan sonra iki dakikalık dengelenme süresi, istasyonlar arasındaki küçük sapmalar, nemle şişen partikül ölçümleri (κ = 0,3 ile κ-Köhler büyümesi), donmuş bir CO₂ sensörü, tek kanalda görülen hatalar, kayıt kesintileri ve 16 bitlik sınırına ulaşmış bir ışık sensörü.
