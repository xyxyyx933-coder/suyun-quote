# -*- coding: utf-8 -*-
"""
苏运算 · 桌面软件宿主（pywebview + WebView2）

前端：苏运算.html（单文件应用，内嵌运费算法 / 报价 / 汇总 / 货代实单学习）
本模块只做三件事：
  1) 起窗口、加载 html
  2) 提供运费记录 / 汇总报价记录的读写（落盘到 exe 同目录 json）
  3) 代理实时汇率请求（避开浏览器 CORS）
"""
import os
import sys
import csv
import json
from datetime import datetime
from urllib.request import Request, urlopen

import webview

APP_NAME = '苏运算'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'


def resource_path(rel):
    """打包后取临时解包目录，开发时取脚本目录"""
    if getattr(sys, 'frozen', False):
        base = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, rel)


def data_dir():
    """数据目录：打包后 = exe 所在目录；开发时 = 脚本目录"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


RECORD_FILE = os.path.join(data_dir(), '运费记录.json')
CSV_FILE = os.path.join(data_dir(), '运费记录.csv')
QUOTE_STATE_FILE = '苏银报价状态.json'   # 内嵌报价页（苏银报价计算器 v1.22+）的完整状态

# 允许前端落盘的文件（防止任意路径写文件）
ALLOWED_STORE = {
    '货代实单.json',
    '运费记录.json',
    '报价记录.json',
    QUOTE_STATE_FILE,
}


class RecordApi:
    """暴露给前端 window.pywebview.api 的接口。"""

    # ---------- 基础 ----------
    def ping(self):
        return {'ok': True, 'app': APP_NAME, 'dir': data_dir()}

    def _read_all(self):
        try:
            with open(RECORD_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception:
            pass
        return []

    def _write_all(self, rows):
        try:
            with open(RECORD_FILE, 'w', encoding='utf-8') as f:
                json.dump(rows, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ---------- 运费记录 ----------
    def save_record(self, rec):
        if not isinstance(rec, dict):
            return {'ok': False, 'msg': '记录格式不正确'}
        rows = self._read_all()
        new_id = 1
        for r in rows:
            try:
                new_id = max(new_id, int(r.get('id', 0)) + 1)
            except Exception:
                pass
        rec = dict(rec)
        rec['id'] = new_id
        rec['saved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rows.insert(0, rec)
        self._write_all(rows)
        return {'ok': True, 'count': len(rows), 'id': new_id}

    def list_records(self):
        return self._read_all()

    def delete_record(self, rid):
        rows = self._read_all()
        out = []
        for r in rows:
            try:
                same = str(r.get('id')) == str(rid)
            except Exception:
                same = False
            if not same:
                out.append(r)
        self._write_all(out)
        return {'ok': True, 'count': len(out)}

    def clear_records(self):
        self._write_all([])
        return {'ok': True, 'count': 0}

    def export_csv(self):
        rows = self._read_all()
        path = CSV_FILE
        try:
            with open(path, 'w', encoding='utf-8-sig', newline='') as f:
                w = csv.writer(f)
                w.writerow(['记录时间', '目的国', '邮编', '详细地址', '尺寸(cm)', '实重(kg)',
                            'CBM(方)', '计费重(kg)', '推荐渠道', '最低总价(RMB)', '全部渠道报价', '备注'])
                for r in rows:
                    w.writerow([r.get('saved_at', ''), r.get('destName', ''), r.get('zip', ''),
                                str(r.get('addr', '') or '').replace('\n', ' '),
                                r.get('dim', ''), r.get('gross', ''), r.get('cbm', ''),
                                r.get('chargeW', ''), r.get('bestChannel', ''),
                                r.get('bestTotal', ''), r.get('allChannels', ''), r.get('note', '')])
        except Exception as e:
            return {'ok': False, 'msg': str(e)}
        return {'ok': True, 'path': path, 'count': len(rows)}

    # ---------- 通用 JSON 存档（货代实单 / 汇总报价记录） ----------
    def save_json(self, name, text):
        if name not in ALLOWED_STORE:
            return {'ok': False, 'msg': '不允许的文件名'}
        path = os.path.join(data_dir(), name)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text if isinstance(text, str) else json.dumps(text, ensure_ascii=False))
        except Exception as e:
            return {'ok': False, 'msg': str(e)}
        return {'ok': True, 'path': path}

    def load_json(self, name):
        if name not in ALLOWED_STORE:
            return {'ok': False, 'text': ''}
        path = os.path.join(data_dir(), name)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return {'ok': True, 'text': f.read()}
        except Exception:
            return {'ok': False, 'text': ''}

    # ---------- 报价页状态桥（苏银报价计算器 v1.22+ 调用） ----------
    def save_data(self, txt):
        """整包保存报价页状态（与 localStorage 双写互为备份）"""
        try:
            path = os.path.join(data_dir(), QUOTE_STATE_FILE)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(txt if isinstance(txt, str) else json.dumps(txt, ensure_ascii=False))
            return {'ok': True, 'path': path}
        except Exception as e:
            return {'ok': False, 'msg': str(e)}

    def load_data(self):
        try:
            path = os.path.join(data_dir(), QUOTE_STATE_FILE)
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ''

    def save_text(self, name, txt):
        """报价文本等直接存到桌面"""
        safe = os.path.basename(str(name or 'export.txt'))
        desk = os.path.join(os.path.expanduser('~'), 'Desktop')
        if not os.path.isdir(desk):
            desk = data_dir()
        path = os.path.join(desk, safe)
        try:
            with open(path, 'w', encoding='utf-8-sig') as f:
                f.write(str(txt or ''))
            return path
        except Exception:
            return ''

    # ---------- 全量备份 / 恢复 ----------
    BACKUP_FILES = ['运费记录.json', '报价记录.json', QUOTE_STATE_FILE, '货代实单.json']

    def export_backup(self):
        """把所有业务数据打包成一个 JSON 存到 exe 目录"""
        data = {'_app': '苏运算', '_ver': 1,
                '_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        n = 0
        for name in self.BACKUP_FILES:
            try:
                with open(os.path.join(data_dir(), name), 'r', encoding='utf-8') as f:
                    data[name] = f.read()
                n += 1
            except Exception:
                continue
        path = os.path.join(
            data_dir(),
            '数据备份_' + datetime.now().strftime('%Y%m%d_%H%M') + '.json')
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
        except Exception as e:
            return {'ok': False, 'msg': str(e)}
        return {'ok': True, 'path': path, 'count': n}

    def restore_backup(self, text):
        """从备份 JSON 恢复（只覆盖备份里存在的已知文件）"""
        try:
            data = json.loads(text)
        except Exception as e:
            return {'ok': False, 'msg': '备份文件解析失败：' + str(e)}
        if not isinstance(data, dict) or data.get('_app') != '苏运算':
            return {'ok': False, 'msg': '这不是本程序的备份文件'}
        n = 0
        for name in self.BACKUP_FILES:
            if name not in data:
                continue
            try:
                json.loads(data[name])   # 先校验内容是合法 JSON 再落盘
            except Exception:
                continue
            try:
                with open(os.path.join(data_dir(), name), 'w', encoding='utf-8') as f:
                    f.write(data[name])
                n += 1
            except Exception:
                continue
        return {'ok': True, 'count': n}

    # ---------- 实时汇率 ----------
    def get_rates(self):
        urls = [
            'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/cny.json',
            'https://open.er-api.com/v6/latest/CNY',
        ]
        for u in urls:
            try:
                req = Request(u, headers={'User-Agent': UA})
                with urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                raw = data.get('cny') or data.get('rates')
                if not raw:
                    continue
                rates = {'CNY': 1.0}
                for k, v in raw.items():
                    try:
                        fv = float(v)
                    except Exception:
                        continue
                    if fv > 0:
                        rates[str(k).upper()] = fv
                if rates.get('USD'):
                    date = data.get('date') or data.get('time_last_update_utc') or ''
                    return {
                        'ok': True,
                        'base': 'CNY',
                        'rates': rates,
                        'date': str(date)[:10] if date else '',
                        'source': 'jsdelivr' if 'jsdelivr' in u else 'er-api',
                        'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    }
            except Exception:
                continue
        return {'ok': False, 'msg': '网络暂不可用'}


html_path = resource_path('苏运算.html')
icon_path = resource_path('app.ico')
api = RecordApi()

if __name__ == '__main__':
    webview.create_window(
        title=APP_NAME,
        url=html_path,
        width=1280,
        height=860,
        min_size=(960, 640),
        js_api=api,
    )
    webview.start(gui='edgechromium', icon=icon_path)
