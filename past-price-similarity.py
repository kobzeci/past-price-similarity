import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from binance.client import Client

# -----------------------------------------------------
# 1) Binance'ten veri indirme fonksiyonu
# -----------------------------------------------------
def download_data_from_binance(instrument, period, start_date, api_key, api_secret, csv_filename):
    """
    Binance'ten tarihsel kline (mum) verisi indirip CSV'ye kaydeder.
    """
    client = Client(api_key, api_secret)
    
    # Veriyi indirme
    klines = client.get_historical_klines(instrument, period, start_date)
    
    # Kline verisini DataFrame'e dönüştürme
    columns = [
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ]
    df = pd.DataFrame(klines, columns=columns)
    
    # Zaman kolonlarını milisaniyeden datetime formatına çevir
    df["Open Time"] = pd.to_datetime(df["Open Time"], unit='ms')
    df["Close Time"] = pd.to_datetime(df["Close Time"], unit='ms')
    
    # Sayısal kolonları float'a çevir
    numeric_cols = ["Open", "High", "Low", "Close", "Volume",
                    "Quote Asset Volume", "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume"]
    df[numeric_cols] = df[numeric_cols].astype(float)
    
    # "Ignore" kolonu gereksiz, silelim
    df.drop(columns=["Ignore"], inplace=True)
    
    # CSV'ye kaydet
    df.to_csv(csv_filename, index=False)
    
    print(f"Toplam {len(df)} satır veri '{csv_filename}' dosyasına kaydedildi.")
    return df

# -----------------------------------------------------
# 2) Normalizasyon fonksiyonu
# -----------------------------------------------------
def get_normalized_series(prices):
    """
    Bir fiyat dizisini, ilk barına göre normalize eder (ilk bar -> 0).
    Örneğin ilk bar 100 ise, 120 -> +0.20, 90 -> -0.10 vb.
    """
    if len(prices) == 0:
        return np.array([])
    first_price = prices[0]
    return (prices / first_price) - 1.0

# -----------------------------------------------------
# 3) Öklidyen mesafe fonksiyonu
# -----------------------------------------------------
def euclidean_distance(x, y):
    """
    İki numpy dizisi (zaman serisi) arasındaki öklidyen mesafeyi hesaplar.
    """
    return np.sqrt(np.sum((x - y)**2))

# -----------------------------------------------------
# 4) Benzerlik analizi (Normalize + Sonraki blok kaydırma)
# -----------------------------------------------------
def analyze_similarity(df, n_bars=100):
    """
    df: Tüm veri (DataFrame)
    n_bars: Son kaç barlık fiyat hareketini temel alacağız?

    Adımlar:
      1) 'Mevcut son n_bars' -> normalize
      2) Geçmişte her n_bars'lık bloğu da normalize, öklidyen mesafe karşılaştırması
      3) En benzer dönemin 'sonraki n_bars'ını da normalize edip
         önceki bloğun son değerine kaydırarak tek grafikte çiz.
    """
    # DataFrame'i zaman sıralamasına göre düzenleyelim
    df.sort_values(by="Open Time", inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # Sabit: Sonraki X bar sayısı (analizle aynı, dilerseniz farklı yapabilirsiniz)
    FUTURE_BARS = n_bars
    
    # Mevcut son n bar (ham fiyat)
    latest_block = df.tail(n_bars).copy()
    latest_prices = latest_block["Close"].values
    
    # Normalize edelim (kırmızı çizgi)
    latest_norm = get_normalized_series(latest_prices)

    # Tüm veri üzerinde kaydırmalı şekilde benzerlik arıyoruz
    similarities = []
    for i in range(len(df) - n_bars - FUTURE_BARS):
        past_prices = df["Close"].iloc[i : i + n_bars].values
        # Her blok kendi ilk barına göre normalize
        past_norm   = get_normalized_series(past_prices)
        
        distance    = euclidean_distance(latest_norm, past_norm)
        similarities.append((i, distance))
    
    # Mesafeye göre sıralama (en düşük -> en benzer)
    similarities.sort(key=lambda x: x[1])
    
    # İlk 3 en benzer, isterseniz 1 tanesiyle de sınırlayabilirsiniz
    best_matches = similarities[:3]
    
    results = []
    
    # Grafikte sadece en iyi eşleşmeyi gösterelim (dilerseniz hepsini de çizebilirsiniz)
    if len(best_matches) > 0:
        best_idx, best_dist = best_matches[0]
        
        # Benzer döneminin tarih bilgileri
        start_time = df["Open Time"].iloc[best_idx]
        end_time   = df["Open Time"].iloc[best_idx + n_bars - 1]
        
        # Benzer blok (ham fiyat + normalize) - mavi çizgi
        best_past_prices = df["Close"].iloc[best_idx : best_idx + n_bars].values
        best_past_norm   = get_normalized_series(best_past_prices)
        
        # Sonraki n_bars (ham fiyat + normalize) - yeşil çizgi
        best_future_prices = df["Close"].iloc[best_idx + n_bars : best_idx + n_bars + FUTURE_BARS].values
        if len(best_future_prices) < FUTURE_BARS:
            # Veri eksik olabilir
            print("Veri eksik, en iyi eşleşme sonrasında yeterli bar yok.")
        else:
            best_future_norm = get_normalized_series(best_future_prices)
            
            # ---- Farklı: Sonraki bloğu, önceki bloğun son değerine kaydırma ----
            last_val_of_past = best_past_norm[-1]  # mavi çizginin bittiği nokta
            best_future_norm = best_future_norm + last_val_of_past
            # --------------------------------------------------------------------
            
            # Grafik
            plt.figure(figsize=(10, 6))
            
            # Mevcut son n_bars (kırmızı)
            plt.plot(latest_norm, label="Mevcut Son Blok (normalize)", color='red')
            
            # Benzer n_bars (mavi)
            plt.plot(
                best_past_norm,
                label=f"Benzer {n_bars} Bar\n({start_time} -> {end_time})", 
                color='blue'
            )
            
            # Benzerlik sonrası n_bars (yeşil, kaydırılmış)
            plt.plot(
                range(n_bars, n_bars + FUTURE_BARS),
                best_future_norm,
                label="Benzerlik Sonrası (kaydırılmış)",
                color='green'
            )
            
            plt.title("Normalizasyon + Kaydırma (Önceki Blok Sonundan Devam)")
            plt.xlabel("Bar Index (Göreceli)")
            plt.ylabel("Normalize Fiyat (İlk Bar = 0)")
            plt.legend()
            plt.show()
            
            # Performans (ham fiyat üzerinden)
            future_max = best_future_prices.max()
            future_min = best_future_prices.min()
            pct_change = (best_future_prices[-1] - best_future_prices[0]) / best_future_prices[0] * 100
            
            results.append({
                "Benzer Dönem Başlangıcı": start_time,
                "Benzer Dönem Sonu": end_time,
                "Benzerlik (Distance)": best_dist,
                "Sonraki Bar Max": future_max,
                "Sonraki Bar Min": future_min,
                "Sonraki Bar % Değişim": pct_change
            })
    
    df_results = pd.DataFrame(results)
    return df_results

# -----------------------------------------------------
# 5) ANA PROGRAM
# -----------------------------------------------------
if __name__ == "__main__":
    instrument = input("Lütfen enstrümanı giriniz (örn: BTCUSDT): ").upper()
    period = input("Lütfen periyodu giriniz (örn: 1m, 5m, 15m, 1h, 4h, 1d): ").lower()
    start_date = input("Veriyi hangi tarihten itibaren çekelim? (YYYY-MM-DD): ")
    n_bars = int(input("Son kaç barlık fiyatı temel alalım? (örn: 100): "))
    
    choice = input("Elinizde mevcut CSV dosyası var mı? (y/n): ")
    
    if choice.lower() == 'y':
        csv_path = input("CSV dosyasının yolunu giriniz: ")
        if not os.path.exists(csv_path):
            print("Belirtilen dosya bulunamadı, program sonlanıyor.")
            sys.exit(1)
        
        df_data = pd.read_csv(csv_path)
        if "Open Time" not in df_data.columns:
            print("CSV dosyasında 'Open Time' kolonu yok, format uyumsuz olabilir.")
            sys.exit(1)
        
        df_data["Open Time"] = pd.to_datetime(df_data["Open Time"])
        print(f"Mevcut CSV dosyası yüklendi: {csv_path}")
    
    else:
        try:
            from config_f import api_key, api_secret
        except ImportError as e:
            print("config_f.py import edilemedi:", e)
            sys.exit(1)
        
        csv_filename = f"{instrument}_{period}_{start_date}.csv"
        df_data = download_data_from_binance(
            instrument=instrument,
            period=period,
            start_date=start_date,
            api_key=api_key,
            api_secret=api_secret,
            csv_filename=csv_filename
        )
    
    # Benzerlik analizini çalıştır
    df_results = analyze_similarity(df_data, n_bars=n_bars)
    
    # Tablo çıktısı
    if df_results.empty:
        print("Benzerlik analizi sonuç vermedi veya veri yetersiz.")
    else:
        print("\n--- Normalizasyon + Kaydırma Sonuçları ---")
        print(df_results)
