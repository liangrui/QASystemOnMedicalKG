# build_medicalgraph.py 详细代码解析

## 文件信息
- **文件名**: build_medicalgraph.py
- **功能**: 知识图谱构建（节点+关系）
- **行数**: 274行
- **核心类**: MedicalGraph

---

## 代码结构

```python
class MedicalGraph:
    def __init__(self)                # 初始化
    def read_nodes(self)              # 读取JSON数据，提取节点和关系
    def create_node(self, label, nodes) # 创建节点
    def create_diseases_nodes(self, disease_infos) # 带属性的疾病节点
    def create_graphnodes(self)       # 创建所有节点入口
    def create_relationship(self, ...) # 创建关系
    def create_graphrels(self)        # 创建所有关系入口
    def export_data(self)             # 导出数据
```

---

## 核心方法详解

### 1. __init__ - 初始化

```python
def __init__(self):
    cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
    self.data_path = os.path.join(cur_dir, 'data/medical.json')
    self.g = Graph(
        host="127.0.0.1",
        http_port=7474,
        user="lhy",
        password="lhy123")
```

---

### 2. read_nodes - 数据提取（核心方法，100+行）

#### 提取节点
```python
drugs = []
foods = []
checks = []
departments = []
producers = []
diseases = []
symptoms = []
disease_infos = []  # 疾病详细信息（属性）
```

#### 提取关系
```python
rels_department = []      # 科室从属
rels_noteat = []          # 忌吃
rels_doeat = []           # 宜吃
rels_recommandeat = []    # 推荐食谱
rels_commonddrug = []     # 常用药
rels_recommanddrug = []   # 推荐药
rels_check = []           # 检查
rels_drug_producer = []   # 药品生产
rels_symptom = []         # 症状
rels_acompany = []        # 并发症
rels_category = []        # 疾病科室
```

#### 逐行解析JSON
```python
for data in open(self.data_path):
    data_json = json.loads(data)
    disease = data_json['name']
    diseases.append(disease)
    
    # 疾病属性
    disease_dict['desc'] = data_json.get('desc', '')
    disease_dict['cause'] = data_json.get('cause', '')
    # ... prevent, cure_lasttime, cure_way, cured_prob, easy_get
    
    # 症状
    if 'symptom' in data_json:
        symptoms += data_json['symptom']
        for symptom in data_json['symptom']:
            rels_symptom.append([disease, symptom])
    
    # 并发症
    if 'acompany' in data_json:
        for acompany in data_json['acompany']:
            rels_acompany.append([disease, acompany])
    
    # 药物
    if 'common_drug' in data_json:
        drugs += data_json['common_drug']
        for drug in data_json['common_drug']:
            rels_commonddrug.append([disease, drug])
    
    # 食物
    if 'not_eat' in data_json:
        foods += data_json['not_eat']
        for food in data_json['not_eat']:
            rels_noteat.append([disease, food])
    # ... do_eat, recommand_eat
    
    # 科室
    if 'cure_department' in data_json:
        cure_department = data_json['cure_department']
        if len(cure_department) == 2:
            big = cure_department[0]
            small = cure_department[1]
            rels_department.append([small, big])  # 小科室属于大科室
            rels_category.append([disease, small]) # 疾病属于小科室
        departments += cure_department
    
    # 检查
    if 'check' in data_json:
        checks += data_json['check']
        for check in data_json['check']:
            rels_check.append([disease, check])
    
    # 药品生产厂家
    if 'drug_detail' in data_json:
        drug_detail = data_json['drug_detail']
        producer = [i.split('(')[0] for i in drug_detail]
        rels_drug_producer += [[i.split('(')[0], i.split('(')[-1].replace(')', '')] for i in drug_detail]
        producers += producer
```

---

### 3. create_node - 创建节点

```python
def create_node(self, label, nodes):
    count = 0
    for node_name in nodes:
        node = Node(label, name=node_name)
        self.g.create(node)
        count += 1
        print(count, len(nodes))
```

---

### 4. create_diseases_nodes - 创建疾病节点（带属性）

```python
def create_diseases_nodes(self, disease_infos):
    count = 0
    for disease_dict in disease_infos:
        node = Node("Disease", 
                    name=disease_dict['name'], 
                    desc=disease_dict['desc'],
                    prevent=disease_dict['prevent'], 
                    cause=disease_dict['cause'],
                    easy_get=disease_dict['easy_get'], 
                    cure_lasttime=disease_dict['cure_lasttime'],
                    cure_department=disease_dict['cure_department'],
                    cure_way=disease_dict['cure_way'], 
                    cured_prob=disease_dict['cured_prob'])
        self.g.create(node)
        count += 1
        print(count)
```

---

### 5. create_graphnodes - 创建所有节点

```python
def create_graphnodes(self):
    Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, *rels = self.read_nodes()
    self.create_diseases_nodes(disease_infos)
    self.create_node('Drug', Drugs)
    self.create_node('Food', Foods)
    self.create_node('Check', Checks)
    self.create_node('Department', Departments)
    self.create_node('Producer', Producers)
    self.create_node('Symptom', Symptoms)
```

---

### 6. create_relationship - 创建关系

```python
def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
    count = 0
    # 去重
    set_edges = []
    for edge in edges:
        set_edges.append('###'.join(edge))
    all = len(set(set_edges))
    
    for edge in set(set_edges):
        edge = edge.split('###')
        p = edge[0]
        q = edge[1]
        query = "match(p:%s),(q:%s) where p.name='%s' and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
            start_node, end_node, p, q, rel_type, rel_name)
        try:
            self.g.run(query)
            count += 1
            print(rel_type, count, all)
        except Exception as e:
            print(e)
```

**技巧**:
- 使用`'###'.join(edge)`来去重
- 用match找到节点，然后create关系

---

### 7. create_graphrels - 创建所有关系

```python
def create_graphrels(self):
    Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, \
    rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, \
    rels_commonddrug, rels_drug_producer, rels_recommanddrug, rels_symptom, \
    rels_acompany, rels_category = self.read_nodes()
    
    self.create_relationship('Disease', 'Food', rels_recommandeat, 'recommand_eat', '推荐食谱')
    self.create_relationship('Disease', 'Food', rels_noteat, 'no_eat', '忌吃')
    self.create_relationship('Disease', 'Food', rels_doeat, 'do_eat', '宜吃')
    self.create_relationship('Department', 'Department', rels_department, 'belongs_to', '属于')
    self.create_relationship('Disease', 'Drug', rels_commonddrug, 'common_drug', '常用药品')
    self.create_relationship('Producer', 'Drug', rels_drug_producer, 'drugs_of', '生产药品')
    self.create_relationship('Disease', 'Drug', rels_recommanddrug, 'recommand_drug', '好评药品')
    self.create_relationship('Disease', 'Check', rels_check, 'need_check', '诊断检查')
    self.create_relationship('Disease', 'Symptom', rels_symptom, 'has_symptom', '症状')
    self.create_relationship('Disease', 'Disease', rels_acompany, 'acompany_with', '并发症')
    self.create_relationship('Disease', 'Department', rels_category, 'belongs_to', '所属科室')
```

---

## 知识图谱Schema

### 实体类型（7种）
| 类型 | Label | 数量 |
|-----|-------|-----|
| 疾病 | Disease | 8,807 |
| 药品 | Drug | 3,828 |
| 食物 | Food | 4,870 |
| 症状 | Symptom | 5,998 |
| 检查 | Check | 3,353 |
| 科室 | Department | 54 |
| 生产厂家 | Producer | 17,201 |

### 关系类型（11种）
| 关系类型 | 起始节点 | 结束节点 | 关系名 |
|---------|---------|---------|-------|
| has_symptom | Disease | Symptom | 症状 |
| common_drug | Disease | Drug | 常用药品 |
| recommand_drug | Disease | Drug | 好评药品 |
| do_eat | Disease | Food | 宜吃 |
| no_eat | Disease | Food | 忌吃 |
| recommand_eat | Disease | Food | 推荐食谱 |
| need_check | Disease | Check | 诊断检查 |
| acompany_with | Disease | Disease | 并发症 |
| belongs_to | Disease | Department | 所属科室 |
| belongs_to | Department | Department | 属于 |
| drugs_of | Producer | Drug | 生产药品 |

---

## 使用方法

```python
if __name__ == '__main__':
    handler = MedicalGraph()
    print("step1:导入图谱节点中")
    handler.create_graphnodes()
    print("step2:导入图谱边中")      
    handler.create_graphrels()
```

**注意**: 这步可能需要几个小时，因为有30万+关系要创建！

---

## 代码优化建议

1. **批量导入**
```python
# 而不是逐条create
UNWIND $batch as row
MATCH (p:Disease {name: row.start}), (q:Drug {name: row.end})
CREATE (p)-[r:common_drug {name: '常用药品'}]->(q)
```

2. **索引**
```python
CREATE INDEX ON :Disease(name);
CREATE INDEX ON :Drug(name);
```

3. **进度条**
```python
from tqdm import tqdm
for edge in tqdm(set(set_edges)):
    ...
```

---

## 总结

这个文件是知识图谱构建的核心：
- ✅ 完整的节点创建
- ✅ 完整的关系创建
- ✅ 数据解析清晰
- ⚠️ 单条创建效率低（生产环境建议批量）
- ⚠️ 缺少进度显示和错误恢复

非常好的展示了如何从JSON构建知识图谱！
