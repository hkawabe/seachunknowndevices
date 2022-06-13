#!/usr/bin/env python3

import re
import subprocess

# MACアドレスとベンダの対応表のデータベース作成(辞書のリスト)
def make_vendorlist(dbfilename):
    db = []
    with open(dbfilename, 'r', encoding='utf-8') as dbf:
        for line in dbf.readlines():
            (macprefix, vendor) = line.split(',')[0:2]
            db.append({ 'macprefix' : macprefix, 'vendor' : vendor })
    return db

# MACアドレスからベンダーを検索する
def lookup_vendor(macaddr, db):
    prefix = re.findall('([0-9a-z]{2}:[0-9a-z]{2}:[0-9a-z]{2}):[0-9a-z]{2}:[0-9a-z]{2}:[0-9a-z]{2}', macaddr)
    for i in db:
        print(i['macprefix'])
        #if prefix == i['macprefix']
          #  return i['vendor']
    return None

def main():

    # ベンダーDBの作成
    db = make_vendorlist('mac-vendors-export.csv')

    # 家庭内の既知デバイスのMACアドレスリストを作成
    ours = []
    with open('ourdevices.csv', 'r', encoding='utf-8') as inf:
        for line in inf.readlines():
            # コメント行はスキップする
            if line.startswith('#') or line == '\n':
                continue
            ours.append(line.split(',')[0])

    # サブネット全範囲のIPアドレスにPingしてOSのARPエントリを作成する
#    for n in range(0,256):
#        ipaddr = "192.168.5." + str(n)
#        pingcmd = ['/sbin/ping', '-c', '1', '-t', '1', ipaddr]
#        subprocess.run(pingcmd)

    # ARPテーブル内容の取得
    cp = subprocess.run(['/usr/sbin/arp', '-a', '-i', 'en1'], encoding='utf-8', stdout=subprocess.PIPE)

    # 得られたMACアドレス一覧を照合
    for entry in cp.stdout.splitlines():
        # arpコマンドの結果からMACアドレス部分を取り出し
        macaddr = entry.split()[3]

        # "0: 11:32: bb:1e: f3"みたいなものを"00: 11:32: bb:1e: f3"の形に修正する
        if len(macaddr.split(':')[0]) == 1:
            macaddr = '0' + macaddr
        # 検出したMACアドレスが既知リスト内にあるかをチェック
        if macaddr not in ours:
            # 未知のMACアドレスを発見！
            vendor = lookup_vendor(macaddr, db)
            print(macaddr, vendor)

if __name__ == "__main__":
    main()