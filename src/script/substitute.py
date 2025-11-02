# References
# https://jinja.palletsprojects.com/en/stable/
# https://omomuki-tech.com/archives/1370

from jinja2 import Environment, FileSystemLoader
import os

def template(file: str) -> str:
    # テンプレートファイルがあるディレクトリのパス
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    # 1. 環境(Environment)の作成と設定
    # FileSystemLoader: 指定されたディレクトリからテンプレートをロードする
    env = Environment(loader=FileSystemLoader(template_dir))
    # 2. テンプレートのロード (ファイル名を指定)
    template = env.get_template(file)
    # 3. レンダリング
    data = { 
            "greeting_message": "ようこそ！", 
            "username": "Pythonista"
    }
    output = template.render(data)
    # output にはレンダリングされたHTML文字列が入る
    print(output)
    # 必要であればファイルに書き出す
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(output)
    return output

if __name__ == "__main__":

