# valorant數據查詢介面

## 專案簡介

本專案提供一個簡潔的圖形化介面，讓使用者可查詢 VALORANT VCT 聯賽選手的數據表現。  
選手數據由 [VLR.GG](https://www.vlr.gg/) 網站擷取，並透過資料視覺化與 GUI 呈現，方便快速查詢與分析。


## 主要功能

- 以選手名、隊伍、賽區、使用角色為條件查詢選手本賽季平均數據
- 主畫面顯示查詢結果表格，可條件篩選與按欄位排序
- 點選選手可進入個人頁面，顯示：
  - 選手照片
  - 選手五維雷達圖
  - 數據細項總覽
- 圖形化介面（GUI），操作直覺、查詢快速


## 使用技術

- **Python 3.x**
- **網路爬蟲**：`requests`, `BeautifulSoup`
- **資料處理**：`pandas`, `numpy`, `re`, `unicodedata`
- **資料庫操作**：`SQLAlchemy`, `SQLite`
- **數據視覺化**：`matplotlib`, `scikit-learn`
- **圖形化介面**：`tkinter`, `pandastable`, `Pillow`


## 執行方式

1. 安裝必要套件:
pip install -r requirements.txt

2. 執行爬蟲腳本（產生資料庫與照片）:
python val_crawler_sqlite.py

3. 執行 GUI 程式:
python val_gui_sqlite.py


## 資料來源

本專案所使用的數據與圖片資料來自以下網站：

- [VLR.GG](https://www.vlr.gg/)
- [VALORANT Esports 官方網站](https://valorantesports.com)

僅作為學術與學習使用，無任何商業用途。