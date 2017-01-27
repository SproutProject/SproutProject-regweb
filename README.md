# SproutProject-regweb

Sprout 2016 registration website.

# Build Production Environment

測試環境: **ubuntu 14.04 & memory 2GB**

# Deployment

1. 更新、升級套件、設定時區

   ```bash
   sudo apt-get update
   sudo apt-get upgrade -y
   sudo dpkg-reconfigure tzdata
   ```

   選 **asia -> Taipei**

2. 安裝 Nginx

    ```bash
    sudo apt-get install nginx -y
    ```

3. 安裝 PostgreSQL

    ```bash
    sudo apt-get install postgresql postgresql-contrib -y
    ```
    
    新增帳號與資料庫
    
    ```bash
    sudo -i -u postgres
    psql
    CREATE USER regweb WITH PASSWORD 'regweb';
    CREATE DATABASE regweb;
    GRANT ALL PRIVILEGES ON DATABASE regweb TO regweb;
    \q
    exit
    ```
    
    修改 `/etc/postgresql/[version number]/main/pg_hba.conf` 內的設定（[ ]內依當前最新版本號而定）
    
    ```bash
    local   all             postgres                                peer
    ```
    
    改成
    
    ```bash
    local   all             postgres                                md5
    ```

    重新啟動 psql
    
    ```bash
    sudo service postgresql restart
    ```
    
4. 建立 Python3 虛擬環境

    安裝 python 3.5
    
    ```bash
    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get update
    sudo apt-get install python3.5 -y
    ```

    安裝 virtualenv
    
    ```bash
    sudo apt-get install python-virtualenv -y
    ```
    
    建立虛擬環境並啟用
    
    ```bash
    virtualenv -p python3.5 ENV3
    source ENV3/bin/activate
    ```
    
5. 建立報名網站

    首先安裝 `git`
    
    ```bash
    sudo apt-get install git -y
    ```
    
    Clone project 並放至 `/srv` 底下
    
    ```bash
    git clone https://github.com/SproutProject/SproutProject-regweb.git
    sudo mv SproutProject-regweb /srv/regweb
    ```
    
    安裝 python 所需 library 與套件
    
    ```bash
    sudo apt-get install libpython3.5-dev libpq-dev libffi6 libffi-dev -y
    cd /srv/regweb/python
    pip install -r requirements.txt
    ```
    
    複製範例設定檔（Tornado 與 Nginx）並進行設定
    
    ```bash
    cd /srv/regweb/nginx
    sudo cp sprout.example /etc/nginx/sites-available/sprout
    sudo ln -s /etc/nginx/sites-available/sprout /etc/nginx/sites-enabled/sprout
    cd /srv/regweb/python
    cp Config.py.example Config.py
    ```
    
    其中 `Config.py` 內 `HOST` 需與 nginx 的 `sprout` 檔內的 `server_name` 對應。
    
    修改完 Nginx 設定檔的 `server_name` 後需重啟 Nginx
    
    ```bash
    sudo service nginx restart
    ```
    
    `DB_*` 是跟 PostgreSQL 相關的設定。
    
    `SMTP_*` 是跟網站發信相關的設定：
    
    1. 基本上會用 `sprout@csie.ntu.edu.tw` 這個帳號去做發信用。
    2. `SMTP_HOST` 請設成 `smtp.gmail.com`，切記勿使用系上 smtp 作為發信用。
    3. `SMTP_SENDER` 是對方收信會看到寄件人的名稱。
    
    `GOOGLE_*` 是跟 google sheet 相關的設定：
    
    1. `GOOGLE_SPREAD_SHEET_ID`: 需先手動建一個 google sheet 並把 ID 設定給此變數，模板可參考[此連結](https://docs.google.com/spreadsheets/d/11Qq5rbkaO4TRscgBwHRc4r85NeAtA-If38XU9YEhDlY/)。
    2. 根據 [Python Quickstart](https://developers.google.com/sheets/api/quickstart/python) 中 STEP 1. 的步驟生成 `client_secret.json` 檔，放至 `/srv/regweb/python` 目錄下。
    3. `GOOGLE_REFRESH_TIME` 為更新表格的時間間隔，單位為秒
    
    `SECRET_KEY` 為 Tornado server cookie 加密用的 key，以及在 Tornado 內部發送更新 google sheet 的 key。
    
    `PRETEST_*` 為算法班預試相關的設定：
    
    1. `PRETEST_HOST` 為預試 cms 的網址。
    2. `PRETEST_SSO_LOGIN_PASSWORD` 為計算從報名網站登入 cms 系統的 hash key，請洽 cms 系統負責人。
    3. `PRETEST_THRESHOLD` 為算法班預試的門檻分數，預設為 300.0 分。
    
    `ENTRANCE_*` 為算法班入芽考相關的設定，同算法班預試。
    
    `DEADLINE` 為整個資訊之芽報名的截止日期，會在報名結束後擋掉備審問題的新增與修改。

6. 啟動報名網站

    第一次啟動 `Server.py` 時必須多加一個參數 `--noauth_local_webserver`，之後生成 google api 的 cache 檔案後就不用在加此參數。

    ```bash
    cd /srv/regweb/python
    python Server.py --noauth_local_webserver
    ```

7. 建立管理者帳號

    依照正常註冊帳號流程，註冊帳號後進入 PostgreSQL 內將指定的帳號 power 調成 2
    
    ```SQL
    UPDATE "user" SET "power"=2 WHERE "mail"='sprout@example.com'
    ```
    
    權限為 2 的帳號可在 `/spt/ass_god/` 頁面對其他帳號的權限進行調整，基本上應該會是由一個權限 2 的帳號去新增其他管理者帳號，其餘的管理者帳號權限為 1 時便可在 `/spt/ass/` 頁面去做關於報名的所有相關設定。