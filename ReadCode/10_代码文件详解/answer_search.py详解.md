# answer_search.py 详细代码解析

## 文件信息
- **文件名**: answer_search.py
- **功能**: 查询执行和答案格式化
- **行数**: 136行
- **核心类**: AnswerSearcher

---

## 代码结构

```python
class AnswerSearcher:
    def __init__(self)                    # 初始化Neo4j连接
    def search_main(self, sqls)           # 执行查询主流程
    def answer_prettify(self, question_type, answers) # 答案格式化
```

---

## 核心方法详解

### 1. __init__ - 初始化连接

```python
def __init__(self):
    self.g = Graph(
        host="127.0.0.1",
        http_port=7474,
        user="lhy",
        password="lhy123")
    self.num_limit = 20
```

**说明**:
- 连接本地Neo4j数据库
- 用户名密码硬编码（生产环境应该用配置）
- `num_limit`: 最多返回20个结果

---

### 2. search_main - 执行查询主流程

```python
def search_main(self, sqls):
    final_answers = []
    for sql_ in sqls:
        question_type = sql_['question_type']
        queries = sql_['sql']
        answers = []
        for query in queries:
            ress = self.g.run(query).data()
            answers += ress
        final_answer = self.answer_prettify(question_type, answers)
        if final_answer:
            final_answers.append(final_answer)
    return final_answers
```

**流程**:
1. 遍历每个查询结构
2. 对每个Cypher执行查询
3. 收集所有结果
4. 调用格式化
5. 返回答案列表

---

### 3. answer_prettify - 答案格式化（核心方法）

#### 模式A: 关系查询结果格式化

```python
if question_type == 'disease_symptom':
    desc = [i['n.name'] for i in answers]
    subject = answers[0]['m.name']
    final_answer = '{0}的症状包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

elif question_type == 'symptom_disease':
    desc = [i['m.name'] for i in answers]
    subject = answers[0]['n.name']
    final_answer = '症状{0}可能染上的疾病有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
```

#### 模式B: 属性查询结果格式化

```python
elif question_type == 'disease_cause':
    desc = [i['m.cause'] for i in answers]
    subject = answers[0]['m.name']
    final_answer = '{0}可能的成因有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))

elif question_type == 'disease_prevent':
    desc = [i['m.prevent'] for i in answers]
    subject = answers[0]['m.name']
    final_answer = '{0}的预防措施包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
```

#### 模式C: 特殊处理 - 并发症

```python
elif question_type == 'disease_acompany':
    desc1 = [i['n.name'] for i in answers]
    desc2 = [i['m.name'] for i in answers]
    subject = answers[0]['m.name']
    desc = [i for i in desc1 + desc2 if i != subject]  # 排除疾病自己
    final_answer = '{0}的症状包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
```

#### 模式D: 特殊处理 - 宜吃食物（区分关系类型）

```python
elif question_type == 'disease_do_food':
    do_desc = [i['n.name'] for i in answers if i['r.name'] == '宜吃']
    recommand_desc = [i['n.name'] for i in answers if i['r.name'] == '推荐食谱']
    subject = answers[0]['m.name']
    final_answer = '{0}宜食的食物包括有：{1}\n推荐食谱包括有：{2}'.format(
        subject, 
        ';'.join(list(set(do_desc))[:self.num_limit]), 
        ';'.join(list(set(recommand_desc))[:self.num_limit]))
```

---

## 返回结果示例

### Neo4j原始返回
```python
[
    {'m.name': '感冒', 'r.name': 'has_symptom', 'n.name': '咳嗽'},
    {'m.name': '感冒', 'r.name': 'has_symptom', 'n.name': '流鼻涕'},
    {'m.name': '感冒', 'r.name': 'has_symptom', 'n.name': '发热'}
]
```

### 格式化后的回答
```
感冒的症状包括：咳嗽；流鼻涕；发热
```

---

## 18类问题回答模板

| 问题类型 | 模板示例 |
|---------|---------|
| disease_symptom | {disease}的症状包括：{symptoms} |
| symptom_disease | 症状{symptom}可能染上的疾病有：{diseases} |
| disease_cause | {disease}可能的成因有：{causes} |
| disease_acompany | {disease}的症状包括：{diseases} |
| disease_not_food | {disease}忌食的食物包括有：{foods} |
| disease_do_food | {disease}宜食的食物包括有：{foods}\n推荐食谱包括有：{recipes} |
| food_not_disease | 患有{diseases}的人最好不要吃{food} |
| food_do_disease | 患有{diseases}的人建议多试试{food} |
| disease_drug | {disease}通常的使用的药品包括：{drugs} |
| drug_disease | {drug}主治的疾病有{diseases},可以试试 |
| disease_check | {disease}通常可以通过以下方式检查出来：{checks} |
| check_disease | 通常可以通过{check}检查出来的疾病有{diseases} |
| disease_prevent | {disease}的预防措施包括：{preventions} |
| disease_lasttime | {disease}治疗可能持续的周期为：{time} |
| disease_cureway | {disease}可以尝试如下治疗：{ways} |
| disease_cureprob | {disease}治愈的概率为（仅供参考）：{prob} |
| disease_easyget | {disease}的易感人群包括：{people} |
| disease_desc | {disease},熟悉一下：{desc} |

---

## 关键处理技术

### 1. 去重处理
```python
list(set(desc))[:self.num_limit]
```
- `set`: 去重
- `[:20]`: 限制数量

### 2. 空结果处理
```python
if not answers:
    return ''
```

### 3. 关系类型区分
```python
if i['r.name'] == '宜吃'
elif i['r.name'] == '推荐食谱'
```

### 4. 双向结果合并（并发症）
```python
desc = [i for i in desc1 + desc2 if i != subject]
```

---

## 代码优化建议

### 1. 配置管理
```python
# config.py
NEO4J_CONFIG = {
    'host': os.getenv('NEO4J_HOST', '127.0.0.1'),
    'port': 7474,
    'user': os.getenv('NEO4J_USER', 'neo4j'),
    'password': os.getenv('NEO4J_PASSWORD', 'password')
}
```

### 2. 增加超时和重试
```python
try:
    ress = self.g.run(query).data()
except Exception as e:
    logger.error(f"Query failed: {e}")
    return []
```

### 3. 模板配置化
```python
ANSWER_TEMPLATES = {
    'disease_symptom': "{0}的症状包括：{1}"
}
```

### 4. 连接池
```python
# 使用连接池而不是每次新建连接
```

---

## 总结

这个文件职责单一清晰：
- ✅ 执行Cypher查询
- ✅ 格式化自然语言回答
- ✅ 处理特殊情况
- ⚠️ 配置硬编码
- ⚠️ 缺少错误处理

非常好的展示了如何将结构化数据转为自然语言！
