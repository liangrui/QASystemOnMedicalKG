# question_parser.py 详细代码解析

## 文件信息
- **文件名**: question_parser.py
- **功能**: 问句解析，Cypher查询生成
- **行数**: 183行
- **核心类**: QuestionPaser

---

## 代码结构

```python
class QuestionPaser:
    def build_entitydict(self, args)          # 实体字典转换
    def parser_main(self, res_classify)       # 主解析流程
    def sql_transfer(self, question_type, entities) # SQL生成
```

---

## 核心方法详解

### 1. build_entitydict - 实体字典转换

```python
def build_entitydict(self, args):
    entity_dict = {}
    for arg, types in args.items():
        for type in types:
            if type not in entity_dict:
                entity_dict[type] = [arg]
            else:
                entity_dict[type].append(arg)
    return entity_dict
```

**功能**:
- 输入: `{'感冒': ['disease'], '咳嗽': ['symptom']}`
- 输出: `{'disease': ['感冒'], 'symptom': ['咳嗽']}`

**用途**: 方便后续按类型取实体

---

### 2. parser_main - 主解析流程

```python
def parser_main(self, res_classify):
    args = res_classify['args']
    entity_dict = self.build_entitydict(args)
    question_types = res_classify['question_types']
    
    sqls = []
    for question_type in question_types:
        sql_ = {'question_type': question_type}
        sql = self.sql_transfer(question_type, entity_dict.get(entity_type))
        if sql:
            sql_['sql'] = sql
            sqls.append(sql_)
    return sqls
```

**流程**:
1. 获取分类结果
2. 转换实体字典格式
3. 对每个问题类型生成对应的Cypher
4. 返回查询列表

---

### 3. sql_transfer - 核心SQL生成

**这是最复杂的方法，约100行**

#### 类型A: 查询疾病属性（8种）

```python
if question_type == 'disease_cause':
    sql = ["MATCH (m:Disease) where m.name = '{0}' return m.name, m.cause".format(i) for i in entities]

elif question_type == 'disease_prevent':
    sql = ["MATCH (m:Disease) where m.name = '{0}' return m.name, m.prevent".format(i) for i in entities]
# ... prevent, lasttime, cureway, cureprob, easyget, desc
```

#### 类型B: 查询关系（7种）

```python
# 查询症状
elif question_type == 'disease_symptom':
    sql = ["MATCH (m:Disease)-[r:has_symptom]->(n:Symptom) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

# 查询并发症（双向）
elif question_type == 'disease_acompany':
    sql1 = ["MATCH (m:Disease)-[r:acompany_with]->(n:Disease) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
    sql2 = ["MATCH (m:Disease)-[r:acompany_with]->(n:Disease) where n.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
    sql = sql1 + sql2

# 查询药物（常用药 + 推荐药）
elif question_type == 'disease_drug':
    sql1 = ["MATCH (m:Disease)-[r:common_drug]->(n:Drug) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
    sql2 = ["MATCH (m:Disease)-[r:recommand_drug]->(n:Drug) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]
    sql = sql1 + sql2
```

#### 类型C: 反向查询（3种）

```python
# 症状到疾病
elif question_type == 'symptom_disease':
    sql = ["MATCH (m:Disease)-[r:has_symptom]->(n:Symptom) where n.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

# 药物到疾病
elif question_type == 'drug_disease':
    sql1 = [...]  # common_drug 反向
    sql2 = [...]  # recommand_drug 反向
    sql = sql1 + sql2
```

---

## Cypher查询模式

### 模式1: 查询节点属性
```cypher
MATCH (m:Disease) 
WHERE m.name = '感冒' 
RETURN m.name, m.cause
```

### 模式2: 查询关系
```cypher
MATCH (m:Disease)-[r:has_symptom]->(n:Symptom) 
WHERE m.name = '感冒' 
RETURN m.name, r.name, n.name
```

### 模式3: 双向关系查询
```cypher
// 正向
MATCH (m:Disease)-[r:acompany_with]->(n:Disease) WHERE m.name = '感冒'
// 反向  
MATCH (m:Disease)-[r:acompany_with]->(n:Disease) WHERE n.name = '感冒'
```

---

## 问题类型对应关系

| 问题类型 | 查询内容 | 返回字段 |
|---------|---------|---------|
| disease_symptom | 疾病症状 | m.name, r.name, n.name |
| symptom_disease | 症状→疾病 | m.name, r.name, n.name |
| disease_cause | 病因 | m.name, m.cause |
| disease_acompany | 并发症 | m.name, r.name, n.name (双向) |
| disease_not_food | 忌吃 | m.name, r.name, n.name |
| disease_do_food | 宜吃+推荐食谱 | m.name, r.name, n.name |
| food_not_disease | 食物忌用疾病 | m.name, r.name, n.name |
| food_do_disease | 食物宜用疾病 | m.name, r.name, n.name |
| disease_drug | 常用药+推荐药 | m.name, r.name, n.name |
| drug_disease | 药物治什么病 | m.name, r.name, n.name |
| disease_check | 检查项目 | m.name, r.name, n.name |
| check_disease | 检查对应疾病 | m.name, r.name, n.name |
| disease_prevent | 预防措施 | m.name, m.prevent |
| disease_lasttime | 治疗周期 | m.name, m.cure_lasttime |
| disease_cureway | 治疗方式 | m.name, m.cure_way |
| disease_cureprob | 治愈概率 | m.name, m.cured_prob |
| disease_easyget | 易感人群 | m.name, m.easy_get |
| disease_desc | 疾病描述 | m.name, m.desc |

---

## 输出数据结构

```python
[
    {
        'question_type': 'disease_symptom',
        'sql': [
            "MATCH (m:Disease)-[r:has_symptom]->(n:Symptom) WHERE m.name = '感冒' return m.name, r.name, n.name"
        ]
    },
    {
        'question_type': 'disease_cause',
        'sql': [
            "MATCH (m:Disease) WHERE m.name = '感冒' return m.name, m.cause"
        ]
    }
]
```

---

## 设计亮点

1. **清晰的分类处理**: 18类问题，每类对应一个elif分支
2. **统一的返回格式**: 每个分支返回同样结构的数据
3. **灵活的多实体处理**: 使用列表推导，支持多个实体
4. **双向关系处理**: 对并发症等关系，双向查询保证完整
5. **多关系合并**: 疾病药物=常用药+推荐药

---

## 代码优化建议

1. **使用模板引擎**
```python
TEMPLATES = {
    'disease_cause': "MATCH (m:Disease) WHERE m.name = '{0}' RETURN m.name, m.cause"
}
sql = [TEMPLATES[question_type].format(i) for i in entities]
```

2. **参数化查询**（防止注入）
```python
query, params = prepare_query(question_type, entities)
```

3. **错误处理**
```python
try:
    sql = [...]
except Exception as e:
    logger.error(e)
    sql = []
```

---

## 总结

这个文件虽然长，但结构清晰：
- ✅ 每种问题类型对应一个分支
- ✅ Cypher构造直观
- ✅ 支持多实体、多关系
- ⚠️ 代码有重复（可以用模板优化）

很好的展示了如何用规则生成SQL（Cypher）！
