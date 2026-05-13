#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 medical.json 中的数据分布
"""

import json
from collections import Counter, defaultdict
import os

def analyze_medical_data():
    json_path = "/workspace/data/medical.json"
    
    print("=" * 70)
    print("医疗知识图谱数据分析报告")
    print("=" * 70)
    
    # 1. 读取数据
    print("\n[1] 正在读取数据...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line.strip()) for line in f if line.strip()]
    
    print(f"    成功加载 {len(data)} 条疾病数据")
    
    # 2. 基础统计
    print("\n[2] 基础统计")
    print("-" * 70)
    print(f"    疾病总数: {len(data)}")
    
    # 3. 统计每个字段的存在情况
    print("\n[3] 字段完整性统计")
    print("-" * 70)
    field_counter = Counter()
    field_examples = {}
    
    for item in data:
        for key in item:
            field_counter[key] += 1
            if key not in field_examples:
                field_examples[key] = item[key]
    
    sorted_fields = sorted(field_counter.items(), key=lambda x: x[1], reverse=True)
    
    for field, count in sorted_fields:
        percentage = (count / len(data)) * 100
        print(f"    {field:<20} 出现次数: {count:<8} 覆盖率: {percentage:.1f}%")
    
    # 4. 统计列表字段的元素数量分布
    print("\n[4] 列表字段元素数量分布")
    print("-" * 70)
    list_fields = ['symptom', 'acompany', 'drug', 'common_drug', 
                   'recommand_drug', 'do_eat', 'not_eat', 
                   'recommand_eat', 'check', 'cure_department']
    
    for field in list_fields:
        if field in field_counter:
            counts = []
            for item in data:
                val = item.get(field, [])
                if isinstance(val, list):
                    counts.append(len(val))
            
            if counts:
                avg = sum(counts) / len(counts)
                max_cnt = max(counts)
                min_cnt = min(counts)
                print(f"\n    [{field}]")
                print(f"      平均元素数: {avg:.1f}")
                print(f"      最多: {max_cnt} | 最少: {min_cnt}")
                print(f"      范围分布:")
                
                cnt_counter = Counter(counts)
                for k in sorted(cnt_counter.keys())[:10]:
                    print(f"        {k}: {cnt_counter[k]}次")
                if len(cnt_counter) > 10:
                    print(f"        ... 更多")
    
    # 5. 统计分类字段的值分布
    print("\n[5] 分类字段值分布")
    print("-" * 70)
    
    # 医保状态
    yibao_status_values = []
    for item in data:
        if 'yibao_status' in item:
            yibao_status_values.append(item['yibao_status'])
    
    if yibao_status_values:
        print("\n    [医保状态(yibao_status)]")
        for val, cnt in Counter(yibao_status_values).most_common():
            print(f"      {val}: {cnt}")
    
    # 易感人群
    easy_get_values = []
    for item in data:
        if 'easy_get' in item:
            easy_get_values.append(item['easy_get'])
    
    if easy_get_values:
        print("\n    [易感人群(easy_get) - 示例]")
        for val, cnt in Counter(easy_get_values).most_common(10):
            print(f"      {val}: {cnt}")
    
    # 治疗周期
    cure_lasttime_values = []
    for item in data:
        if 'cure_lasttime' in item:
            cure_lasttime_values.append(item['cure_lasttime'])
    
    if cure_lasttime_values:
        print("\n    [治疗周期(cure_lasttime) - 示例]")
        for val, cnt in Counter(cure_lasttime_values).most_common(10):
            print(f"      {val}: {cnt}")
    
    # 治愈率
    cured_prob_values = []
    for item in data:
        if 'cured_prob' in item:
            cured_prob_values.append(item['cured_prob'])
    
    if cured_prob_values:
        print("\n    [治愈率(cured_prob) - 示例]")
        for val, cnt in Counter(cured_prob_values).most_common(10):
            print(f"      {val}: {cnt}")
    
    # 6. 统计实体数量（从列表中提取）
    print("\n[6] 提取到的实体总数")
    print("-" * 70)
    
    all_symptoms = set()
    all_drugs = set()
    all_foods_do = set()
    all_foods_not = set()
    all_departments = set()
    all_checks = set()
    all_acompany_diseases = set()
    
    for item in data:
        # 症状
        if 'symptom' in item and isinstance(item['symptom'], list):
            all_symptoms.update(item['symptom'])
        
        # 药物
        if 'drug' in item and isinstance(item['drug'], list):
            all_drugs.update(item['drug'])
        if 'common_drug' in item and isinstance(item['common_drug'], list):
            all_drugs.update(item['common_drug'])
        if 'recommand_drug' in item and isinstance(item['recommand_drug'], list):
            all_drugs.update(item['recommand_drug'])
        
        # 食物
        if 'do_eat' in item and isinstance(item['do_eat'], list):
            all_foods_do.update(item['do_eat'])
        if 'not_eat' in item and isinstance(item['not_eat'], list):
            all_foods_not.update(item['not_eat'])
        
        # 科室
        if 'cure_department' in item and isinstance(item['cure_department'], list):
            all_departments.update(item['cure_department'])
        
        # 检查
        if 'check' in item and isinstance(item['check'], list):
            all_checks.update(item['check'])
        
        # 并发症
        if 'acompany' in item and isinstance(item['acompany'], list):
            all_acompany_diseases.update(item['acompany'])
    
    print(f"    症状数量: {len(all_symptoms)}")
    print(f"    药物数量: {len(all_drugs)}")
    print(f"    宜吃食物: {len(all_foods_do)}")
    print(f"    忌食食物: {len(all_foods_not)}")
    print(f"    科室数量: {len(all_departments)}")
    print(f"    检查项目: {len(all_checks)}")
    print(f"    并发症数: {len(all_acompany_diseases)}")
    
    # 7. 展示一些样本数据
    print("\n[7] 示例数据")
    print("-" * 70)
    print(f"\n    第1条数据示例 ({data[0].get('name', 'N/A')}):")
    for k, v in sorted(data[0].items()):
        if isinstance(v, list):
            print(f"      {k}: {len(v)}个 {v[:5]}{'...' if len(v)>5 else ''}")
        elif isinstance(v, str) and len(v) > 50:
            print(f"      {k}: {v[:50]}...")
        else:
            print(f"      {k}: {v}")
    
    print("\n" + "=" * 70)
    print("分析完成！")
    print("=" * 70)
    
    # 8. 生成 JSON 格式的统计结果供进一步分析
    summary = {
        "total_diseases": len(data),
        "field_stats": dict(field_counter),
        "entity_counts": {
            "symptoms": len(all_symptoms),
            "drugs": len(all_drugs),
            "foods_do": len(all_foods_do),
            "foods_not": len(all_foods_not),
            "departments": len(all_departments),
            "checks": len(all_checks),
            "acompany_diseases": len(all_acompany_diseases)
        },
        "examples": {
            "first_disease": data[0]
        }
    }
    
    summary_path = "/workspace/medical_data_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细统计结果已保存至: {summary_path}")

if __name__ == "__main__":
    analyze_medical_data()
