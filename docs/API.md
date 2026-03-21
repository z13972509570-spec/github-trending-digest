# API 文档

## TrendingFetcher

Trending 数据抓取器。

### 构造函数

```python
TrendingFetcher(github_token: Optional[str] = None)
```

### 方法

#### `fetch_trending()`

```python
def fetch_trending(
    self,
    language: Optional[str] = None,
    since: str = "daily"
) -> List[Project]
```

#### `fetch_rising_stars()`

```python
def fetch_rising_stars(self, days: int = 1) -> List[Project]
```

## TrendAnalyzer

趋势分析器。

### 方法

#### `analyze()`

```python
def analyze(
    self,
    projects: List[Project],
    report_type: str = "daily"
) -> TrendReport
```

#### `categorize()`

```python
def categorize(self, projects: List[Project]) -> Dict[str, List[Project]]
```

## TrendStorage

数据存储。

### 构造函数

```python
TrendStorage(db_path: str = "./data/trending.db")
```

### 方法

#### `save_projects()`

```python
def save_projects(self, projects: List[Project], report_type: str = "daily")
```

#### `get_recent_projects()`

```python
def get_recent_projects(self, days: int = 1, limit: int = 100) -> List[Project]
```

## WeChatNotifier

微信推送器。

### 构造函数

```python
WeChatNotifier(
    gateway_url: Optional[str] = None,
    gateway_token: Optional[str] = None,
    target: Optional[str] = None
)
```

### 方法

#### `send_report()`

```python
def send_report(self, report: TrendReport) -> bool
```
