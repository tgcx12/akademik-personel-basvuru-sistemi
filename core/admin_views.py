# core/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.utils import timezone
from core.models.admin_models import JuriAdaylari
from core.models.admin_models import Ilanı, Basvurular
from core.models.admin_models import Kullanicilar
from core.models.admin_models import  Kullanicilar, JuriAdaylari, Basvurular, Yonetici
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
import requests
import xml.etree.ElementTree as ET
from core.models import Kullanici

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
    
@csrf_exempt
def kullanici_kaydet(request):
    if request.method == 'POST':
        try:
            isim = request.POST.get('isim', '').strip()
            soyisim = request.POST.get('soyisim', '').strip()
            tc_no = request.POST.get('tc', '').strip()
            dogum_tarihi_str = request.POST.get('dogumTarihi', '').strip()
            unvan = request.POST.get('unvan', '').strip()
            rol = request.POST.get('rol', '').strip().lower()
            sifre = request.POST.get('sifre', '').strip()

            # Rol kontrolü
            if rol not in ['aday', 'juri', 'yönetici', 'admin']:
                return JsonResponse({'status': 'fail', 'message': 'Geçerli bir rol seçiniz.'})

            # Doğum tarihi kontrolü
            try:
                dogum_tarihi = datetime.strptime(dogum_tarihi_str, "%Y-%m-%d").date()
                dogum_yili = dogum_tarihi.year
            except ValueError:
                return JsonResponse({'status': 'fail', 'message': 'Geçerli bir doğum tarihi giriniz (YYYY-AA-GG).'})

            # TC kimlik doğrulama
            if not verify_tc_kimlik(tc_no, isim, soyisim, dogum_yili):
                return JsonResponse({'status': 'fail', 'message': 'TC Kimlik doğrulaması başarısız.'})

            # TC tekrar kontrol
            if Kullanici.objects.filter(tc_kimlik_no=tc_no).exists():
                return JsonResponse({'status': 'fail', 'message': 'Bu TC ile zaten kayıt yapılmış.'})

            # Kullanıcı oluştur
            Kullanici.objects.create(
                tc_kimlik_no=tc_no,
                ad_soyad=f"{isim} {soyisim}",
                sifre_hash=sifre,
                rol=rol,
                olusturma_tarihi=timezone.now(),
                dogum_tarihi=dogum_tarihi,
                akademik_unvan=unvan,
                email='',
                adres=''
            )

            return JsonResponse({'status': 'success', 'message': 'Kullanıcı başarıyla kaydedildi.'})

        except Exception as e:
            print("[HATA]", e)
            return JsonResponse({'status': 'fail', 'message': 'Sunucu tarafında hata oluştu.'})

    return JsonResponse({'status': 'fail', 'message': 'Geçersiz istek.'})

def devam_eden_basvurular(request):
    """Bitiş tarihi bugün veya sonrasında olan ilanlar"""
    bugun   = timezone.localdate()
    ilanlar = Ilanı.objects.filter(bitis_tarih__gte=bugun) \
                          .order_by('-basl_tarih')
    return render(request, 'tablesDevamB.html', {
        'ilanlar': ilanlar
    })

def yeni_basvurular(request):
    """Yeni başvurular sayfası (henüz doldurulmadıysa statik)"""
    return render(request, 'tablesYeniB.html')

def yeni_kullanici(request):
    """Yeni başvurular sayfası (henüz doldurulmadıysa statik)"""
    return render(request, 'yeniKullanici.html')

from core.models.admin_models import Kullanicilar, JuriAdaylari

def kayitli_kullanicilar(request):
    """
    Sistemdeki yöneticiler, kullanıcılar ve jüri adaylarının listelendiği sayfa.
    """
    yoneticiler    = Yonetici.objects.all()
    kullanicilar   = Kullanicilar.objects.all()
    juri_adaylari  = JuriAdaylari.objects.all()
    return render(request, 'kayıtlıKullanicilar.html', {
        'yoneticiler': yoneticiler,
        'kullanicilar': kullanicilar,
        'juri_adaylari': juri_adaylari
    })


def tables(request):
    """Yeni başvurular sayfası (henüz doldurulmadıysa statik)"""
    return render(request, 'tables.html')

def biten_basvurular(request):
    """Filtre yok: tüm ilanları listeler"""
    ilanlar = Ilanı.objects.all().order_by('-basl_tarih')
    return render(request, 'tablesBitenB.html', {
        'ilanlar': ilanlar
    })

def basvurudetay(request, ilan_id):
    """
    Bir ilana ait başvuruları gösterir.
    URL parametresi ilan_id üzerinden çalışır.
    """
    ilan       = get_object_or_404(Ilanı, pk=ilan_id)
    basvurular = Basvurular.objects.filter(ilan=ilan) \
                                   .select_related('kullanici') \
                                   .order_by('-basvuru_tarihi')
    return render(request, 'basvurudetay.html', {
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
    return render(request, 'tablesSonuclananB.html', {
        'basvurular': basvurular
    })

def detail_application(request, basvuru_id):
    basvuru = get_object_or_404(
        Basvurular.objects.select_related('kullanici', 'ilan'),
        pk=basvuru_id
    )
    return render(request, 'detailapplication.html', {
        'basvuru': basvuru,
        'ilan':    basvuru.ilan,
        'kisi':    basvuru.kullanici,
    })