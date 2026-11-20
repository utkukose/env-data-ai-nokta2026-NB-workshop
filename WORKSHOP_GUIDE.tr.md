# Atölye rehberi

Bu rehber, NOKTA projesi (ÜNİDES 2026) kapsamında 20 Kasım 2026'da gerçekleştirilen *Yapay Zekâ ile Çevresel Veri Analizi ve Yorumlama* başlıklı iki saatlik oturumun akış planıdır. İngilizce sürümü [WORKSHOP_GUIDE.md](WORKSHOP_GUIDE.md) dosyasındadır. Süreler oturumun başlangıcından itibaren sayılmıştır, bu yüzden plan her başlangıç saatine uyar.

Oturumun tamamı atölye sitesinden yürütülmektedir: https://utkukose.github.io/env-data-ai-nokta2026-NB-workshop/tr/ (İngilizce için `/tr/` olmadan). Her bölüm aynı ritmi izler. Önce bir soru gelir, ardından sayfa cevabı bir animasyon ya da 3B sahneyle gösterir ve turuncu kutu Colab'daki Python notebook'un ilgili kısmını açar. Oturum NOKTA Laboratuvarıyla kapanır.

## Oturumdan önce

Bir gün önce yedi sayfanın tamamı her iki dilde, sunum yapılacak dizüstü bilgisayarda ve bir telefonda birer kez açılmalıdır. 3B sahneler WebGL gerektirir. Eski bir projeksiyon bilgisayarında gece görünümü (`T` tuşu) ve daha küçük bir tarayıcı penceresi sahnelerin akıcı çalışmasına yardım eder. Python notebook da Colab'da baştan sona bir kez çalıştırılmalıdır. Python notebook yaklaşık bir dakikada biter ve verinin GitHub'dan indirilebildiğini doğrular.

NOKTA Laboratuvarındaki değerlendirme, onu gösteren tarayıcıda kaydedilen cevaplardan ve adımlardan oluşturulmaktadır. Bu yüzden bir prova, kendi cevaplarını tarayıcıda bırakır. Başlangıçtan yaklaşık on beş dakika önce eğitmen NOKTA Laboratuvarının Değerlendirme sekmesini açar ve *Yeni oturum başlat* düğmesine basarak önceki kayıtları siler. Oturum boyunca da her tahmin sorusunda salonun verdiği cevabı kendi tarayıcısında işaretler. Böylece sondaki değerlendirme bu oturumu anlatır. Aşağıdaki mesaj sohbet penceresinde ya da ilk slaytta paylaşılabilir:

> Atölye sitesi, kurulum gerekmez: https://utkukose.github.io/env-data-ai-nokta2026-NB-workshop/tr/
> Python notebook (Türkçe, Colab): Her sayfadaki turuncu düğmeler
> İngilizce site: Aynı adres /tr/ olmadan · Depo: https://github.com/utkukose/env-data-ai-nokta2026-NB-workshop

## Eğitmen kontrolleri

Her sayfada sağ ve sol ok tuşları sonraki ya da önceki durağa, `]` ve `[` sonraki ya da önceki bölüme geçer. `T` kâğıt ve gece görünümünü, `F` tam ekranı, `L` İngilizce ile Türkçe arasında dili değiştirir. `B` geri sayımlı beş dakikalık bir ara açar, `?` tuşları listeler. Cevaplar ve sonuçlar yalnızca kullanılan tarayıcıda tutulur ve NOKTA Laboratuvarındaki değerlendirmeyi besler.

## Akış planı

| Süre | Blok | Ekranda | Katılımcılar |
|---|---|---|---|
| 0:00 | Açılış: Ölç → Analiz Et → Paylaş → Aksiyona Dönüştür | Başlangıç sayfası, 3B kampüs ikizi | siteyi ve Python notebook'u açar |
| 0:08 | 1. Bölüm açılışı: En yüksek PM2,5 hangi noktada? | `part1.html`, 1. durak, turu oynatma | cevaplar, sonra turu izler |
| 0:13 | On kanal · kampüsler arası basınç farkı | 2. durak | basınç sorusunu cevaplar |
| 0:16 | Veri doktoru: Isınma, donmuş CO₂, sıçramalar, eksik değer sıfır değildir | 3. durak | cevaplar, sonra ziyaret ve kanal değiştirir |
| 0:22 | Üç istasyon, tek hikâye · nemli hava | 4. ve 5. duraklar | istasyonları hizalar, nem kaydırıcısını oynatır |
| 0:26 | Temizlemenin kodu | Python notebook, 1. kısım | 0. ve 1. kısımları çalıştırır |
| 0:30 | 2. Bölüm açılışı: Son durak sıcak görünür | `part2.html`, 1. durak | cevaplar, sonra turlar arasında ilerler |
| 0:38 | Tipik değerler · ilişki mi, neden mi? | 2. ve 3. duraklar | cevaplar, ortalamaları ve grupları açar |
| 0:45 | Daha nemli mi, yalnızca daha soğuk mu? | 4. durak | çiy noktası kaydırıcılarını oynatır |
| 0:48 | Adil tablonun kodu | Python notebook, 2. kısım | 2. kısmı çalıştırır, Alıştırma 2.A'yı dener |
| 0:52 | Ara | `B` tuşu | ara ekranındaki soruyu cevaplar |
| 0:57 | 3. Bölüm açılışı: Kaç tür yer var? | `part3.html`, 3B bulut | cevaplar, nokta türüne göre renklendirir |
| 1:03 | Adım adım k-ortalamalar, J ve siluet | 2. durak, sahnenin altındaki düğmeler | yerleştirir, atar, taşır, çalıştırır |
| 1:09 | Altı kanal, üç eksen | 3. durak | cevaplar, bileşenlere geçer |
| 1:12 | Grupları adlandırın · kümelemenin kodu | 4. durak, Python notebook'un 3. kısmı | dört grubu adlandırır |
| 1:17 | 4. Bölüm açılışı: Dürüst bir test | `part4.html`, 1. durak | cevaplar, iki bölmeyi karşılaştırır |
| 1:22 | Neye dayanıyor? | 2. durak | cevaplar, önem değerlerini okur |
| 1:26 | Ya şöyle olsaydı? Modelin üzerinde gezinin | 3. ve 4. duraklar | hazır senaryoları dener, yüzeyi döndürür |
| 1:33 | Modelin kodu | Python notebook, 4. kısım | 4. kısmı çalıştırır, kaydırıcıları dener |
| 1:37 | 5. Bölüm açılışı: Hataları bulun | `part5.html`, 1. durak | cümleleri işaretler, sonra denetler |
| 1:44 | Güvenli bir prompt (istem) · iddia ne kadar güçlü? | 2. ve 3. duraklar | promptu kopyalar, iddiaları sınıflar |
| 1:50 | Çözüm kartı | 4. durak | her ekip bir kart yazar |
| 1:55 | Değerlendirme, sahada uygulama ve sorular | `lab.html#debrief`, ardından `lab.html#field` | değerlendirmeyi açar, saha görevlerini not eder |

## Her blokta anlatılacaklar

Akış planı sırayı ve süreleri verir. Aşağıdaki paragraflar ise her bloğun katılımcılara bırakması gereken mesajı ve bu mesajı destekleyen sentetik veri sayılarını vermektedir.

**Açılış, 0:00-0:08.** Açılış, analize geçmeden önce verinin nasıl toplandığını anlatır. Her kampüste taşınabilir tek bir istasyon altı nokta türünü ziyaret eder ve her ziyaret 15 dakika sürer. 2. tur aynı güzergâhı bir hafta sonra aynı saatlerde, ancak ters sırayla, P6'dan P1'e doğru tekrarlar. Başlangıç sayfasındaki ölçüm planı bunu tablo olarak gösterir ve bir dakika ekranda tutulmaya değer. Katılımcılar açılıştan ziyaret, tur ve referans noktası kavramlarını öğrenmiş olarak ayrılmalıdır, çünkü sonraki bütün karşılaştırmalar bu üç kavrama dayanmaktadır.

**1. Bölüm, 0:08-0:30.** Bir ölçüm, ancak kalitesi denetlendikten sonra veri hâline gelir. Yeniden oynatma, değerlerin bir tur boyunca nasıl biriktiğini gösterir. Basınç sorusu, Kampüs A ile Kampüs C arasındaki yaklaşık 115 hPa'lık farkın büyük ölçüde rakımdan geldiğini ortaya koyar. Dolayısıyla basınç bir kampüsün hava kalitesini değil, konumunu anlatır. Veri doktoru durağında her hatanın kendine özgü bir izi vardır: Taşımadan sonraki ilk iki dakikadaki kayma, tek kanalda görülen tekil bir sıçrama, donmuş bir sensörün düz çizgisi ve kayıt cihazının bıraktığı boşluklar. Eksik değer örneği üzerinde biraz durulmalıdır. Altı boş ölçüm sıfır olarak yazıldığında ortalama sıcaklık 10,37 °C'den 7,54 °C'ye düşmektedir. Dedektör yerleştirilen hataların neredeyse tamamını yakalar, ancak gerçek duman ve egzoz bulutlarının içine düşen iki PM2,5 hatasını kaçırır. Bu yüzden işaretlenen ölçümlere bir insanın da bakması gerekir. Ardından oturumun ilk YZ yöntemi olan Isolation Forest, kural kullanmadan ikinci bir görüş verir. Yöntem 65 sıra dışı ölçüm işaretler, ancak bunların çoğu gerçek duman ve egzoz bulutlarıdır. Bu da sıra dışı olmanın hatalı olmak anlamına gelmediğini gösterir. 1. Bölüm 36 ziyaret × 13 dakika = 468 temiz dakikalık tabloyla biter ve sonraki bütün sayılar bu tablodan gelir.

**2. Bölüm, 0:30-0:52.** Adil bir karşılaştırma saatin, aykırı değerlerin ve gizli grupların etkisini kontrol etmelidir. Kampüs A'nın 1. turunda yeşil alan 13,9 °C, yol 13,3 °C ölçer, ancak yeşil alan ısınan bir sabahta en son ölçülmüştür. İki turun ortalamasında yeşil alan referans noktasından 1,1 °C daha serin, yol ise 0,6 °C daha sıcaktır. Kutu grafikleri, kalabalık girişin yakınında kısa süreli sigara dumanının ortalamayı medyanın üstüne çektiğini gösterir. Bütün dakikalar birlikte alındığında sıcaklık ile basınç arasındaki korelasyon r = +0,81'dir. Oysa her kampüsün ve turun kendi içinde korelasyon −0,41 ile −0,64 arasında kalır. Gizli üçüncü etken kampüsün kendisidir. Çiy noktası durağı, havadaki su miktarını sıcaklıktan ayırarak bölümü kapatır.

**3. Bölüm, 0:57-1:17.** Gözetimsiz öğrenme gruplar önerir, bu grupları adlandırmak ve doğrulamak ise insanların işidir. k-ortalamalar merkezleri yerleştirir, her dakikayı en yakın merkeze atar ve hiçbir şey değişmeyene kadar merkezleri taşır. Dört grupla çalıştırıldığında dört yinelemede durur, J = 363,0 ve siluet değeri 0,499 olur. Siluet değeri üç ile altı grup arasında neredeyse değişmez. Bu yüzden dört grup seçimi, analistin vermesi ve gerekçelendirmesi gereken bir karardır. PCA, altı kanalın varyansının yaklaşık %86'sını üç bileşende korur. Adlandırma durağı, bir grup numarasının ancak merkezi ve saha formları okunduktan sonra bir mikroiklime dönüştüğünü vurgulamak için uygun yerdir.

**4. Bölüm, 1:17-1:37.** Bir model, nasıl kullanılacaksa öyle test edilmelidir. Skorlardan önce ilk durak rastgele orman algoritmasını açıklar: Her biri dakikaların rastgele seçilmiş farklı bir örnekleminden öğrenilen bir evet-hayır soru zinciri olan çok sayıda karar ağacı ve bu ağaçların cevaplarının ortalaması. Rastgele orman modeli kendi eğitim dakikalarında R² = 0,66, rastgele test dakikalarında 0,54 değerine ulaşır, bütün noktalar dışarıda tutulduğunda ise yalnızca 0,32'de kalır. Aynı noktadan gelen çok sayıda dakika birbirinden bağımsız gözlemler değildir. Bu yüzden modelin yeni bir yerde nasıl çalışacağını yalnızca son skor anlatır. Önem sıralamasında trafik ilk, günün arka plan PM2,5 değeri ikinci, kapıdaki insanlar ise üçüncü sıradadır. Model nemi neredeyse hiç kullanmaz ve 4.A alıştırması bunun ham PM2,5 ile de değişmediğini gösterir. Yani bu sonuç 1. Bölümdeki nem düzeltmesinden kaynaklanmaz. Senaryo paneli ve 3B yüzey, kampüste gerçek bir değişiklik yapıldığında ne olacağını değil, modelin veriden ne öğrendiğini gösterir.

**5. Bölüm, 1:37-1:55.** Sayılar analizden gelir, kelimeler YZ'den gelebilir, son karar ise ekibe aittir. YZ paragrafındaki altı hata altı farklı türdendir: Uydurulmuş bir sayı, uydurulmuş bir oranla kurulan nedensel bir iddia, kısa bir ziyaretin medyanının 24 saatlik bir kılavuz değeriyle karşılaştırılması, üniversitelerin sıralanması, yerden değil saatten kaynaklanan bir fark ve bulunamayan bir kaynak. Güvenli prompt, asistandan sayıları bilmesini istemek yerine ona olgu tablosunu, çalışmanın tasarımını ve yedi kuralı verir. İddia merdiveni, gözlenen bulguyu yalnızca ilişkili olandan, müdahale gerektirenden ve desteklenmeyenden ayırır. Ardından her ekip 28 Kasım'daki üç masadan biri için bir çözüm kartı yazar: *Mikroiklim ve yeşil kampüs*, *Atık ve döngüsel ekonomi* ya da *Su, kaynak verimliliği ve gençlik katılımı*. Kart beş soruyu cevaplar: Sorun, dayanak, çözüm, uygulanabilirlik ve gençlerin rolü.

**NOKTA Laboratuvarı, 1:55-2:00.** Değerlendirme, oturumu ziyaret edilen sayfaları, yapılan tahminleri, atılan etkileşimli adımları ve çözüm kartını içeren bir saha raporuna dönüştürür. Raporun son notu beş kuralı tekrarlar: Ham dosyayı koru, noktaları iki tur üzerinden karşılaştır, ortalama alma süresini bildir, kümeleri ve önem değerlerini hipotez olarak gör ve YZ'nin yazdığı her sayıyı denetle. Ardından eğitmen *Sahada uygulama* sekmesini açar ve altı görevin nasıl kullanılacağını anlatır. Atölye yüz yüze yapılıyorsa ekipler görevleri oturumun hemen ardından yapar. Çevrim içi yapılıyorsa her ekip bunları daha sonra kendi kampüsünde yapar. Kalan dakikalar, laboratuvarın 3B araçları el altındayken soruları cevaplamaya ayrılır.

## Canlı anket soruları

Sayfalar kendi sorularını sorar. Aşağıdaki dört soru ayrıca bir anket aracıyla salona yöneltilebilir. Böylece bütün katılımcıların cevapları birlikte görünür.

**0:08, 1. Bölüm.** Kampüs A'nın 1. turunda PM2,5 nerede en yüksek? *Gölgeli / Trafik / Referans / Güneşli / Yoğun / Yeşil.*

**0:30, 2. Bölüm.** 1. turda yeşil alan 13,9 °C, yol 13,3 °C ölçüyor. Yeşil alan daha mı sıcak? *Evet / Hayır, daha geç ölçüldü / İkisi eşit.*

**0:52, ara.** 1. turda hangi nokta en sıcak görünür ve bu neden yanıltıcı olabilir? *Açık uçlu.*

**1:17, 4. Bölüm.** Bütün noktalar dışarıda tutulduğunda rastgele orman modelinin skoruna ne olur? *Yükselir / Aynı kalır / Belirgin biçimde düşer.*

## Yedek plan

3B sahneler açılmıyorsa tarayıcıda WebGL desteği yok demektir. Her durak grafikleriyle yine çalışır ve gece görünümü (`T`) yükü azaltır. Colab yavaşsa ya da bir katılımcı oturum açamıyorsa Python notebook'un bütün önemli sayıları sayfalarda da vardır. GitHub Pages açılmazsa yerel bir kopyadaki `docs/` klasörü doğrudan diskten açılır. Site sunucu gerektirmez ve three.js, KaTeX ile yazı tipini içinde taşır. Colab'da veri indirme başarısız olursa `data/` klasöründeki dosyalar Colab'ın Dosyalar paneliyle yüklenebilir. Ekran paylaşımı çalışmazsa site adresi katılımcıların kendi ekranlarından takip etmesine imkân verir.

## Süre notları

1. Bölüm en uzun bloktur, çünkü sonraki bütün bölümlerin kullandığı veriyi hazırlar. Süre kısalırsa 2. durak bir dakikada gösterilebilir ve yan yana test durağı tablosundan özetlenebilir. 3. Bölüm, sağdaki duraklar ilerlerken sahne ekranda kaldığında en iyi sonucu verir. Geniş ekranlarda sahne yerinde sabit durur. 4. Bölümde bir noktayı dışarıda bırakma animasyonu kendiliğinden döner, eğitmen de onun üzerine konuşabilir. Değerlendirme yalnızca eğitmenin tarayıcısında cevaplanan soruları raporlayabilir. Bu yüzden salonun cevapları oturum ilerledikçe o tarayıcıda işaretlenmelidir.

## Sahada uygulama: Ekipler dışarı çıkabilirse

Oturumun kendisi kimseden dışarı çıkıp ölçüm yapmasını istemez, çünkü tamamen ekran başında yürütülebilecek biçimde tasarlanmıştır. NOKTA Laboratuvarındaki *Sahada uygulama* sekmesi (`lab.html#field`) gerçek bir kampüs için altı kısa görev ekler: Bir sensörün ısınma süresini izlemek, sensöre vuran güneşi havanın sıcaklığından ayırmak, ışığı büyüklük mertebesiyle ölçmek, bir saha formunu doldurmak, on öğrenciye soru sormak ve sonuçları geri getirmek. Her görev ait olduğu bölümü, süresini ve neye ihtiyaç duyduğunu belirtir.

Atölye yüz yüze yapılabildiğinde sahada uygulama oturumun hemen ardından gelebilir. Her ekip görevleri üyeleri arasında paylaşır, yaklaşık kırk dakika dışarıda çalışır ve son çeyrek saati altıncı göreve ayırır. Atölye çevrim içi yapıldığında eğitmen sekmeyi kapanış dakikalarında tanıtır, ekipler de görevleri analiz günlerinde kendi kampüslerinde yapar. Oturumu daha sonra izleyen herkes bu görevleri istediği zaman yapabilir. Sonuçlar saha turlarının ölçümlerinin yerini tutmaz, ancak her çözüm kartına sahada ilk bir denetim sağlar.

## Oturumdan sonra: 21-24 Kasım

Analiz günlerinde aynı Python notebook gerçek veriyle kullanılır. Her ekip Python notebook'un 0. kısmını açar ve `DATA_SOURCE = "own"` yapar. Ölçümlerini, saha formlarını ve yan yana testi `data/nokta_template.csv` sütunlarıyla yükler, kayıt cihazı başka adlar kullanıyorsa `COLUMN_MAP` sözlüğünü doldurur. Böylece sonraki her hücre ekibin kendi kampüsüyle çalışır. Python notebook'un 5. kısmı da 28 Kasım'daki kongre ve çalıştay için olgu tablosunu, promptu ve çözüm kartını yazdırır.

Ekipler için kısa bir denetim listesi:

1. Ham kayıt dosyalarına dokunmayın, kopyalar üzerinde çalışın.
2. Her saha formunda ziyaret sırasını, başlangıç ve bitiş saatlerini ve notları yazın.
3. Her taşımadan sonraki ilk iki dakikayı ziyaret medyanlarının dışında bırakın.
4. Her değeri ortalama alma süresiyle birlikte bildirin, örneğin "iki adet 15 dakikalık ziyaretin medyanı".
5. Noktaları iki tur ortalaması ve referans noktasından fark üzerinden karşılaştırın, kampüsleri sıralamayın.
6. YZ'nin yazdığı her sayıyı rapora ya da postere girmeden önce olgu tablosuyla denetleyin.
