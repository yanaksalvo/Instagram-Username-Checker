# Instagram Username Checker

Bu araç, Instagram platformunda kullanıcı adlarının kullanılabilirliğini kontrol etmek için geliştirilmiştir.

## Gereksinimler

- **Python**: Projenin çalışması için Python yüklü olmalıdır. Eğer sisteminizde Python yüklü değilse, [resmi Python web sitesinden](https://www.python.org/downloads/) indirebilirsiniz.
- Python'un yüklü olup olmadığını kontrol etmek için terminalde şu komutu çalıştırabilirsiniz:
  ```
  python --version
  ```

## Kurulum

1. Projeyi GitHub'dan indirin veya kopyalayın:
   ```bash
   git clone https://github.com/yanaksalvo/Instagram-Username-Checker.git
   ```
2. Proje dizinine gidin:
   ```bash
   cd Instagram-Username-Checker
   ```
3. Gerekli modülleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

## Kullanım

1. **Tekli Kullanıcı Adı Kontrolü**:
   - Kodu çalıştırın:
     ```bash
     python username_checker.py
     ```
   - Menüden **2. çözümü** seçin.
   - Kontrol etmek istediğiniz kullanıcı adını girin.

2. **Çoklu Kullanıcı Adı Kontrolü**:
   - Proje dizininde bir `username.txt` dosyası oluşturun.
   - Kontrol etmek istediğiniz kullanıcı adlarını alt alta yazın.
   - Kodu çalıştırın:
     ```bash
     python username_checker.py
     ```
   - Menüden **1. çözümü** seçin.

## Sonuçlar

- **Taken**: Kullanıcı adı zaten kullanılıyor.
- **Available**: Kullanıcı adı kullanılabilir.

## Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.

## İletişim

Sorularınız veya önerileriniz için bana Telegram üzerinden ulaşabilirsiniz:  
[@babakonusmazgosterirhepicraat](https://t.me/babakonusmazgosterirhepicraat)
