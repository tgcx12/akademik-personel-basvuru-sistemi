# core/views.py
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import JuriAdaylari, Ilan, JuriDegerlendirme,Basvurular
from django.shortcuts import render, redirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from .models import JuriAdaylari, Ilan, JuriDegerlendirme, Basvurular
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from .models import Ilanı
from .models import Basvurular
from django.http                    import HttpResponse, Http404

from django.shortcuts import render
from core.models import Kullanici # Model dosyanın yoluna göre değişebilir
from datetime import date
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
import xml.etree.ElementTree as ET
import requests
from datetime import datetime



def verify_tc_kimlik(tc_kimlik_no, ad, soyad, dogum_yili):
    soap_request = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <TCKimlikNoDogrula xmlns="http://tckimlik.nvi.gov.tr/WS">
          <TCKimlikNo>{tc_kimlik_no}</TCKimlikNo>
          <Ad>{ad.upper()}</Ad>
          <Soyad>{soyad.upper()}</Soyad>
          <DogumYili>{dogum_yili}</DogumYili>
        </TCKimlikNoDogrula>
      </soap:Body>
    </soap:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://tckimlik.nvi.gov.tr/WS/TCKimlikNoDogrula"
    }

    try:
        response = requests.post(
            "https://tckimlik.nvi.gov.tr/Service/KPSPublic.asmx",
            data=soap_request.encode('utf-8'),
            headers=headers,
            timeout=10
        )

        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://tckimlik.nvi.gov.tr/WS'}
        result = root.find('.//ns:TCKimlikNoDogrulaResult', namespace)

        return result is not None and result.text.lower() == 'true'

    except Exception as e:
        print(f"[TC Doğrulama Hatası] {e}")
        return False



def yindex(request):
    ilanlar = Ilan.objects.all()
    return render(request, 'yindex.html', {'ilanlar': ilanlar})

def index(request):
    return render(request, 'index.html')


def download_bilgilendirme(request, ilanID):
    # 🔧 pk yerine ilanid kullan!
    ilan = get_object_or_404(Ilan, ilanid=ilanID)

    if not ilan.bilgilendirme_dosya:
        raise Http404("Bu ilana ait PDF bulunamadı.")

    response = HttpResponse(ilan.bilgilendirme_dosya, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=ilan_{ilan.ilanid}_bilgilendirme.pdf'
    response['Content-Length'] = len(ilan.bilgilendirme_dosya)

    return response


def yeni_basvurular(request):
    if request.method == 'POST':
        bolum      = request.POST.get('bolum')
        pozisyon   = request.POST.get('pozisyon')
        aciklama   = request.POST.get('aciklama')
        basl_tarih = request.POST.get('basl_tarih')
        bitis_tarih= request.POST.get('bitis_tarih')
        kadro_sayi = request.POST.get('kadro_sayi')

        # Dosya yükleme (ilk dosyayı alıyoruz, istersen hepsini kaydederiz)
        uploaded_files = request.FILES.getlist('dosyalar')
        file_urls = []
        if uploaded_files:
            fs = FileSystemStorage()
            for dosya in uploaded_files:
                filename = fs.save(dosya.name, dosya)
                file_urls.append(fs.url(filename))

        # Veritabanına kaydet
        Ilan.objects.create(
            bolum=bolum,
            pozisyon=pozisyon,
            aciklama=aciklama,
            bilgilendirme_dosya=file_urls,
            basl_tarih=basl_tarih,
            bitis_tarih=bitis_tarih,
            kadro_sayi=kadro_sayi,
        )
        # Başarılıysa anasayfaya veya liste sayfasına yönlendir
        return redirect('yhome')

    # GET ise formu göster
    return render(request, 'ytablesYeniB.html')

def devam_eden_basvurular(request):
    """Bitiş tarihi bugün veya sonrasında olan ilanları listeler"""
    bugun   = timezone.localdate()
    ilanlar = Ilan.objects.filter(bitis_tarih__gte=bugun).order_by('-basl_tarih')
    return render(request, 'ytablesDevamB.html', {'ilanlar': ilanlar})

def biten_basvurular(request):
    """Bitiş tarihi bugün veya sonrasında olan ilanları listeler"""
    bugun   = timezone.localdate()
    ilanlar = Ilan.objects.filter(basl_tarih__gte=bugun).order_by('-bitis_tarih')
    return render(request, 'ytablesBitenB.html', {
        'ilanlar': ilanlar
    })

def ilan_duzenle(request, ilan_id):
    ilan = get_object_or_404(Ilan, pk=ilan_id)
    if request.method == 'POST':
        try:
            ilan.bolum       = request.POST.get('bolum')
            ilan.pozisyon    = request.POST.get('pozisyon')
            ilan.aciklama    = request.POST.get('aciklama')
            ilan.basl_tarih  = request.POST.get('basl_tarih')
            ilan.bitis_tarih = request.POST.get('bitis_tarih')
            ilan.kadro_sayi  = request.POST.get('kadro_sayi')
            # (PDF güncellemesini istersen ekleyebilirsin)
            ilan.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Yalnızca POST desteklenir.'}, status=405)


def ilan_sil(request, ilan_id):
    ilan = get_object_or_404(Ilan, pk=ilan_id)

    # 1) Ona bağlı başvuruların fk alanını NULL yap
    Basvurular.objects.filter(ilan_id=ilan.pk).update(ilan_id=None)

    # 2) İlanı sil
    ilan.delete()

    return redirect('tablesDevamB')

#def yeni_basvurular(request):
#    """Yeni başvurular sayfası (henüz doldurulmadıysa statik)"""
#    return render(request, 'tablesYeniB.html')


def yeni_juri(request):
    """Yeni başvurular sayfası (henüz doldurulmadıysa statik)"""
    return render(request, 'yyeniKullanici.html')

def tables(request):
    if request.method == 'POST':
        sender    = request.POST.get('sender')
        recipient = request.POST.get('recipient')
        subject   = request.POST.get('subject')
        body      = request.POST.get('body')

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=sender,
                recipient_list=[recipient],
                fail_silently=False,
            )
            messages.success(request, 'Mail başarıyla gönderildi.')
        except Exception as e:
            print("DEBUG: HATA OLDU")
            print(f"[Mail Hatası] {e}")
            messages.error(request, f'Gönderim hatası: {e}')

        return redirect('tables')

    return render(request, 'tables.html')

def ytables(request):
    if request.method == 'POST':
        sender    = request.POST.get('sender')
        recipient = request.POST.get('recipient')
        subject   = request.POST.get('subject')
        body      = request.POST.get('body')

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=sender,
                recipient_list=[recipient],
                fail_silently=False,
            )
            messages.success(request, 'Mail başarıyla gönderildi.')
        except Exception as e:
            print("DEBUG: HATA OLDU")
            print(f"[Mail Hatası] {e}")
            messages.error(request, f'Gönderim hatası: {e}')

        return redirect('ytables')

    return render(request, 'ytables.html')

def basvurudetay(request, ilan_id):
    """
    Bir ilana ait başvuruları gösterir.
    URL parametresi ilan_id üzerinden çalışır.
    """
    ilan       = get_object_or_404(Ilanı, pk=ilan_id)
    basvurular = Basvurular.objects.filter(ilan=ilan) \
                                   .select_related('kullanici') \
                                   .order_by('-basvuru_tarihi')
    return render(request, 'ybasvurudetay.html', {
        'ilan': ilan,
        'basvurular': basvurular
    })

def sonuclanan_basvurular(request):
    # Artık hiçbir tarih filtresi yok; tüm kayıtlar listelenecek
    basvurular = (
        Basvurular.objects
        .select_related('ilan', 'kullanici')
        .order_by('-basvuru_tarihi')
    )
    return render(request, 'ytablesSonuclananB.html', {
        'basvurular': basvurular
    })

def detail_application(request, basvuru_id):
    basvuru = get_object_or_404(
        Basvurular.objects.select_related('kullanici', 'ilan'),
        pk=basvuru_id
    )
    return render(request, 'ydetailapplication.html', {
        'basvuru': basvuru,
        'ilan':    basvuru.ilan,
        'kisi':    basvuru.kullanici,
    })

def sistem_kullanicilari(request):
    kullanici_qs = Kullanici.objects.all()

    enriched = []
    for k in kullanici_qs:
        enriched.append({
            "id": k.id,
            "tc_kimlik_no": k.tc_kimlik_no,
            "ad_soyad": k.ad_soyad.strip(),
            "sifre": k.sifre_hash,
            "rol": k.rol,
            "unvan": k.akademik_unvan,
            "olusturma_tarihi": k.olusturma_tarihi,
            "son_giris": k.son_giris
        })

    return render(request, 'ykayıtlıKullanicilar.html', {
        "kullanicilar": enriched
    })

def kayitli_kullanicilar(request):
    if request.method == 'POST':
        juri_ids = request.POST.getlist('juri_ids')
        ilan_ids = request.POST.getlist('ilan_ids')

        # Formdan gelen her jüri için eşleşen ilanı güncelle
        for jid, iid in zip(juri_ids, ilan_ids):
            if jid.isdigit() and iid.isdigit():
                JuriAdaylari.objects.filter(pk=int(jid)).update(ilanid_id=int(iid))

        # Başarılı işlem sonrası sayfaya yönlendir
        return redirect(reverse('ykayitli_kullanicilar') + '?success=1')

    juri_adaylari = JuriAdaylari.objects.select_related('ilanid').all()
    ilanlar = Ilan.objects.all()
    return render(request, 'ykayıtlıKullanicilar.html', {
        'juri_adaylari': juri_adaylari,
        'ilanlar': ilanlar,
    })


from django.shortcuts import render, redirect
from .models import JuriAdaylari

def yeni_juri_olustur(request):
    if request.method == 'POST':
        tc_no   = request.POST.get('tcNo', '').strip()
        adsoyad = request.POST.get('adSoyad', '').strip()
        unvan   = request.POST.get('unvan', '').strip()
        sifre   = request.POST.get('password', '').strip()
        gun     = request.POST.get('gun', '').zfill(2)
        ay      = request.POST.get('ay', '').zfill(2)
        yil     = request.POST.get('yil', '').strip()

        # 1. Ad-soyad ayırma kontrolü
        try:
            ad, soyad = adsoyad.split(' ', 1)
        except ValueError:
            messages.error(request, "Lütfen ad ve soyadı boşlukla ayırın.")
            return redirect('yyeniKullanici')

        # 2. Doğum tarihi kontrolü
        try:
            dogum_tarihi_str = f"{yil}-{ay}-{gun}"
            dogum_tarihi = datetime.strptime(dogum_tarihi_str, "%Y-%m-%d").date()
            dogum_yili = int(yil)
        except ValueError:
            messages.error(request, "Geçerli bir doğum tarihi giriniz (YYYY-AA-GG).")
            return redirect('yyeniKullanici')

        # 3. TC Kimlik doğrulama
        if not verify_tc_kimlik(tc_no, ad, soyad, dogum_yili):
            messages.error(request, "TC Kimlik bilgileri e-Devlet doğrulamasından geçemedi.")
            return redirect('yyeniKullanici')

        # 4. Daha önce kayıtlı mı?
        if Kullanici.objects.filter(tc_kimlik_no=tc_no).exists():
            messages.error(request, "Bu TC ile zaten kayıt olunmuş.")
            return redirect('yeni_juri_olusturma')

        # 5. Kullanıcı oluşturma
        kullanici = Kullanici.objects.create(
            tc_kimlik_no=tc_no,
            ad_soyad=adsoyad,
            sifre_hash=sifre,  # Şifre hash'lenmemiş gibi görünüyor, düzeltmeniz önerilir!
            rol='juri',
            olusturma_tarihi=timezone.now(),
            dogum_tarihi=dogum_tarihi,
            akademik_unvan=unvan
        )

        messages.success(request, "Kayıt başarıyla tamamlandı.")
        return redirect('yeni_juri_olusturma')


    return render(request, 'yyeniKullanici.html')

def biten_ilanlar(request):
    bugun = date.today()
    ilanlar = Ilan.objects.filter(bitis_tarih__lt=bugun)
    return render(request, 'ytablesBitenB.html', {'ilanlar': ilanlar})