import os
import shutil
from flask import Flask, send_from_directory, abort, render_template
import subprocess

# リポジトリをクローンするディレクトリ
temp_dir = "/tmp/nebula_repo"

# リポジトリのクローンとセットアップを行う
def clone_and_setup_repo():
    # 一時ディレクトリが存在する場合は削除
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    print("Cloning the repository...")
    result = os.system(f"git clone https://github.com/izum00/Alu.git --recursive {temp_dir}")
    
    if result != 0:
        print("Error: Failed to clone the repository.")
        return

    # クローンしたディレクトリに移動してセットアップ
    os.chdir(temp_dir)
    os.system("npm i")
    os.system("cp .env.example .env")
    os.system("npm i -g pnpm")
    os.system("pnpm i")
    os.system("npm run build")
    os.system("npm start")
    os.system("npm restart")

    # index.htmlをカレントディレクトリに移動
    index_html_path = os.path.join(temp_dir, 'index.html')
    if os.path.exists(index_html_path):
        if os.path.exists('index.html'):
            os.remove('index.html')
        shutil.move(index_html_path, '.')

# クローンとセットアップを実行
clone_and_setup_repo()

# Flaskアプリケーションの設定
app = Flask(__name__, template_folder=os.path.join(temp_dir, 'views'))

# ルートでindex.htmlを表示
@app.route('/')
def index():
    # index.htmlがリポジトリ内のviewsディレクトリに存在しない場合は404エラー
    index_html_path = os.path.join(temp_dir, 'views', 'index.html')
    if not os.path.exists(index_html_path):
        print("index 404")
        return abort(404, description="index.html not found.")

    # Flaskのテンプレートエンジンを使ってindex.htmlをレンダリング
    return render_template('index.html')

# 静的ファイルを提供するためのルート
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(temp_dir, 'views'), filename)

# main.jsの存在を確認するエンドポイント
@app.route('/check_main_js')
def check_main_js():
    if os.path.exists(os.path.join(temp_dir, 'static', 'main.js')):
        return "main.js exists."
    else:
        return "main.js does not exist."

if __name__ == '__main__':
    # port 7860でFlaskアプリを起動
    app.run(host='0.0.0.0', port=7860)
