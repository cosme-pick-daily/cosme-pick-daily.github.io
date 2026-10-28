# cosme-pick-daily.github.io
美容アイテムの紹介ページ（広告を含みます）

公開URL: https://cosme-pick-daily.github.io/

## 商品の追加

```
python scripts/add_product.py --name "商品名" --price 1980 --image "https://..." --url "https://hb.afl.rakuten.co.jp/..." --push
```

`data/products.json` に追記され、`--push` を付けるとそのファイルだけを commit して push します。

## ローカル確認

```
python -m http.server 8000
```

http://localhost:8000/ を開く（ファイルを直接開くと JSON が読み込めません）。
