#!/usr/bin/env python3

import re
import subprocess

# MACアドレスとベンダの対応表のデータベースをCSVファイルから作成(辞書のリスト)
def make_vendorlist(dbfilename):
    db = []
    with open(dbfilename, 'r', encoding='utf-8') as dbf:
        for line in dbf.readlines():
            (macprefix, vendor) = line.split(',')[0:2]
            db.append({ 'macprefix' : macprefix.lower(), 'vendor' : vendor })
    return db

# 家庭内の既知デバイスのMACアドレスリストを作成
def make_knowndevicelist(listfilename):
    ours = []
    with open(listfilename, 'r', encoding='utf-8') as inf:
        for line in inf.readlines():
            # コメント行はスキップする
            if line.startswith('#') or line == '\n':
                continue
            ours.append(line.split(',')[0])
    return ours

# MACアドレスからベンダーを検索する
def lookup_vendor(macaddr, db):
    prefix = re.findall('([0-9A-Za-z]+:[0-9A-Za-z]+:[0-9A-Za-z]+):[0-9A-Za-z]+:[0-9A-Za-z]+:[0-9A-Za-z]+', macaddr)[0]
    for ent in db:
        if prefix == ent['macprefix']:
            return ent['vendor']
    return None

# MACアドレスのフォーマットの統一
# 省略された"0"を補完する
def fix_macaddr(macaddr):
    octets = macaddr.split(':')
    fixed_octes = []
    for ch in octets:
        if len(ch) != 2:
            ch = '0' + ch
        fixed_octes.append(ch)
    return ':'.join(fixed_octes)

def main():
    # ベンダーDBの作成
    db = make_vendorlist('mac-vendors-export.csv')
    # 既知デバイスMACアドレスリストの作成
    ours = make_knowndevicelist('ourdevices.csv')

    # サブネット全範囲のIPアドレスにPingしてOSのARPエントリを作成する
    for n in range(0,256):
        ipaddr = "192.168.5." + str(n)
        pingcmd = ['/sbin/ping', '-c', '1', '-t', '1', ipaddr]
        subprocess.run(pingcmd)

    # ARPテーブル内容の取得
    cp = subprocess.run(['/usr/sbin/arp', '-a', '-i', 'en1'], encoding='utf-8', stdout=subprocess.PIPE)

    unknowns = []
    # 得られたMACアドレス一覧を照合
    for entry in cp.stdout.splitlines():
        # arpコマンドの結果からMACアドレス部分を取り出し
        ip, dummy, macaddr = entry.split()[1:4]
        macaddr = fix_macaddr(macaddr)
        if 'incomplete' in macaddr:
            continue
        # 検出したMACアドレスが既知リスト内にあるかをチェック
        if macaddr not in ours:
            # 未知のMACアドレスを発見！
            vendor = lookup_vendor(macaddr, db)
            unknowns.append({ 'ip': ip, 'macaddr' : macaddr, 'vendor': vendor})

    # 結果の表示
    for ent in unknowns:
        print("{0} on {1} : {2}".format(ent['macaddr'], ent['ip'], ent['vendor']))

if __name__ == "__main__":
    main()