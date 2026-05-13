# question_classifier.py 详细代码解析

## 文件信息
- **文件名**: question_classifier.py
- **功能**: 问句分类和实体识别
- **行数**: 224行
- **核心类**: QuestionClassifier
- **核心算法**: Aho-Corasick

---

## 核心功能

1. 加载7类实体词和否定词
2. 构建AC自动机进行快速实体匹配
3. 匹配特征词进行问题分类
4. 输出实体和问题类型

---

## 代码结构概览

```python
class QuestionClassifier:
    def __init__(self)              # 初始化
    def classify(self, question)     # 分类主方法
    def build_wdtype_dict(self)      # 构建词-类型字典
    def build_actree(self, wordlist) # 构建AC自动机
    def check_medical(self, question) # 医疗实体匹配
    def check_words(self, wds, sent) # 特征词检测
```

---

## 逐方法详解

### 1. __init__ 初始化方法

**功能**: 加载词典、构建AC自动机、初始化特征词

**关键代码**:
```python
self.disease_wds = [i.strip() for i in open(self.disease_path) if i.strip()]
self.department_wds = [...]
# ... 加载其他6类实体

self.region_words = set(self.department_wds + ...)  # 合并所有实体词

self.region_tree = self.build_actree(list(self.region_words))  # 构建AC自动机

self.wdtype_dict = self.build_wdtype_dict()  # 词-类型映射

# 定义18类问题的特征词
self.symptom_qwds = ['症状', '表征', ...]
self.cause_qwds = ['原因', '成因', ...]
# ... 其他特征词
```

**设计亮点**:
- 使用`set`去重
- 预计算各种数据结构，避免运行时计算
- 特征词列表设计得很全

---

### 2. classify 分类主方法

**这是核心方法，约100行**

**流程**:
```python
def classify(self, question):
    # Step 1: 匹配实体
    medical_dict = self.check_medical(question)
    if not medical_dict:
        return {}
    
    # Step 2: 收集实体类型
    types = []
    for type_ in medical_dict.values():
        types += type_
    
    # Step 3: 匹配问题特征词，确定问题类型
    question_types = []
    if self.check_words(self.symptom_qwds, question) and ('disease' in types):
        question_type = 'disease_symptom'
        question_types.append(question_type)
    
    if self.check_words(self.symptom_qwds, question) and ('symptom' in types):
        question_type = 'symptom_disease'
        question_types.append(question_type)
    
    # ... 其他16类问题判断
    
    # Step 4: 回退机制
    if question_types == [] and 'disease' in types:
        question_types = ['disease_desc']
    
    if question_types == [] and 'symptom' in types:
        question_types = ['symptom_disease']
    
    return {
        'args': medical_dict,
        'question_types': question_types
    }
```

**关键处理逻辑**:

| 处理 | 说明 |
|-----|------|
| 实体匹配 | AC自动机 + 最长匹配 |
| 类型判断 | 特征词匹配 + 实体类型 |
| 否定词 | 通过deny_words区分肯定/否定 |
| 回退 | 无类型时默认返回disease_desc或symptom_disease |

---

### 3. build_actree 构建AC自动机

```python
def build_actree(self, wordlist):
    actree = ahocorasick.Automaton()
    for index, word in enumerate(wordlist):
        actree.add_word(word, (index, word))
    actree.make_automaton()
    return actree
```

**解析**:
- 使用`ahocorasick`库（需pip安装）
- `add_word`: 添加模式串
- `make_automaton`: 构建自动机，构建失败指针等
- 返回构建好的自动机对象

---

### 4. check_medical 医疗实体匹配

```python
def check_medical(self, question):
    # Step 1: 用AC自动机匹配所有实体
    region_wds = []
    for i in self.region_tree.iter(question):
        wd = i[1][1]
        region_wds.append(wd)
    
    # Step 2: 最长匹配去重
    stop_wds = []
    for wd1 in region_wds:
        for wd2 in region_wds:
            if wd1 in wd2 and wd1 != wd2:
                stop_wds.append(wd1)
    final_wds = [i for i in region_wds if i not in stop_wds]
    
    # Step 3: 映射到类型
    final_dict = {i: self.wdtype_dict.get(i) for i in final_wds}
    
    return final_dict
```

**最长匹配算法解析**:
```
假设匹配结果: ['急性', '急性支气管炎']
检查: '急性' 在 '急性支气管炎' 中 → 去掉'急性'
最终结果: ['急性支气管炎']
```

**时间复杂度**: O(n²)，n是匹配结果数，实际中n很小所以没问题

---

### 5. build_wdtype_dict 构建词-类型字典

```python
def build_wdtype_dict(self):
    wd_dict = dict()
    for wd in self.region_words:
        wd_dict[wd] = []
        if wd in self.disease_wds:
            wd_dict[wd].append('disease')
        if wd in self.department_wds:
            wd_dict[wd].append('department')
        # ... 其他类型
    return wd_dict
```

**设计**:
- 一个词可能属于多个类型，所以value是list
- 比如一个词可能既是疾病又是症状

---

### 6. check_words 特征词检测

```python
def check_words(self, wds, sent):
    for wd in wds:
        if wd in sent:
            return True
    return False
```

**简单但实用**:
- 只要特征词列表中有一个在句子中就返回True
- 相当于OR逻辑

---

## 18类问题类型详解

| 类型 | 触发条件 | 查询内容 |
|-----|---------|---------|
| disease_symptom | disease + 症状类词 | 疾病的症状 |
| symptom_disease | symptom + 症状类词 | 症状对应疾病 |
| disease_cause | disease + 原因类词 | 疾病病因 |
| disease_acompany | disease + 并发症词 | 疾病并发症 |
| disease_not_food | disease + 食物词 + 否定词 | 疾病忌吃 |
| disease_do_food | disease + 食物词 - 否定词 | 疾病宜吃 |
| food_not_disease | food + 食物/治疗词 + 否定词 | 食物忌用疾病 |
| food_do_disease | food + 食物/治疗词 - 否定词 | 食物宜用疾病 |
| disease_drug | disease + 药物词 | 疾病用什么药 |
| drug_disease | drug + 治疗词 | 药物治什么病 |
| disease_check | disease + 检查词 | 疾病查什么 |
| check_disease | check + 检查/治疗词 | 检查对应疾病 |
| disease_prevent | disease + 预防词 | 疾病预防 |
| disease_lasttime | disease + 周期词 | 治疗周期 |
| disease_cureway | disease + 治疗词 | 治疗方式 |
| disease_cureprob | disease + 概率词 | 治愈概率 |
| disease_easyget | disease + 易感词 | 易感人群 |
| disease_desc | 只有disease | 疾病描述 |

---

## 数据结构

### 输出格式
```python
{
    'args': {
        '感冒': ['disease'],
        '咳嗽': ['symptom']
    },
    'question_types': ['disease_symptom', 'symptom_disease']
}
```

### wdtype_dict格式
```python
{
    '感冒': ['disease'],
    '咳嗽': ['symptom'],
    '内科': ['department'],
    ...
}
```

---

## 代码优化建议

### 1. 优化最长匹配

**当前**: O(n²)

**建议**: 按长度排序，长词优先
```python
region_wds.sort(key=len, reverse=True)
selected = []
for wd in region_wds:
    if not any(wd in s for s in selected):
        selected.append(wd)
```

### 2. 特征词匹配优化

**当前**: 逐个check

**建议**: 构建trie或AC自动机加速

### 3. 增加置信度

**建议**:
```python
{
    'args': {...},
    'question_types': [...],
    'confidence': 0.95
}
```

### 4. 文件加载优化

**建议**: 捕获异常
```python
try:
    self.disease_wds = [...]
except FileNotFoundError:
    logger.error("File not found!")
    raise
```

---

## 总结

这个文件是系统的关键组件：
- ✅ 高效的AC算法
- ✅ 完整的特征词定义
- ✅ 实用的最长匹配
- ⚠️ 可以优化性能
- ⚠️ 缺少错误处理

它展示了如何用规则方法做NLU，学习价值很高！
