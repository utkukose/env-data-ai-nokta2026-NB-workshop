# Atölye rehberi

Bu rehber, NOKTA projesi (ÜNİDES 2026) kapsamında 20 Kasım 2026'da gerçekleştirilen *Yapay Zekâ ile Çevresel Veri Analizi ve Yorumlama* başlıklı iki saatlik oturumun akış planıdır. İngilizce sürümü [WORKSHOP_GUIDE.md](WORKSHOP_GUIDE.md) dosyasındadır. Süreler oturumun başlangıcından itibaren sayılmıştır, bu yüzden plan her başlangıç saatine uyar.

Oturumun tamamı atölye sitesinden yürütülmektedir: https://utkukose.github.io/env-data-ai-nokta2026-NB-workshop/tr/ (İngilizce için `/tr/` olmadan). Her bölüm aynı ritmi izler. Önce bir soru gelir, ardından sayfa cevabı bir animasyon ya da 3B sahneyle gösterir ve turuncu kutu Colab defterinin ilgili bölümünü açar. Oturum NOKTA Laboratuvarıyla kapanır.

## Oturumdan önce

Bir gün önce yedi sayfanın tamamı her iki dilde, sunum yapılacak dizüstü bilgisayarda ve bir telefonda birer kez açılmalıdır. 3B sahneler WebGL gerektirir. Eski bir projeksiyon bilgisayarında `T` tuşu (gece görünümü) ve daha küçük bir tarayıcı penceresi sahnelerin akıcı çalışmasına yardım eder. Colab defteri baştan sona bir kez çalıştırılmalıdır. Yaklaşık bir dakikada biter ve verinin GitHub'dan indirilebildiğini doğrular.

Başlangıçtan yaklaşık on beş dakika önce eğitmenin tarayıcısında başlangıç sayfası açılmalıdır. Böylece sondaki değerlendirme oturum boyunca verilen cevapları toplar. Aşağıdaki mesaj sohbet penceresinde ya da ilk slaytta paylaşılabilir:

> Atölye sitesi, kurulum gerekmez: https://utkukose.github.io/env-data-ai-nokta2026-NB-workshop/tr/
> Colab defteri (Türkçe): Her sayfadaki turuncu düğmeler
> İngilizce site: Aynı adres /tr/ olmadan · Depo: https://github.com/utkukose/env-data-ai-nokta2026-NB-workshop

## Eğitmen kontrolleri

Her sayfada sağ ve sol ok tuşları sonraki ya da önceki durağa, `]` ve `[` sonraki ya da önceki bölüme geçer. `T` kâğıt ve gece görünümünü, `F` tam ekranı, `L` İngilizce ile Türkçe arasında dili değiştirir. `B` geri sayımlı beş dakikalık bir ara açar, `?` tuşları listeler. Cevaplar ve sonuçlar yalnızca kullanılan tarayıcıda tutulur ve NOKTA Laboratuvarındaki değerlendirmeyi besler.

## Akış planı

| Süre | Blok | Ekranda | Katılımcılar |
|---|---|---|---|
| 0:00 | Açılış: Ölç → Analiz Et → Paylaş → Aksiyona Dönüştür | Başlangıç sayfası, 3B kampüs ikizi | siteyi ve defteri açar |
| 0:08 | 1. Bölüm açılışı: En yüksek PM2,5 hangi noktada? | `part1.html`, 1. durak, turu oynatma | cevaplar, sonra turu izler |
| 0:13 | On kanal · kampüsler arası basınç farkı | 2. durak | basınç sorusunu cevaplar |
| 0:16 | Veri doktoru: Isınma, donmuş CO₂, sıçramalar, eksik değer sıfır değildir | 3. durak | cevaplar, sonra ziyaret ve kanal değiştirir |
| 0:22 | Üç istasyon, tek hikâye · nemli hava | 4. ve 5. duraklar | istasyonları hizalar, nem kaydırıcısını oynatır |
| 0:26 | Temizlemenin kodu | defter, 1. Bölüm | 0. ve 1. bölümleri çalıştırır |
| 0:30 | 2. Bölüm açılışı: Son durak sıcak görünür | `part2.html`, 1. durak | cevaplar, sonra turlar arasında ilerler |
| 0:38 | Tipik değerler · ilişki mi, neden mi? | 2. ve 3. duraklar | cevaplar, ortalamaları ve grupları açar |
| 0:45 | Daha nemli mi, yalnızca daha soğuk mu? | 4. durak | çiy noktası kaydırıcılarını oynatır |
| 0:48 | Adil tablonun kodu | defter, 2. Bölüm | 2. Bölümü çalıştırır, Alıştırma 2.A'yı dener |
| 0:52 | Ara | `B` tuşu | ara ekranındaki soruyu cevaplar |
| 0:57 | 3. Bölüm açılışı: Kaç tür yer var? | `part3.html`, 3B bulut | cevaplar, nokta türüne göre renklendirir |
| 1:03 | Adım adım k-ortalamalar, J ve siluet | 2. durak, sahnenin altındaki düğmeler | yerleştirir, atar, taşır, çalıştırır |
| 1:09 | Altı kanal, üç eksen | 3. durak | cevaplar, bileşenlere geçer |
| 1:12 | Grupları adlandırın · kümelemenin kodu | 4. durak, defterin 3. Bölümü | dört grubu adlandırır |
| 1:17 | 4. Bölüm açılışı: Dürüst bir test | `part4.html`, 1. durak | cevaplar, iki bölmeyi karşılaştırır |
| 1:22 | Neye dayanıyor? | 2. durak | cevaplar, önem değerlerini okur |
| 1:26 | Ya şöyle olsaydı? Modelin üzerinde gezinin | 3. ve 4. duraklar | hazır senaryoları dener, yüzeyi döndürür |
| 1:33 | Modelin kodu | defter, 4. Bölüm | 4. Bölümü çalıştırır, kaydırıcıları dener |
| 1:37 | 5. Bölüm açılışı: Hataları bulun | `part5.html`, 1. durak | cümleleri işaretler, sonra denetler |
| 1:44 | Güvenli bir istem · iddia ne kadar güçlü? | 2. ve 3. duraklar | istemi kopyalar, iddiaları sınıflar |
| 1:50 | Çözüm kartı | 4. durak | her ekip bir kart yazar |
| 1:55 | Değerlendirme ve sorular | `lab.html#debrief` | değerlendirmeyi açar |

## Canlı anket soruları

Sayfalar kendi sorularını sorar. Aşağıdaki dört soru ayrıca bir anket aracıyla salona yöneltilebilir. Böylece bütün katılımcıların cevapları birlikte görünür.

**0:08, 1. Bölüm.** Kampüs A'nın 1. turunda PM2,5 nerede en yüksek? *Gölgeli / Trafik / Referans / Güneşli / Yoğun / Yeşil.*

**0:30, 2. Bölüm.** 1. turda yeşil alan 13,9 °C, yol 13,3 °C ölçüyor. Yeşil alan daha mı sıcak? *Evet / Hayır, daha geç ölçüldü / İkisi eşit.*

**0:52, ara.** 1. turda hangi nokta en sıcak görünür ve bu neden yanıltıcı olabilir? *Açık uçlu.*

**1:17, 4. Bölüm.** Bütün noktalar dışarıda tutulduğunda ormanın skoruna ne olur? *Yükselir / Aynı kalır / Belirgin biçimde düşer.*

## Yedek plan

3B sahneler açılmazsa tarayıcıda WebGL yoktur. Her durak grafikleriyle yine çalışır ve gece görünümü (`T`) yükü azaltır. Colab yavaşsa ya da bir katılımcı oturum açamıyorsa defterin bütün önemli sayıları sayfalarda da vardır. GitHub Pages açılmazsa yerel bir kopyadaki `docs/` klasörü doğrudan diskten açılır. Site sunucu gerektirmez ve three.js, KaTeX ile yazı tipini içinde taşır. Colab'da veri indirme başarısız olursa `data/` klasöründeki dosyalar Colab'ın Dosyalar paneliyle yüklenebilir. Ekran paylaşımı çalışmazsa site adresi katılımcıların kendi ekranlarından takip etmesine imkân verir.

## Süre notları

1. Bölüm en uzun bloktur, çünkü sonraki bütün bölümlerin kullandığı veriyi hazırlar. Süre kısalırsa 2. durak bir dakikada gösterilebilir ve yan yana test durağı tablosundan özetlenebilir. 3. Bölüm, sağdaki duraklar ilerlerken sahne ekranda kaldığında en iyi sonucu verir. Geniş ekranlarda sahne yerinde sabit durur. 4. Bölümde bir noktayı dışarıda bırakma animasyonu kendiliğinden döner, eğitmen de onun üzerine konuşabilir. Değerlendirme, eğitmenin tarayıcısı oturum boyunca soruları cevapladığında en yararlı hâlini alır.

## Oturumdan sonra: 21-24 Kasım

Analiz günlerinde aynı defter gerçek veriyle kullanılır. Her ekip 0. Bölümü açar ve `DATA_SOURCE = "own"` yapar. Ölçümlerini, saha formlarını ve yan yana testi `data/nokta_template.csv` sütunlarıyla yükler, kayıt cihazı başka adlar kullanıyorsa `COLUMN_MAP` sözlüğünü doldurur. Böylece sonraki her hücre ekibin kendi kampüsüyle çalışır ve 5. Bölüm, 28 Kasım'daki kongre ve çalıştay için olgu tablosunu, istemi ve çözüm kartını yazdırır.

Ekipler için kısa bir denetim listesi:

1. Ham kayıt dosyalarına dokunmayın, kopyalar üzerinde çalışın.
2. Her saha formunda ziyaret sırasını, başlangıç ve bitiş saatlerini ve notları yazın.
3. Her taşımadan sonraki ilk iki dakikayı ziyaret medyanlarının dışında bırakın.
4. Her değeri ortalama alma süresiyle birlikte bildirin, örneğin "iki adet 15 dakikalık ziyaretin medyanı".
5. Noktaları iki tur ortalaması ve referans noktasından fark üzerinden karşılaştırın, kampüsleri sıralamayın.
6. YZ'nin yazdığı her sayıyı rapora ya da postere girmeden önce olgu tablosuyla denetleyin.
