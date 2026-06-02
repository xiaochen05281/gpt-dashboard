#!/usr/bin/env python3
"""
Excel to JSON 转换脚本 v3
正确处理多岗位合并、多Sheet、跳过模板文件
"""

import os
import json
import pandas as pd
import time

DATA_DIR = 'source'
OUTPUT_DIR = 'data/json'

MONTH_MAP = {
    '1月': '2026-01', '2月': '2026-02', '3月': '2026-03',
    '4月': '2026-04', '5月': '2026-05', '6月': '2026-06',
    '7月': '2026-07', '8月': '2026-08', '9月': '2026-09',
    '10月': '2026-10', '11月': '2026-11', '12月': '2026-12',
}

def find_month_from_filename(filename):
    for key, val in MONTH_MAP.items():
        if key in filename:
            return val
    return None

def detect_data_type(filepath):
    p = filepath.replace('\\', '/')
    if ('绩效异常' in p or '装车岗' in p or '卸车岗' in p
            or '倒包岗' in p or '供件岗' in p or '封包岗' in p
            or '分拣岗' in p or '扫描岗' in p):
        return 'performance'
    if '工资偏高' in p:
        return 'salary'
    if '连续出勤' in p and '未出勤' not in p:
        return 'attendance'
    if '未出勤' in p or '连续未出勤' in p:
        return 'absence'
    if '工时过高' in p:
        return 'overtime'
    if '工时偏低' in p:
        return 'undertime'
    if '人数' in p or '基数' in p:
        return 'headcount'
    if '请假' in p:
        return 'leaveRecord'
    if '主管组长' in p or '管幅' in p:
        return 'managerSpan'
    if '后勤' in p or '职能' in p:
        return 'logisticsRatio'
    return 'unknown'

def main():
    if not os.path.exists(DATA_DIR):
        print('[WARN] 数据目录 ' + DATA_DIR + ' 不存在')
        return

    # 按 (month, data_type) 分组
    groups = {}
    for root, dirs, files in os.walk(DATA_DIR):
        if root.startswith(OUTPUT_DIR):
            continue
        for f in files:
            if not f.endswith(('.xlsx', '.xls')) or f.startswith('~') or '模板' in f:
                continue
            fp = os.path.join(root, f)
            month = find_month_from_filename(f)
            if not month:
                try:
                    mtime = os.path.getmtime(fp)
                    month = time.strftime('%Y-%m', time.localtime(mtime))
                except Exception:
                    month = '2026-05'
            dtype = detect_data_type(fp)
            if dtype == 'unknown':
                print('[WARN] 未知类型: ' + f)
                continue
            key = (month, dtype)
            if key not in groups:
                groups[key] = []
            groups[key].append(fp)

    if not groups:
        print('[WARN] 未找到有效的Excel文件')
        return

    print('找到 ' + str(len(groups)) + ' 组数据')
    success = 0

    for (month, dtype), file_list in groups.items():
        all_records = []   # 单Sheet文件的记录
        all_sheets = {}  # 多Sheet文件的记录
        has_multi = False
        job_name = None

        for fp in file_list:
            try:
                xl = pd.ExcelFile(fp)
                base = os.path.splitext(os.path.basename(fp))[0]
                job_name = base.replace('-5月', '')

                for sheet_name in xl.sheet_names:
                    df = pd.read_excel(fp, sheet_name=sheet_name)
                    if df.empty:
                        continue
                    df = df.where(pd.notnull(df), None)
                    records = df.to_dict(orient='records')
                    # 绩效类型：添加 job 字段
                    if dtype == 'performance':
                        for r in records:
                            r['job'] = job_name
                    # 多Sheet
                    if len(xl.sheet_names) > 1:
                        if sheet_name not in all_sheets:
                            all_sheets[sheet_name] = []
                        all_sheets[sheet_name].extend(records)
                        has_multi = True
                    else:
                        all_records.extend(records)

                print('  [OK] ' + os.path.basename(fp) + ' (' + str(len(records) if 'records' in dir() else 0) + ' rows)')
            except Exception as e:
                print('  [FAIL] ' + fp + ': ' + str(e))

        # 构建输出
        output = {
            'month': month,
            'type': dtype,
            'generatedAt': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        if has_multi:
            output['sheets'] = all_sheets
            total = sum(len(v) for v in all_sheets.values())
        else:
            output['data'] = all_records
            total = len(all_records)

        out_path = os.path.join(OUTPUT_DIR, month, dtype + '.json')
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print('  -> ' + out_path + ' (' + str(total) + ' rows total)')
        success += 1

    print('[OK] 完成: ' + str(success) + '/' + str(len(groups)) + ' 组')

if __name__ == '__main__':
    main()
