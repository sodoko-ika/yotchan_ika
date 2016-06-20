# yotchan_ika
IkaLogのWebSocketサーバ機能と連動して ナワバリバトルのタイムライン的なテキストを出力するスクリプトです。  
  
出力されたテキストファイルの中身を、YouTubeの動画説明欄にそのままコピペして保存すれば、時間のリンクが作成された形で閲覧できるハズです。  
（動画をアップした本人は、動画説明欄をクリックすると自動的に編集モードになると思うので注意してください。）  
  
今のところ、ナワバリバトルの処理しかありません。（ひたすらレギュラーマッチということで…）  
  
HH動作に必要なもの   
IkaLog CUI版に合わせた環境で作りました。Python 3.4で動作確認をしています。  
このスクリプトを動作させるのには下記のpipが必要だと思います。  
pip install ws4py  
pip install tornado  
  
HH使い方  
・WebSocketサーバ機能が動作するように設定されたIkaLogを起動後、マッチング開始までのタイミングでこのスクリプトを起動してください。  
・ステージ紹介～ジャッジくん登場までの間の流れが記録されて、バトルごとに ./20160228-0101.txt みたいな感じのファイルが出来るハズです。  
・IkaLogを終了させると、このスクリプトの動作も終わるハズです。  
・作成したファイルの削除機能は無いので、使用済みのファイルは手動で削除をお願いします。  
  
HH動作テストの方法  
1.WebSocketサーバ機能が動作するように設定されたWinIkaLogを準備してください。  
2.WinIkaLogのWebSocketサーバの設定に合わせて、このスクリプトのIPアドレスとポート番号を変更してください。  
3.WinIkaLogを起動後、このスクリプトを起動してください。  
4.おさんぽモードで、マサバ海峡大橋のような落下して自滅可能なステージを選択して、さんぽ開始後に場外へ落ちてください。  
5.IkaLogのコマンドプロンプトに 'やられた！' と表示されて、このスクリプトから '処理に必要な情報が取得できていません.()'というメッセージが表示されればOKです。  
ポート番号9090で駄目だった時は、IkaLogの設定含めて他の番号（例えば 8080とか）を試すとかすると通るかもしれません。  
