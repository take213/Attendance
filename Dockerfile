# ベースイメージとしてPython 3のDjangoイメージを使用
FROM python:3.8

# 環境変数を設定
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 作業ディレクトリを指定
WORKDIR /app

# 依存パッケージをインストール
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# ソースコードをコピー
COPY . /app/

# ポートを公開
EXPOSE 8000

# Djangoサーバーを起動
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
