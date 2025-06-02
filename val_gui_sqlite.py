import tkinter as tk
from tkinter import ttk
import pandas as pd
from sqlalchemy import create_engine
from pandastable import Table, TableModel
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ValorantStatsApp:
    def __init__(self, master):
        # 建立視窗
        self.master = master
        self.master.title('選手數據查詢')
        self.master.geometry('1150x650+400+250')
        # 資料庫連線
        self.engine = create_engine("sqlite:///vlrgg.db")
        # 隊名、地區清單
        self.team_list = self.get_team_list()
        self.region_list = self.get_region_list()
        # 查詢列及資料表
        self.create_query_frame()
        self.create_table()
    
    # 隊伍列表
    def get_team_list(self, region=None):
        sql = "SELECT DISTINCT Team FROM valorant_stats"
        params = None
        if region:
            sql += " WHERE Region = ?"
            params = (region,)
        return pd.read_sql(sql, self.engine, params=params)['Team'].tolist()
    
    # 地區列表
    def get_region_list(self):
        sql = "SELECT DISTINCT Region FROM valorant_stats"
        return pd.read_sql(sql, self.engine)['Region'].tolist()
    
    # 查詢列
    def create_query_frame(self):
        # 查詢區塊
        frame = tk.Frame(self.master)
        frame.grid(row=0, column=0, columnspan=7, padx=10, pady=5)
        
        # 選手名查詢
        # 標籤
        tk.Label(frame, text='選手名稱:').grid(row=0, column=0, padx=10)
        # 輸入框
        self.entry_player = tk.Entry(frame)
        self.entry_player.grid(row=0, column=1, padx=10)
        self.entry_player.bind("<Return>", self.search_player)
        # 按鈕
        self.search_button = tk.Button(frame, text='查詢', command=self.search_player)
        self.search_button.grid(row=0, column=2, padx=10)
        
        # Agent查詢
        # 標籤
        tk.Label(frame, text='使用角色:').grid(row=0, column=3, padx=10)
        # 輸入框
        self.entry_agent = tk.Entry(frame)
        self.entry_agent.grid(row=0, column=4, padx=10)
        self.entry_agent.bind("<Return>", self.search)
        # 按鈕
        self.search_button = tk.Button(frame, text='查詢', command=self.search)
        self.search_button.grid(row=0, column=5, padx=10)
        
        
        # 隊伍名查詢
        # 標籤
        tk.Label(frame, text='隊伍:').grid(row=0, column=6, padx=10)
        # 下拉清單
        self.combo_team = ttk.Combobox(frame, values=['ALL'] + self.team_list, state="readonly")
        self.combo_team.set("ALL")
        self.combo_team.grid(row=0, column=7, padx=10)
        self.combo_team.bind("<<ComboboxSelected>>", self.search)
        
        # 地區名查詢
        # 標籤
        tk.Label(frame, text='賽區:').grid(row=0, column=8, padx=10)
        # 下拉清單
        self.combo_region = ttk.Combobox(frame, values=['ALL'] + self.region_list, state="readonly")
        self.combo_region.set('ALL')
        self.combo_region.grid(row=0, column=9, padx=10)
        self.combo_region.bind("<<ComboboxSelected>>", self.select_region)
        
        # reset按鈕
        self.search_button = tk.Button(frame, text='重設', command=self.reset)
        self.search_button.grid(row=0, column=10, padx=10)
    
    # 資料表
    def create_table(self):
        # 表頭
        self.columns = ['Player', 'Team', 'Region', 'Agents', "Rating", "ACS", "KD", 'KAST', 'ADR',
                        'KPR', 'APR', 'FKPR', 'FDPR', 'HS', 'CL']
        thead = pd.DataFrame([[''] * len(self.columns)], columns=self.columns)
        # 建立表格框架
        table_frame = tk.Frame(self.master)
        table_frame.grid(row=1, column=0, columnspan=11, sticky="nsew", padx=5, pady=8)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        # pandastable
        self.pt = Table(table_frame, dataframe=thead, editable=False)
        self.pt.show()
        self.pt.bind("<Double-Button-1>", self.open_personal_page)
    
    # 依條件查詢
    def search(self, event=None):
        player = self.entry_player.get().strip()
        agent = self.entry_agent.get().strip()
        team = self.combo_team.get()
        region = self.combo_region.get()

        sql = '''SELECT Player, Team, Region, Agents, Rating, ACS, KD, KAST, ADR, 
        KPR, APR, FKPR, FDPR, HS, CL FROM valorant_stats WHERE 1=1'''
        params = []
        
        if player:
            sql += " AND Player LIKE ?"
            params.append(f"%{player}%")
            
        if agent:
            sql += " AND Agents LIKE ?"
            params.append(f"%{agent}%")

        if team and team != "ALL":
            sql += " AND Team = ?"
            params.append(team)

        if region and region != "ALL":
            sql += " AND Region = ?"
            params.append(region)

        df = pd.read_sql(sql, self.engine, params=tuple(params) if params else None)
        self.pt.updateModel(TableModel(df))
        self.pt.redraw()
    
    # 查詢選手    
    def search_player(self, event=None):
        player = self.entry_player.get().strip()
        if player:
            self.combo_team.set('ALL')
            self.combo_region.set('ALL')
            self.entry_agent.delete(0, tk.END)
            self.search()
            self.entry_player.delete(0, tk.END)
    
    # 選擇地區
    def select_region(self, event=None):
        region = None if self.combo_region.get() == 'ALL' else self.combo_region.get()
        new_team_list = self.get_team_list(region)
        self.combo_team['values'] = ['ALL'] + new_team_list
        self.combo_team.set('ALL')
        self.search()
        
    # 清空所有查詢
    def reset(self):
        self.combo_team.set('ALL')
        self.combo_region.set('ALL')
        self.entry_player.delete(0, tk.END)
        self.entry_agent.delete(0, tk.END)
        self.search()
    
    # 個人頁面
    def show_player_page(self, player_name):
        # 查詢該選手資料
        sql = "SELECT * FROM valorant_stats WHERE Player = ?"
        df = pd.read_sql(sql, self.engine, params=(player_name,))
        sql_2 = "SELECT * FROM personal_stats WHERE Player = ?"
        df2 = pd.read_sql(sql_2, self.engine, params=(player_name,))
        
        # 建立新視窗
        new_win = tk.Toplevel(self.master)
        new_win.title(player_name)
        new_win.geometry("800x600+500+250")
        new_win.grid_rowconfigure(1, weight=1)
        new_win.grid_columnconfigure(0, weight=1)
        
        # 上半區塊: 照片+雷達圖
        top_frame = tk.Frame(new_win)
        top_frame.grid(row=0, column=0, padx=20, pady=10)
    
        # 顯示圖片
        img_path = df.loc[0]['Picture']
        try:
            img = Image.open(img_path)
            img = img.resize((200, 200))
            photo = ImageTk.PhotoImage(img)
            label_img = tk.Label(top_frame, image=photo)
            label_img.image = photo
            label_img.grid(row=0, column=0, padx=20, pady=10)
        except:
            tk.Label(top_frame, text='圖片載入失敗').grid(row=0, column=0, padx=10)
            
        # 顯示雷達圖
        try:
            fig = self.create_radar_chart(player_name)
            # 建立FigureCanvasTkAgg 物件
            canvas = FigureCanvasTkAgg(fig, master=top_frame)
            canvas.draw()
            # 建立tkinter widget 元件
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.configure(width=350, height=350)
            canvas_widget.grid(row=0, column=1, padx=20, pady=10)
        except:
            tk.Label(top_frame, text='雷達圖載入失敗').grid(row=0, column=1, padx=10)
    
        # 下半區塊: 數據表格
        bottom_frame = tk.Frame(new_win)
        bottom_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        bottom_frame.grid_propagate(False) # 禁止自動調整大小
        
        pt = Table(bottom_frame, dataframe=df2, editable=False)
        pt.show()

    # 做雷達圖 
    def create_radar_chart(self, player):
        # 讀取資料
        df = pd.read_sql("SELECT Player, Team, Region, Rating, ACS, KD, KAST, FKPR, FDPR FROM valorant_stats", self.engine)
        # 指標欄位
        df['FKD'] = df['FKPR'] - df['FDPR']
        metrics = ['Rating', 'ACS', 'KD', 'KAST', 'FKD']

        # 標準化
        scaler = MinMaxScaler()
        df[metrics] = scaler.fit_transform(df[metrics])

        # 取選手數據
        labels = metrics
        player_name = player
        player_data = df[df['Player'] == player_name][metrics].values.flatten()

        # 補一個值讓雷達圖首尾相連
        values = np.append(player_data, player_data[0])
        # 座標弧度
        angles = np.linspace(0, 2 * np.pi, len(labels) + 1)

        # 建立極座標圖
        fig, ax = plt.subplots(figsize=(3, 3), subplot_kw={'polar': True})
        ax.plot(angles, values, linewidth=2, label=player_name)
        ax.fill(angles, values, alpha=0.25)                 # 填滿
        ax.set_thetagrids(angles[:-1] * 180/np.pi, labels)  # 軸標籤
        # ax.set_title(f"{player_name}", fontweight='bold')   # 標題
        ax.set_ylim(0, 1)                                   # y軸區間
        ax.set_yticklabels([])                              # 清除y軸標籤
        ax.set_aspect('equal')                              # 等比例
        fig.tight_layout()                                  # 自動調整間距
        return fig
    
    # 開啟選手個人頁面
    def open_personal_page(self, event):
        rowclicked = self.pt.get_row_clicked(event)
        if rowclicked is not None:
            player_name = self.pt.model.df.loc[rowclicked]['Player']
            self.show_player_page(player_name)


# 執行主程式
if __name__ == "__main__":
    win = tk.Tk()
    app = ValorantStatsApp(win)
    win.mainloop()