
from django.db import models

class Admin(models.Model):
    adminid = models.AutoField(db_column='adminID', primary_key=True)  # Field name made lowercase.
    tc = models.CharField(unique=True, max_length=11)
    sifre = models.TextField()

    class Meta:
        managed = False
        db_table = 'admin'


class ArastirmaProjelerii(models.Model):
    basvuru = models.ForeignKey('Basvurular', models.DO_NOTHING)
    proje_turu = models.TextField()  # This field type is a guess.
    proje_detaylari = models.TextField(blank=True, null=True)
    proje_belgesi = models.TextField(blank=True, null=True)
    gorev_belgesi = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'arastirma_projeleri'


class Atiflari(models.Model):
    basvuru = models.ForeignKey('Basvurular', models.DO_NOTHING)
    atif_turu = models.TextField()  # This field type is a guess.
    eserin_adi_ve_atis_sayisi = models.TextField(blank=True, null=True)
    pdf_yolu = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'atiflar'




class Basvurular(models.Model):
    kullanici = models.ForeignKey('Kullanicilar', models.DO_NOTHING)
    faaliyet_donemi = models.TextField(blank=True, null=True)
    basvurulan_kadro = models.TextField()
    basvuru_tarihi = models.DateField()
    basvuru_pdf = models.BinaryField(blank=True, null=True)
    ilan = models.ForeignKey('Ilanı', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'basvurular'


class BilimselToplantiFaaliyetlerii(models.Model):
    basvuru = models.ForeignKey(Basvurular, models.DO_NOTHING)
    bilimsel_toplanti_turu = models.TextField()  # This field type is a guess.
    detaylar = models.TextField(blank=True, null=True)
    belge_yolu = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bilimsel_toplanti_faaliyetleri'



class Editorlukk(models.Model):
    basvuru = models.ForeignKey(Basvurular, models.DO_NOTHING)
    tur = models.TextField()  # This field type is a guess.
    aciklama = models.TextField(blank=True, null=True)
    gorev_belge = models.TextField(blank=True, null=True)
    indeks_belge = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'editorluk'


class EgitimFaaliyetlerii(models.Model):
    basvuru = models.ForeignKey(Basvurular, models.DO_NOTHING)
    ders_turu = models.TextField()  # This field type is a guess.
    ders_detaylari = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'egitim_faaliyetleri'


class GuzelSanatlarFaaliyetlerii(models.Model):
    basvuru = models.ForeignKey(Basvurular, models.DO_NOTHING)
    faaliyet_turu = models.TextField()  # This field type is a guess.
    detaylar = models.TextField(blank=True, null=True)
    dokuman = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'guzel_sanatlar_faaliyetleri'


class IdariGorevleri(models.Model):
    basvuru = models.ForeignKey(Basvurular, models.DO_NOTHING)
    gorev_turu = models.TextField()  # This field type is a guess.
    gorev_birimi_yili = models.TextField(blank=True, null=True)
    belge_yukle = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'idari_gorevler'


class Ilanı(models.Model):
    ilanid = models.AutoField(db_column='ilanID', primary_key=True)  # Field name made lowercase.
    bolum = models.TextField()
    pozisyon = models.TextField()
    aciklama = models.TextField()
    bilgilendirme_dosya = models.TextField()  # This field type is a guess.
    basl_tarih = models.DateField()
    bitis_tarih = models.DateField()
    kadro_sayi = models.IntegerField()
    basvuru_sayisi = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ilan'


class JuriAdaylari(models.Model):
    juriID= models.AutoField(primary_key=True)
    isim = models.TextField()
    soyisim = models.TextField()
    unvan = models.TextField()
    kullanici_rolu = models.TextField()
    ilanid = models.ForeignKey("core.Ilan", models.DO_NOTHING, db_column='ilanID', blank=True, null=True)  # Field name made lowercase.
    tc = models.CharField(unique=True, max_length=11)
    sifre = models.TextField()
    kullanici = models.ForeignKey("core.Kullanici", models.DO_NOTHING, db_column='kullanici_id', blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'juri_adaylari'


class JuriDegerlendirmesi(models.Model):
    juridegerlendirmeid = models.AutoField(db_column='juriDegerlendirmeID', primary_key=True)  # Field name made lowercase.
    juriid = models.ForeignKey('core.JuriAdaylari', on_delete=models.CASCADE)
    basvuruid = models.ForeignKey(Basvurular, models.DO_NOTHING, db_column='basvuruID', blank=True, null=True)  # Field name made lowercase.
    juri_raporu = models.TextField(blank=True, null=True)  # This field type is a guess.
    onay_durumu = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'juri_degerlendirme'


class Kitaplari(models.Model):
    basvuru = models.ForeignKey(Basvurular, models.DO_NOTHING)
    kitap_turu = models.TextField()  # This field type is a guess.
    kitap_detaylari = models.TextField(blank=True, null=True)
    kapak_ve_icindekiler_pdf = models.TextField(blank=True, null=True)
    yayin_taninirlik_pdf = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kitaplar'




class Makaleleri(models.Model):
    basvuru = models.ForeignKey(Basvurular, models.DO_NOTHING)
    makale_turu = models.TextField()  # This field type is a guess.
    yazarlar_dergi_bilgi = models.TextField(blank=True, null=True)
    pdf_yolu = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'makaleler'


class Odulleri(models.Model):
    basvuru = models.ForeignKey(Basvurular, models.DO_NOTHING)
    tur = models.TextField()  # This field type is a guess.
    aciklama = models.TextField(blank=True, null=True)
    belge_pdf = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'oduller'


class Patentleri(models.Model):
    basvuru = models.ForeignKey(Basvurular, models.DO_NOTHING)
    patent_turu = models.TextField()  # This field type is a guess.
    patent_detaylari = models.TextField()
    patent_belgesi_pdf = models.TextField()

    class Meta:
        managed = False
        db_table = 'patentler'


class TezYoneticiliklerii(models.Model):
    basvuru = models.ForeignKey(Basvurular, models.DO_NOTHING)
    tez_turu = models.TextField()  # This field type is a guess.
    tez_detaylari = models.TextField()
    tez_belgesi_pdf = models.TextField()

    class Meta:
        managed = False
        db_table = 'tez_yoneticilikleri'
class  Kullanicilar(models.Model):
    ROL_SECENEKLERI = [
        ('yönetici', 'Yönetici'),
        ('aday', 'Aday'),
        ('juri', 'Juri'),
        ('admin', 'Admin'),
    ]
    id = models.AutoField(primary_key=True, db_column='id')  # Birincil anahtar eklendi
    tc_kimlik_no    = models.CharField(max_length=11, unique=True, db_column='tc_kimlik_no')
    ad_soyad        = models.TextField(db_column='ad_soyad')
    sifre_hash      = models.TextField(db_column='sifre_hash')
    rol = models.CharField(max_length=20, choices=ROL_SECENEKLERI, db_column='rol')
    olusturma_tarihi= models.DateTimeField(db_column='olusturma_tarihi')
    son_giris       = models.DateTimeField(blank=True, null=True, db_column='son_giris')

    USERNAME_FIELD = 'tc_kimlik_no'  # Kullanıcıyı benzersiz şekilde tanımlayan alan
    REQUIRED_FIELDS = ['rol']  # Superuser oluşturulurken istenecek zorunlu alanlar (tc_kimlik_no zaten USERNAME_FIELD)

    dogum_tarihi = models.DateField(
        db_column='dogum_tarihi'
    )
    email = models.TextField(
        db_column='email'
    )
    adres = models.TextField(
        db_column='adres'
    )
    akademik_unvan = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        db_column='akademik_unvan_kadro_turu'
    )

    def __str__(self):
        return self.tc_kimlik_no # Veya kullanıcıyı daha anlamlı bir şekilde temsil eden bir alan

    # İsteğe bağlı olarak gerekli olabilecek diğer metotlar:
    def is_active(self):
        return True

    def is_staff(self):
        return False

    def is_superuser(self):
        return False

    def get_full_name(self):
        return self.tc_kimlik_no # Veya kullanıcının tam adını döndürebilirsiniz

    def get_short_name(self):
        return self.tc_kimlik_no # Veya kullanıcının kısa adını döndürebilirsiniz

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    class Meta:
        managed = False
        db_table = 'kullanicilar'





class Yonetici(models.Model):
    yonetici_id = models.AutoField(primary_key=True)
    isim = models.TextField()
    soyisim = models.TextField()
    tc = models.CharField(unique=True, max_length=11)
    sifre = models.TextField()
    unvan = models.TextField()
    rol = models.TextField()

    class Meta:
        managed = True
        db_table = 'yonetici'