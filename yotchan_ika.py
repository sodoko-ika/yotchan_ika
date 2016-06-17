#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""IkaLogのWebSocketServer機能と連動して、ナワバリバトルのタイムラインっぽいテキストを出力します.
"""

import csv
import json
import time
from datetime import datetime
from tornado import ioloop
from ws4py.client.tornadoclient import TornadoWebSocketClient

# ステージ名
STAGES = {
    'anchovy': {'ja': 'アンチョビットゲームズ', 'en': 'Ancho-V Games'},
    'arowana':  {'ja': 'アロワナモール', 'en': 'Arowana Mall'},
    'bbass':    {'ja': 'Bバスパーク', 'en': 'Blackbelly Skatepark'},
    'dekaline': {'ja': 'デカライン高架下', 'en': 'Urchin Underpass'},
    'hakofugu': {'ja': 'ハコフグ倉庫', 'en': 'Walleye Warehouse', },
    'hirame':   {'ja': 'ヒラメが丘団地', 'en': 'Flounder Heights', },
    'hokke':    {'ja': 'ホッケふ頭', 'en': 'Port Mackerel'},
    'kinmedai': {'ja': 'キンメダイ美術館', 'en': 'Museum d\'Alfonsino'},
    'mahimahi': {'ja': 'マヒマヒリゾート&スパ', 'en': 'Mahi-Mahi Resort', },
    'masaba':   {'ja': 'マサバ海峡大橋', 'en': 'Hammerhead Bridge', },
    'mongara':  {'ja': 'モンガラキャンプ場', 'en': 'Camp Triggerfish', },
    'mozuku':   {'ja':  'モズク農園', 'en': 'Kelp Dome', },
    'negitoro': {'ja': 'ネギトロ炭鉱', 'en': 'Bluefin Depot', },
    'shionome': {'ja': 'シオノメ油田', 'en': 'Saltspray Rig', },
    'shottsuru': {'ja': 'ショッツル鉱山', 'en': 'Piranha Pit'},
    'tachiuo':  {'ja':  'タチウオパーキング', 'en':  'Moray Towers', },
    }

# ルール名
RULES = {
    'nawabari': {'ja': 'ナワバリバトル', 'en': 'Turf War', },
    'area': {'ja': 'ガチエリア', 'en': 'Splat Zones', },
    'yagura': {'ja': 'ガチヤグラ', 'en': 'Tower Control', },
    'hoko': {'ja': 'ガチホコバトル', 'en': 'Rainmaker', },
    }

# やられ名
#\IkaLog\ikalog\constants.pyから引用させていただきました。
DICT_REASONS = {
    '52gal': {'ja': '.52ガロン', 'en': '.52 Gal'},
    '52gal_deco': {'ja': '.52ガロンデコ', 'en': '.52 Gal Deco'},
    '96gal': {'ja': '.96ガロン', 'en': '.96 Gal'},
    '96gal_deco': {'ja': '.96ガロンデコ', 'en': '.96 Gal Deco'},
    'bold': {'ja': 'ボールドマーカー', 'en': 'Sploosh-o-matic'},
    'bold_7': {'ja': 'ボールドマーカー7', 'en': 'Sploosh-o-matic 7'},
    'bold_neo': {'ja': 'ボールドマーカーネオ', 'en': 'Neo Sploosh-o-matic'},
    'dualsweeper': {'ja': 'デュアルスイーパー', 'en': 'Dual Squelcher'},
    'dualsweeper_custom': {'ja': 'デュアルスイーパーカスタム', 'en': 'Custom Dual Squelcher'},
    'h3reelgun': {'ja': 'H3リールガン', 'en': 'H-3 Nozzlenose'},
    'h3reelgun_cherry': {'ja': 'H3リールガンチェリー', 'en': 'Cherry H-3 Nozzlenose'},
    'h3reelgun_d': {'ja': 'H3リールガンD', 'en': 'H-3 Nozzlenose D'},
    'heroshooter_replica': {'ja': 'ヒーローシューターレプリカ', 'en': 'Hero Shot Replica'},
    'hotblaster': {'ja': 'ホットブラスター', 'en': 'Blaster'},
    'hotblaster_custom': {'ja': 'ホットブラスターカスタム', 'en': 'Custom Blaster'},
    'jetsweeper': {'ja': 'ジェットスイーパー', 'en': 'Jet Squelcher'},
    'jetsweeper_custom': {'ja': 'ジェットスイーパーカスタム', 'en': 'Custom Jet Squelcher'},
    'l3reelgun': {'ja': 'L3リールガン', 'en': 'L-3 Nozzlenose'},
    'l3reelgun_d': {'ja': 'L3リールガンD', 'en': 'L-3 Nozzlenose D'},
    'longblaster': {'ja': 'ロングブラスター', 'en': 'Range Blaster'},
    'longblaster_custom': {'ja': 'ロングブラスターカスタム', 'en': 'Custom Range laster'},
    'longblaster_necro': {'ja': 'ロングブラスターネクロ', 'en': 'Grim Range laster'},
    'momiji': {'ja': 'もみじシューター', 'en': 'Custom Splattershot Jr.'},
    'nova': {'ja': 'ノヴァブラスター', 'en': 'Luna Blaster'},
    'nova_neo': {'ja': 'ノヴァブラスターネオ', 'en': 'Luna Blaster Neo'},
    'nzap83': {'ja': 'N-ZAP83', 'en': 'N-ZAP \'83'},
    'nzap85': {'ja': 'N-ZAP85', 'en': 'N-ZAP \'85'},
    'nzap89': {'ja': 'N-ZAP89', 'en': 'N-Zap \'89'},
    'octoshooter_replica': {'ja': 'オクタシューターレプリカ', 'en': 'Octoshot Replica'},
    'prime': {'ja': 'プライムシューター', 'en': 'Splattershot Pro'},
    'prime_berry': {'ja': 'プライムシューターベリー', 'en': 'Berry Splattershot Pro'},
    'prime_collabo': {'ja': 'プライムシューターコラボ', 'en': 'Forge Splattershot Pro'},
    'promodeler_mg': {'ja': 'プロモデラーMG', 'en': 'Aerospray MG'},
    'promodeler_pg': {'ja': 'プロモデラーPG', 'en': 'Aerospray PG'},
    'promodeler_rg': {'ja': 'プロモデラーRG', 'en': 'Aerospray RG'},
    'rapid': {'ja': 'ラピッドブラスター', 'en': 'Rapid Blaster'},
    'rapid_deco': {'ja': 'ラピッドブラスターデコ', 'en': 'Rapid Blaster Deco'},
    'rapid_elite': {'ja': 'Rブラスターエリート', 'en': 'Rapid Blaster Pro'},
    'rapid_elite_deco': {'ja': 'Rブラスターエリートデコ', 'en': 'Rapid Blaster Pro Deco'},
    'sharp': {'ja': 'シャープマーカー', 'en': 'Splash-o-matic'},
    'sharp_neo': {'ja': 'シャープマーカーネオ', 'en': 'Neo Splash-o-matic'},
    'sshooter': {'ja': 'スプラシューター', 'en': 'Splattershot'},
    'sshooter_collabo': {'ja': 'スプラシューターコラボ', 'en': 'Tentatek Splattershot'},
    'sshooter_wasabi': {'ja': 'スプラシューターワサビ', 'en': 'Wasabi Splattershot'},
    'wakaba': {'ja': 'わかばシューター', 'en': 'Splattershot Jr.'},

    'carbon': {'ja': 'カーボンローラー', 'en': 'Carbon Roller'},
    'carbon_deco': {'ja': 'カーボンローラーデコ', 'en': 'Carbon Roller Deco'},
    'dynamo': {'ja': 'ダイナモローラー', 'en': 'Dynamo Roller'},
    'dynamo_burned': {'ja': 'ダイナモローラーバーンド', 'en': 'Tempered Dynamo Roller'},
    'dynamo_tesla': {'ja': 'ダイナモローラーテスラ', 'en': 'Gold Dynamo Roller'},
    'heroroller_replica': {'ja': 'ヒーローローラーレプリカ', 'en': 'Hero Roller Replica'},
    'hokusai': {'ja': 'ホクサイ', 'en': 'Octobrush'},
    'hokusai_hue': {'ja': 'ホクサイ・ヒュー', 'en': 'Octobrush Nouveau'},
    'pablo': {'ja': 'パブロ', 'en': 'Inkbrush'},
    'pablo_hue': {'ja': 'パブロ・ヒュー', 'en': 'Inkbrush Nouveau'},
    'pablo_permanent': {'ja': 'パーマネント・パブロ', 'en': 'Permanent Inkbrush'},
    'splatroller': {'ja': 'スプラローラー', 'en': 'Splat Roller'},
    'splatroller_collabo': {'ja': 'スプラローラーコラボ', 'en': 'Krak-On Splat Roller'},
    'splatroller_corocoro': {'ja': 'スプラローラーコロコロ', 'en': 'CoroCoro Splat Roller'},

    'bamboo14mk1': {'ja': '14式竹筒銃・甲', 'en': 'Bamboozler 14 MK I'},
    'bamboo14mk2': {'ja': '14式竹筒銃・乙', 'en': 'Bamboozler 14 MK II'},
    'bamboo14mk3': {'ja': '14式竹筒銃・丙', 'en': 'Bamboozler 14 Mk III'},
    'herocharger_replica': {'ja': 'ヒーローチャージャーレプリカ', 'en': 'Hero Charger Replica'},
    'liter3k': {'ja': 'リッター3K', 'en': 'E-liter 3K'},
    'liter3k_custom': {'ja': 'リッター3Kカスタム', 'en': 'Custom E-liter 3K'},
    'liter3k_scope': {'ja': '3Kスコープ', 'en': 'E-liter 3K Scope'},
    'liter3k_scope_custom': {'ja': '3Kスコープカスタム', 'en': 'Custom E-liter 3K Scope'},
    'splatcharger': {'ja': 'スプラチャージャー', 'en': 'Splat Charger'},
    'splatcharger_bento': {'ja': 'スプラチャージャーベントー', 'en': 'Bento Splat Charger'},
    'splatcharger_wakame': {'ja': 'スプラチャージャーワカメ', 'en': 'Kelp Splat Charger'},
    'splatscope': {'ja': 'スプラスコープ', 'en': 'Splatterscope'},
    'splatscope_bento': {'ja': 'スプラスコープベントー', 'en': 'Bento Splatterscope'},
    'splatscope_wakame': {'ja': 'スプラスコープワカメ', 'en': 'Kelp Splatterscope'},
    'squiclean_a': {'ja': 'スクイックリンα', 'en': 'Classic Squiffer'},
    'squiclean_b': {'ja': 'スクイックリンβ', 'en': 'New Squiffer'},
    'squiclean_g': {'ja': 'スクイックリンγ', 'en': 'Fresh Squiffer'},

    'bucketslosher': {'ja': 'バケットスロッシャー', 'en': 'Slosher'},
    'bucketslosher_deco': {'ja': 'バケットスロッシャーデコ', 'en': 'Slosher Deco'},
    'bucketslosher_soda': {'ja': 'バケットスロッシャーソーダ', 'en': 'Soda Slosher'},
    'hissen': {'ja': 'ヒッセン', 'en': 'Tri-Slosher'},
    'hissen_hue': {'ja': 'ヒッセン・ヒュー', 'en': 'Tri-Slosher Nouveau'},
    'screwslosher': {'ja': 'スクリュースロッシャー', 'en': 'Sloshing Machine'},
    'screwslosher_neo': {'ja': 'スクリュースロッシャーネオ', 'en': 'Sloshing Machine Neo'},

    'barrelspinner': {'ja': 'バレルスピナー', 'en': 'Heavy Splatling'},
    'barrelspinner_deco': {'ja': 'バレルスピナーデコ', 'en': 'Heavy Splatling Deco'},
    'barrelspinner_remix': {'ja': 'バレルスピナーリミックス', 'en': 'Heavy Splatling Remix'},
    'hydra': {'ja': 'ハイドラント', 'en': 'Hydra Splatling'},
    'hydra_custom': {'ja': 'ハイドラントカスタム', 'en': 'Custom Hydra Splatling'},
    'splatspinner': {'ja': 'スプラスピナー', 'en': 'Mini Splatling'},
    'splatspinner_collabo': {'ja': 'スプラスピナーコラボ', 'en': 'Zink Mini Splatling'},
    'splatspinner_repair': {'ja': 'スプラスピナーリペア', 'en': 'Refurbished Mini Splatling'},

    'chasebomb': {'ja': 'チェイスボム', 'en':  'Seeker', },
    'jumpbeacon': {'ja': 'ジャンプビーコン', 'en':  'Squid Beakon', },
    'kyubanbomb': {'ja': 'キューバンボム', 'en':  'Suction Bomb', },
    'pointsensor': {'ja': 'ポイントセンサー', 'en':  'Point Sensor', },
    'poison': {'ja': 'ポイズンボール', 'en':  'Disruptor', },
    'quickbomb': {'ja': 'クイックボム', 'en':  'Burst Bomb', },
    'splashbomb': {'ja': 'スプラッシュボム', 'en':  'Splat Bomb', },
    'splashshield': {'ja': 'スプラッシュシールド', 'en':  'Splash Wall', },
    'sprinkler': {'ja': 'スプリンクラー', 'en':  'Sprinkler', },
    'trap': {'ja': 'トラップ', 'en':  'Ink Mine', },

    'barrier': {'ja': 'バリア', 'en':  'Bubbler', },
    'bombrush': {'ja': 'ボムラッシュ', 'en':  'Bomb Rush', },
    'daioika': {'ja': 'ダイオウイカ', 'en':  'Kraken', },
    'megaphone': {'ja': 'メガホンレーザー', 'en':  'Killer Wail', },
    'supersensor': {'ja': 'スーパーセンサー', 'en':  'Echolocator', },
    'supershot': {'ja': 'スーパーショット', 'en':  'Inkzooka', },
    'tornado': {'ja': 'トルネード', 'en':  'Inkstrike', },

    'hoko_shot': {'ja': 'ガチホコショット', 'en': 'Rainmaker Shot', },
    'hoko_barrier': {'ja': 'ガチホコバリア', 'en': 'Rainmaker Shield', },
    'hoko_inksplode': {'ja': 'ガチホコ爆発', 'en': 'Rainmaker Inksplode', },

    'propeller': {'ja': 'プロペラから飛び散ったインク', 'en': 'Ink from a propeller'},

    'oob': {'ja': '三三(.ω.)三 場外に落ちた！', 'en': 'Out of Bounds', },
    'fall': {'ja': '三三(.ω.)三 奈落に落ちた！', 'en': 'Fall', },
    'drown': {'ja': '三三(.ω.)三 水場に落ちた！', 'en': 'Drowning', },
    }

#ギア効果
GEAR_ABILITIES = {
    'bomb_range_up': {'ja': 'ボム飛距離アップ', 'en': 'Bomb Range Up'},
    'bomb_sniffer': {'ja': 'ボムサーチ', 'en': 'Bomb Sniffer'},
    'cold_blooded': {'ja': 'マーキングガード', 'en': 'Cold Blooded'},
    'comeback': {'ja': 'カムバック', 'en': 'Comeback'},
    'damage_up': {'ja': '攻撃力アップ', 'en': 'Damage Up'},
    'defense_up': {'ja': '防御力アップ', 'en': 'Defense Up'},
    'empty': {'ja': '空', 'en': 'Empty'},
    'haunt': {'ja': 'うらみ', 'en': 'Haunt'},
    'ink_recovery_up': {'ja': 'インク回復力アップ', 'en': 'Ink Recovery Up'},
    'ink_resistance_up': {'ja': '安全シューズ', 'en': 'Ink Resistance'},
    'ink_saver_main': {'ja': 'インク効率アップ（メイン）', 'en': 'Ink Saver (Main)'},
    'ink_saver_sub': {'ja': 'インク効率アップ（サブ）', 'en': 'Ink Saver (Sub)'},
    'last_ditch_effort': {'ja': 'ラストスパート', 'en': 'Last-Ditch Effort'},
    'locked': {'ja': '未開放', 'en': 'Locked'},
    'ninja_squid': {'ja': 'イカニンジャ', 'en': 'Ninja Squid'},
    'opening_gambit': {'ja': 'スタートダッシュ', 'en': 'Opening Gambit'},
    'quick_respawn': {'ja': '復活時間短縮', 'en': 'Quick Respawn'},
    'quick_super_jump': {'ja': 'スーパージャンプ時間短縮', 'en': 'Quick Super Jump'},
    'recon': {'ja': 'スタートレーダー', 'en': 'Recon'},
    'run_speed_up': {'ja': 'ヒト移動速度アップ', 'en': 'Run Speed Up'},
    'special_charge_up': {'ja':  'スペシャル増加量アップ', 'en': 'Special Charge Up'},
    'special_duration_up': {'ja':  'スペシャル時間延長', 'en': 'Special Duration Up'},
    'special_saver': {'ja':  'スペシャル減少量ダウン', 'en': 'Special Saver'},
    'stealth_jump': {'ja':  'ステルスジャンプ', 'en': 'Stealth Jump'},
    'swim_speed_up': {'ja':  'イカダッシュ速度アップ', 'en': 'Swim Speed Up'},
    'tenacity': {'ja':  '逆境強化', 'en': 'Tenacity'}
    }

#ギアのブランド
GEAR_BRANDS = {
    'amiibo':     {'ja': 'amiibo', 'en': 'amiibo', },
    'cuttlegear': {'ja': 'アタリメイド', 'en': 'Cuttlegear', },
    'famitsu':    {'ja': 'ファミ通', 'en': 'Famitsu', },
    'firefin':    {'ja': 'ホッコリー', 'en': 'Firefin', },
    'forge':      {'ja': 'Forge', 'en': 'Forge', },
    'inkline':    {'ja': 'Inkline', 'en': 'Inkline', },
    'kog':        {'ja': 'KOG', 'en': 'KOG', },
    'krakon':     {'ja': 'クラーゲス', 'en': 'Krak-On', },
    'rockenberg': {'ja': 'ロッケンベルグ', 'en': 'Rockenberg', },
    'skalop':     {'ja': 'ホタックス', 'en': 'Skalop', },
    'splashmob':  {'ja': 'ジモン', 'en': 'Splash Mob', },
    'squidforce': {'ja': 'バトロイカ', 'en': 'Squidforce', },
    'squidgirl':  {'ja': '侵略！イカ娘', 'en': 'SQUID GIRL', },
    'takoroka':   {'ja': 'ヤコ', 'en': 'Takoroka', },
    'tentatek':   {'ja': 'アロメ', 'en': 'Tentatek', },
    'zekko':      {'ja': 'エゾッコ', 'en': 'Zekko', },
    'zink':       {'ja': 'アイロニック', 'en': 'Zink', },
    }

# 勝ち負け
DICT_JUDGES = {
    'win':  '勝ちました！',
    'lose': '負けました…',
    }

# 出力するメッセージの内容
# eventで判定するロジックを追加した時は、対応する内容を合わせて追加すること。
# キラキラ系の顔文字を使いたかったのですが、使うと動かなくなりました。文字コードの処理が良くわかりません。
#oob系のメッセージは、DICT_REASONS {}に移動しました。
DICT_MESSAGES = {
    'on_game_go_sign': "ε(*'-')з彡 バトルスタート！",
    'on_death_reason_identified': "ﾉ*(≧Д≦)★ %sでやられた！",
    'on_game_killed': "v(`ω´)ﾉ ☆ プレイヤーをたおした！",
    'on_result_judge': "(*ΦωΦ)ﾉ◇ ジャッジくんの結果発表！",
    'on_result_detail': "%sの%sで%s ブキは%s %dp %dk/%ddでした。",
    'unknown': "しらないブキ",
    }

class Structures:
    u""" on_game_start'のタイミングで取得出来る値を処理内で持ちまわる
    start_time:記録開始
    file_handle:ファイル
    stage_name:ステージ日本語名
    rulr_name :ルール日本語名
    death_time:やられ初期通知の時刻
    rulr_name :表示用勝ち/負け
    """
    start_time = datetime.now()
    file_handle = None
    stage_name = 'わからない場所'
    rule_name = 'わからないルール'
    death_time = datetime.now()
    judge = '勝ち負け不明'

def dt2sec(date_time):
    u"""エポックからの経過秒数に変換 """
    ret = int(time.mktime(datetime.timetuple(date_time)))
    return ret

def get_reason_name(reason_code):
    u"""やられ内容の日本語対応を取得する """
    if reason_code in DICT_REASONS:
        reason_name = DICT_REASONS[reason_code]['ja']
    else:
        reason_name = DICT_MESSAGES['unknown']
    return reason_name

def output_message_processing(event, battle_st):
    u"""メッセージをタイムラインっぽく整形してファイルに書き出す＆print() """
    event_code = event['event']

    # やられた時の時刻は初期通知のものを使う
    if event_code == 'on_death_reason_identified':
        result = dt2sec(battle_st.death_time) - dt2sec(battle_st.start_time)
    else:
        result = dt2sec(datetime.now()) - dt2sec(battle_st.start_time)

    #result = result - 0    #自動録画の内容とタイムラインのタイミングにズレが発生する場合に調整できるように（秒数を指定）
    min_sec = '%02d:%02d' % (result // 60, result - (result // 60) * 60)
    msg = '%s %s\n' % (min_sec, DICT_MESSAGES[event_code])

    # やられた時
    if event_code == 'on_death_reason_identified':
        reason_code = event['reason']
        reason_name = get_reason_name(reason_code)
        if reason_code in ('oob', 'fall', 'drown'):
            #場外・転落・水死
            msg = '%s %s\n' % (min_sec, reason_name)
        else:
            msg = msg % reason_name

    # ジャッジくん
    if event_code == 'on_result_judge':
        battle_st.judge = DICT_JUDGES[event['judge']]  #勝ち負けは、リザルトで出しています。

    # リザルト
    # 例：キンメダイ美術館のナワバリバトルで勝ちました！ ブキはプライムシューター 999p 0k/1dでした。
    if event_code == 'on_result_detail':
        if event['score'] is None:  #フェスマッチは、塗りポイントが無かったような気がするので、判定してメッセージを別に記述（必要無いかも）
            msg = '%sの%sで%s ブキは%s %dk/%ddでした。'
            msg = msg % (battle_st.stage_name, battle_st.rule_name, battle_st.judge, \
                get_reason_name(event['weapon']), event['kills'], event['deaths'])
        else:
            msg = msg % (battle_st.stage_name, battle_st.rule_name, battle_st.judge, \
                get_reason_name(event['weapon']), event['score'], event['kills'], event['deaths'])

    battle_st.file_handle.write(msg)
    print(msg.strip())

def abilities_code_swap(code):
    u"""注意①　　通常は使わない機能です。
    キャプチャー環境の違いにより、実際とは違う認識をしている時にコードを入れ替える
    サブスロットには付かない効果で認識している＆一定の法則性がある時のみ有効かも。
    """
    swap_codes = {
        'recon':  'ink_recovery_up',
        'ink_resistance_up': 'run_speed_up',
    }
    if code in swap_codes:
        return swap_codes[code]
    else:
        return code

def downie_lottery(event):
    u"""ダウニーガチャ ログ作成
    ファイル形式は CSV、
    '日時',  'ブランド名',  'ギアレベル',  'スロット1',  'スロット2',  'スロット3'
    発生しないと思いますが、コードに対応する名称が無いときはコードを代入しています。
    """
    dat = [datetime.now().strftime("%Y/%m/%d %H:%M:%S"), '不明', 0]
    #ブランド名
    brand_code = ''
    if not event['gear_brand'] is None:
        brand_code = event['gear_brand']
    if not GEAR_BRANDS[brand_code]['ja'] is None:
        dat[1] = GEAR_BRANDS[brand_code]['ja']
    else:
        dat[1] = brand_code

    #gear_level
    if not  event['gear_level'] is None:
        dat[2] = event['gear_level']

    #スロット1~3
    slot = ['不明', '不明', '不明']
    for i, abilities_code in enumerate(event['sub_abilities']):
        #abilities_code = abilities_code_swap(abilities_code)    #注意①参照
        if not GEAR_ABILITIES[abilities_code]['ja'] is None:
            slot[i] = GEAR_ABILITIES[abilities_code]['ja']
        else:
            slot[i] = abilities_code

    with open('downie_lottery.csv', 'a') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(dat + slot)
        print(dat + slot)

#
class MyClient(TornadoWebSocketClient):
    u"""イベントに合わせてバトルのタイムラインっぽいものを作成する部分
    event_lists = {}に記載した文字列でイベントを判定
    on_game_go_sign: バトル開始！
    on_death_reason_identified: やられた！
    on_game_killed: たおした！
    on_result_judge: ジャッジくん
    on_result_detail: リザルト
    """
    def received_message(self, message):
        event = json.loads(str(message))
        #print(event)

        # バトル開始前のステージ紹介　記録開始
        if event['event'] == 'on_game_start':
            global BATTLE_ST   #何故か global にしないと動かない…
            BATTLE_ST = Structures

            #ステージの日本語名を取得
            if event['stage'] in STAGES:
                BATTLE_ST.stage_name = STAGES[event['stage']]['ja']

            #ルールの日本語名を取得
            if event['rule'] in RULES:
                BATTLE_ST.rule_name = RULES[event['rule']]['ja']

            #記録開始日時
            BATTLE_ST.start_time = datetime.now()

            # ファイル名は記録開始の年月日-時分 20160226-2201.txt みたいな感じで出力しています。
            BATTLE_ST.file_handle = \
                                  open('%s.txt' % BATTLE_ST.start_time.strftime("%Y%m%d-%H%M"), 'w')
            print('\n%sの%s記録開始 (%s)\n' % \
                  (BATTLE_ST.stage_name, BATTLE_ST.rule_name, BATTLE_ST.file_handle.name))

        try:
            # 表示用に、やられ通知の時刻を記憶
            if event['event'] == 'on_game_dead':
                BATTLE_ST.death_time = datetime.now()

            # ここの判定項目を増やした時は、DICT_MESSAGES = {}に対応する値を設定しないと（そのままでは）駄目
            event_lists = {
                'on_game_go_sign',
                'on_death_reason_identified',
                'on_game_killed',
                'on_result_judge',
                'on_result_detail'
                }
            if event['event'] in event_lists:
                output_message_processing(event, BATTLE_ST)

            #ダウニーガチャのログを作成する部分
            if event['event'] == 'on_inkopolis_lottery':
                downie_lottery(event)
        except:
            print('処理に必要な情報が取得できていません.(%s)' % event['event'])

        # 記録終了
        if event['event'] == 'on_game_session_end':
            print('\n(%s) 記録終了' % BATTLE_ST.file_handle.name)
            BATTLE_ST.file_handle.close()

    #
    def closed(self, code, reason=None):
        ioloop.IOLoop.instance().stop()

if __name__ == '__main__':
    # 文字によってエラーになってしまう現象の対応方法が分からないので、変更した時は一度表示して動作確認
    #for code in DICT_MESSAGES:
    #    print(DICT_MESSAGES[code])

    print('(%s) WebSocket 受信を開始します.' % __file__)

    #IPアドレスとポートを環境に合わせて変更してください.
    # WS = MyClient('ws://192.168.1.11:9090/ws', protocols=['http-only', 'chat'])
    WS = MyClient('ws://127.0.0.1:9090/ws', protocols=['http-only', 'chat'])
    WS.connect()
    ioloop.IOLoop.instance().start()
