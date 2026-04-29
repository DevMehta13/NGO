# BDA Exam — Line-by-Line Walkthrough (Zero Background Edition)

> Read this file like a textbook. Every code line is explained. By the end you will know what each piece does and **why** it's there. Open this side-by-side with your Jupyter notebook.

---

# PART A — Tiny Python Concepts You'll See Everywhere

Before touching PySpark, just 6 things to know. They show up in every line of code below.

## A.1 — A list

```python
nums = [10, 20, 30, 40, 50]
```

A list = an ordered collection. **Index starts at 0**, not 1:

```python
nums[0]  # 10
nums[1]  # 20
nums[4]  # 50
```

## A.2 — A tuple (just a list with parentheses)

```python
pair = ("Mumbai", 200)
pair[0]  # "Mumbai"
pair[1]  # 200
```

A `(key, value)` tuple is the bread and butter of `reduceByKey`.

## A.3 — A dictionary

```python
totals = {"Mumbai": 360, "Delhi": 260}
totals["Mumbai"]  # 360
```

Like a list, but you look things up by name (called the "key") instead of by position.

## A.4 — `lambda` = a tiny function in one line

These two are the same thing:

```python
def double(x):
    return x * 2

double = lambda x: x * 2     # exact same function, just shorter
```

So whenever you see `lambda x: x * 2`, read it as "a function that takes `x` and returns `x * 2`."

In PySpark you'll write tons of these:

```python
lambda line: line.split(",")[4]    # "given a line, give me back position 4 after splitting by comma"
lambda a, b: a + b                  # "given two values, give me their sum"
lambda kv: kv[1]                    # "given a (key, value) tuple, give me the value"
```

## A.5 — `.split(",")` = chop a string into a list

```python
line = "1,D1,10,200,Mumbai"
parts = line.split(",")
# parts = ["1", "D1", "10", "200", "Mumbai"]

parts[0]   # "1"      ← ride_id
parts[1]   # "D1"     ← driver_id
parts[2]   # "10"     ← distance
parts[3]   # "200"    ← fare
parts[4]   # "Mumbai" ← city
```

> ⚠️ Everything from `.split(",")` is a **string**. `"200"` is text, not a number. To do math, you must wrap it: `float("200")` → `200.0`.

## A.6 — `for ... in ...` = loop

```python
for city, total in [("Mumbai", 360), ("Delhi", 260)]:
    print(city, total)
# Mumbai 360
# Delhi 260
```

When you loop over (key, value) tuples, Python lets you "unpack" them into two variables at once: `for city, total in ...`.

---

# PART B — PySpark Concepts in 60 Seconds

## B.1 — What is Spark?

A library for processing data **in parallel**. You give it a giant list, it splits work across CPU cores. For our small exam datasets, that doesn't matter — but the same code would work on millions of rows.

## B.2 — Two ways to handle data: RDD vs DataFrame

| | RDD | DataFrame |
|---|---|---|
| What it is | A "distributed list" of items | A "distributed table" with columns |
| You operate by | `map`, `filter`, `reduceByKey` | SQL-like: `select`, `filter`, `groupBy` |
| Used in exam for | Question (a) — reduceByKey stuff | Question (b) — Linear Regression |

Both are Spark, just two ways of looking at the same data.

## B.3 — `sc` vs `spark` (don't get confused)

```python
spark = SparkSession.builder.master("local[*]").getOrCreate()
sc = spark.sparkContext
```

- **`sc`** → the old "remote control" — used for **RDD** code (Question a).
- **`spark`** → the new "remote control" — used for **DataFrame/SQL** code (Question b).

You'll need both. **Always run the SparkSession cell first** in your notebook.

## B.4 — Transformations vs Actions

Spark is "lazy". When you write:

```python
rdd.map(...).filter(...)
```

Nothing actually happens yet. Spark just remembers the plan. It only **runs** when you call an "action" like:

- `.collect()` → bring everything back as a Python list
- `.first()` → grab the first item
- `.count()` → count the items
- `.saveAsTextFile(...)` → save to disk
- `.show()` (DataFrames) → print the table

So the pattern is always: **transform → transform → transform → action**.

---

# PART C — Always-First Cell

Run this **at the top of every notebook**, every time. Nothing else works without it.

```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[*]").appName("BDA").getOrCreate()
sc = spark.sparkContext
sc.setLogLevel("ERROR")
print("Spark version:", spark.version)
```

| Line | Plain English |
|---|---|
| `from pyspark.sql import SparkSession` | Pull the `SparkSession` class out of PySpark |
| `SparkSession.builder.master("local[*]")` | "I want a Spark session that runs locally on my laptop, using all CPU cores (`*`)" |
| `.appName("BDA")` | Just a name (visible in Spark UI). Cosmetic. |
| `.getOrCreate()` | If a session already exists, reuse it. Else, create one. Returns the session. |
| `sc = spark.sparkContext` | Get the older RDD interface. Save it as `sc`. |
| `sc.setLogLevel("ERROR")` | "Hide the noisy INFO/WARN logs. Only show errors." |
| `print(...)` | Sanity check that it worked. You should see `Spark version: 3.5.1`. |

---

# PART D — SET 1 (rides.csv) Walkthrough

Dataset:

```
ride_id, driver_id, distance, fare, city
1, D1, 10, 200, Mumbai
2, D2, 5,  120, Delhi
3, D1, 8,  160, Mumbai
4, D3, 12, 250, Pune
5, D2, 7,  140, Delhi
```

## D.0 — Make the CSV inside the notebook

You don't need to "find" or "upload" the file. Just create it inline.

```python
csv_text = """ride_id,driver_id,distance,fare,city
1,D1,10,200,Mumbai
2,D2,5,120,Delhi
3,D1,8,160,Mumbai
4,D3,12,250,Pune
5,D2,7,140,Delhi
"""
with open("rides.csv", "w") as f:
    f.write(csv_text)
print("rides.csv created")
```

| Line | Plain English |
|---|---|
| `csv_text = """..."""` | Triple-quoted strings let you write multiple lines without escape characters. The variable holds the raw CSV text. |
| `with open("rides.csv", "w") as f:` | Open a file called `rides.csv` for **w**riting. The `with` block auto-closes the file when done. |
| `f.write(csv_text)` | Write our string into the file. |
| `print(...)` | Confirm it worked. |

After this, a real `rides.csv` file lives in your folder. Spark can read it.

---

## D.1 — Question (a): Total fare per city using reduceByKey

### The 6-step pattern (memorize this shape):

1. **Read** file as RDD
2. **Remove** header
3. **Map** to (key, value) pairs
4. **Reduce** by key
5. **Display**
6. **Save**

### Full code:

```python
# Step 1: Read the file as an RDD
rdd_raw = sc.textFile("rides.csv")

# Step 2: Remove the header row
header = rdd_raw.first()
rdd = rdd_raw.filter(lambda line: line != header)

# Step 3: Make (city, fare) pairs
pairs = rdd.map(lambda line: (line.split(",")[4], float(line.split(",")[3])))

# Step 4: Sum fares per city
totals = pairs.reduceByKey(lambda a, b: a + b)

# Step 5: Display
for city, total in totals.collect():
    print(city, "->", total)

# Step 6: Save output
import shutil, os
if os.path.exists("output_a"): shutil.rmtree("output_a")
totals.saveAsTextFile("output_a")
```

### Line by line:

#### Step 1
```python
rdd_raw = sc.textFile("rides.csv")
```
- `sc.textFile(filename)` → reads the file. **Each line of the file becomes one item in the RDD.**
- `rdd_raw` is now conceptually:
  ```
  [
    "ride_id,driver_id,distance,fare,city",  ← header
    "1,D1,10,200,Mumbai",
    "2,D2,5,120,Delhi",
    "3,D1,8,160,Mumbai",
    "4,D3,12,250,Pune",
    "5,D2,7,140,Delhi"
  ]
  ```

#### Step 2
```python
header = rdd_raw.first()
rdd = rdd_raw.filter(lambda line: line != header)
```
- `rdd_raw.first()` → returns the first line: `"ride_id,driver_id,distance,fare,city"`. Saves it in the variable `header`.
- `rdd_raw.filter(lambda line: line != header)` → for every line in `rdd_raw`, keep it only if it is **not equal to** the header line. That removes the header from the RDD.
- After this step, `rdd` only has the 5 data rows, no header.

> Why filter the header? Because in step 3 we'll do `float(...)` on the fare column. If the header is still there, it would try `float("fare")` and crash.

#### Step 3 — the most important line
```python
pairs = rdd.map(lambda line: (line.split(",")[4], float(line.split(",")[3])))
```
- `.map(f)` → apply function `f` to each element. The result is a new RDD.
- The lambda function `lambda line: (line.split(",")[4], float(line.split(",")[3]))` does:
  - `line.split(",")` → splits the line into a list of fields.
  - `[4]` → grabs position 4, which is `city`.
  - `[3]` → grabs position 3, which is `fare` (as a string).
  - `float(...)` → converts `"200"` into the number `200.0`.
  - Wrap them as `(city, fare)` tuple.
- After this step, `pairs` is:
  ```
  [
    ("Mumbai", 200.0),
    ("Delhi",  120.0),
    ("Mumbai", 160.0),
    ("Pune",   250.0),
    ("Delhi",  140.0)
  ]
  ```

> 💡 **Counting tip**: To know which index to use, count the columns of the CSV header **starting at 0**. Always.

#### Step 4 — the magic
```python
totals = pairs.reduceByKey(lambda a, b: a + b)
```
- `reduceByKey` works only on RDDs of `(key, value)` pairs.
- It groups all pairs by their **key** (first element).
- Then for each group, it combines the values pairwise using the function you give it.
- `lambda a, b: a + b` means "add two values together".
- So Mumbai's values `[200.0, 160.0]` → combined: `200 + 160 = 360`.
- Delhi's `[120.0, 140.0]` → `260`.
- Pune's `[250.0]` → `250` (only one, no combining needed).
- Result:
  ```
  [
    ("Mumbai", 360.0),
    ("Delhi",  260.0),
    ("Pune",   250.0)
  ]
  ```

#### Step 5 — display
```python
for city, total in totals.collect():
    print(city, "->", total)
```
- `.collect()` → "**action**" — pulls the data from Spark workers back to normal Python. Returns a regular Python list.
- The for-loop iterates the list and unpacks each tuple into `city` and `total`.
- Output:
  ```
  Mumbai -> 360.0
  Delhi -> 260.0
  Pune -> 250.0
  ```

#### Step 6 — save
```python
import shutil, os
if os.path.exists("output_a"): shutil.rmtree("output_a")
totals.saveAsTextFile("output_a")
```
- Spark **refuses** to write to an existing folder. So we delete `output_a` first if it exists.
- `os.path.exists("output_a")` → True if the folder is there.
- `shutil.rmtree("output_a")` → recursively delete the folder.
- `totals.saveAsTextFile("output_a")` → write the RDD into a folder called `output_a`. Inside, you'll find files named `part-00000` etc., containing the text output.

### Variants you should know

If they ask **count** instead of **sum**:
```python
pairs = rdd.map(lambda line: (line.split(",")[1], 1))   # (driver_id, 1)
counts = pairs.reduceByKey(lambda a, b: a + b)          # add the 1s
```

If they ask **max**:
```python
maxes = pairs.reduceByKey(lambda a, b: max(a, b))
```

If they ask **average** (sum + count, then divide):
```python
pairs = rdd.map(lambda line: (line.split(",")[4], (float(line.split(",")[3]), 1)))
combined = pairs.reduceByKey(lambda a, b: (a[0]+b[0], a[1]+b[1]))
avg = combined.mapValues(lambda v: v[0] / v[1])
```

If they ask **sort by value descending**:
```python
sorted_desc = totals.sortBy(lambda kv: kv[1], ascending=False)
```

---

## D.2 — Question (b): Linear Regression: distance → fare

> "Use distance as feature, fare as label, train Linear Regression, show predictions, print coefficients & intercept."

### What is Linear Regression?

It draws a straight line `y = m·x + c` that best fits the data.
- `y` = label (what we want to predict — here, `fare`)
- `x` = feature (what we use to predict — here, `distance`)
- `m` = coefficient (slope)
- `c` = intercept

So we're saying: "predict fare based on distance, and tell me the formula."

### Full code:

```python
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression

# Step 1: Read CSV as a DataFrame
df = spark.read.csv("rides.csv", header=True, inferSchema=True)
df.show()

# Step 2: Build feature vector
assembler = VectorAssembler(inputCols=["distance"], outputCol="features")
data = assembler.transform(df).select("features", df["fare"].alias("label"))
data.show()

# Step 3: Train the model
lr = LinearRegression(featuresCol="features", labelCol="label")
model = lr.fit(data)

# Step 4: Predictions
predictions = model.transform(data)
predictions.select("features", "label", "prediction").show()

# Step 5: Coefficients & intercept
print("Coefficients:", model.coefficients)
print("Intercept:", model.intercept)
```

### Line by line:

#### Imports
```python
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
```
- `VectorAssembler` → the helper that packages columns into a vector.
- `LinearRegression` → the model class itself.

#### Step 1
```python
df = spark.read.csv("rides.csv", header=True, inferSchema=True)
```
- `spark.read.csv(...)` → reads the CSV as a **DataFrame** (a table).
- `header=True` → the first row contains column names (not data).
- `inferSchema=True` → Spark guesses the types automatically — `distance` becomes int, `fare` becomes int. This means **you don't have to do `float(...)` like in RDD code.**
- `df.show()` → prints the DataFrame as a nice formatted table.

#### Step 2 — VectorAssembler
```python
assembler = VectorAssembler(inputCols=["distance"], outputCol="features")
data = assembler.transform(df).select("features", df["fare"].alias("label"))
data.show()
```

Why is this even needed? PySpark ML algorithms refuse to take individual columns. They demand **one column** where each row is a vector containing all the feature values.

- `VectorAssembler(inputCols=["distance"], outputCol="features")` → "Take the column called `distance` and pack it into a vector. Put the result into a new column called `features`."
- `assembler.transform(df)` → run the assembler. Returns a new DataFrame with the extra `features` column added.
- `.select("features", df["fare"].alias("label"))` → keep only two columns:
  - `features` (the vector)
  - `fare` renamed to `label` (because Spark ML expects exactly the names `features` and `label` by default)
- `.alias("label")` → just renames `fare` → `label`.

After this, `data` looks like:

```
+--------+-----+
|features|label|
+--------+-----+
|  [10.0]|  200|
|  [5.0] |  120|
|  [8.0] |  160|
|  [12.0]|  250|
|  [7.0] |  140|
+--------+-----+
```

#### Step 3 — train
```python
lr = LinearRegression(featuresCol="features", labelCol="label")
model = lr.fit(data)
```
- `LinearRegression(featuresCol=..., labelCol=...)` → create the model object. Tell it which columns to use.
- `.fit(data)` → **train it on `data`**. This is the actual learning step. Returns a fitted model.

#### Step 4 — predict
```python
predictions = model.transform(data)
predictions.select("features", "label", "prediction").show()
```
- `model.transform(data)` → run the trained model on the data. Adds a new column called `prediction`.
- `.select(...)` → just pick the columns you want to display.
- The output shows `features`, `label` (true value), `prediction` (model's guess) side-by-side.

#### Step 5 — answer the question
```python
print("Coefficients:", model.coefficients)
print("Intercept:", model.intercept)
```
- `model.coefficients` → the slope `m` for each feature. It's a vector because there could be many features.
- `model.intercept` → the intercept `c`.

So the formula learned is: `fare ≈ coefficient × distance + intercept`.

---

## D.3 — Question (c): Graph: Driver → City, degree centrality

### What is a graph here?

In CS, a graph = **vertices (nodes)** connected by **edges**. Think of a map: cities (vertices) connected by roads (edges).

The question says "Driver → City" — that means each row in the CSV is an edge from a driver to a city.

### What is degree centrality?

For each node = (number of edges connected to it) / (max possible edges).
- Big number = important/connected node.
- Small number = isolated.

### Full code:

```python
import networkx as nx
import pandas as pd

# Step 1: Read CSV with pandas (easier for graphs than Spark)
pdf = pd.read_csv("rides.csv")
print(pdf)

# Step 2: Create directed graph (because the question says Driver → City)
G = nx.DiGraph()

# Step 3: Add vertices (nodes)
for d in pdf["driver_id"].unique():
    G.add_node(d, type="driver")
for c in pdf["city"].unique():
    G.add_node(c, type="city")

# Step 4: Add edges
for _, row in pdf.iterrows():
    G.add_edge(row["driver_id"], row["city"])

# Step 5: Show vertices and edges
print("Vertices:", list(G.nodes))
print("Edges:", list(G.edges))

# Step 6: Degree centrality
centrality = nx.degree_centrality(G)
for node, score in centrality.items():
    print(f"{node}: {score:.3f}")

# Step 7 (optional): Draw it
import matplotlib.pyplot as plt
nx.draw(G, with_labels=True, node_color="lightblue", node_size=1500, arrows=True)
plt.show()
```

### Line by line:

#### Imports
```python
import networkx as nx        # graph library
import pandas as pd          # easy CSV reading
```
- `nx` and `pd` are just shorter nicknames so you don't type the full names every time.

#### Step 1
```python
pdf = pd.read_csv("rides.csv")
print(pdf)
```
- `pd.read_csv(...)` → reads the CSV into a **pandas** DataFrame (different from Spark DataFrame, but similar idea — a table).
- `pdf` is shorter for "pandas DataFrame".
- Why pandas instead of Spark for graphs? Pandas is simpler for tiny data, and NetworkX works directly with pandas data.

#### Step 2
```python
G = nx.DiGraph()
```
- `nx.DiGraph()` → make an empty **D**irected graph. "Directed" means edges have arrows (a → b is different from b → a).
- Use `nx.Graph()` if the question doesn't show an arrow.

#### Step 3 — add vertices
```python
for d in pdf["driver_id"].unique():
    G.add_node(d, type="driver")
for c in pdf["city"].unique():
    G.add_node(c, type="city")
```
- `pdf["driver_id"]` → the column of all driver IDs.
- `.unique()` → keep only distinct values: `["D1", "D2", "D3"]`.
- For each one: `G.add_node(d, type="driver")` → add it as a node, with extra label `type="driver"` (optional, just helps).
- Same loop for cities: `["Mumbai", "Delhi", "Pune"]`.

#### Step 4 — add edges
```python
for _, row in pdf.iterrows():
    G.add_edge(row["driver_id"], row["city"])
```
- `pdf.iterrows()` → loops over every row of the DataFrame. Each iteration gives `(index, row)`.
- `_` is a throwaway variable for the index (we don't care about it).
- `row["driver_id"]` and `row["city"]` → grab those values from the row.
- `G.add_edge(a, b)` → add an edge from `a` to `b`.

#### Step 5 — display
```python
print("Vertices:", list(G.nodes))
print("Edges:", list(G.edges))
```
- `G.nodes` → all vertices.
- `G.edges` → all edges as tuples like `("D1", "Mumbai")`.

#### Step 6 — degree centrality
```python
centrality = nx.degree_centrality(G)
for node, score in centrality.items():
    print(f"{node}: {score:.3f}")
```
- `nx.degree_centrality(G)` → returns a **dictionary** like `{"D1": 0.4, "D2": 0.4, ...}`.
- `.items()` → iterate over key-value pairs of the dict.
- `f"{node}: {score:.3f}"` → "f-string" — format the score to 3 decimals.

#### Step 7 — draw (optional, but pretty)
```python
import matplotlib.pyplot as plt
nx.draw(G, with_labels=True, node_color="lightblue", node_size=1500, arrows=True)
plt.show()
```
- `nx.draw(...)` → render the graph.
- `with_labels=True` → show node names on each circle.
- `arrows=True` → show direction arrows (since it's a directed graph).
- `plt.show()` → make the plot appear in the notebook.

---

# PART E — SET 2 (delivery.csv) Walkthrough

Dataset:

```
delivery_id, agent_id, distance, delivery_time, zone
1, A1, 5,  30, Zone1
2, A2, 8,  45, Zone2
3, A1, 6,  35, Zone1
4, A3, 10, 60, Zone3
5, A2, 7,  40, Zone2
```

> **The pattern is identical to Set 1.** Only the column names and indexes change. Plus question (a) wants you to **sort the result in descending order**.

## E.0 — Make the CSV

```python
csv_text = """delivery_id,agent_id,distance,delivery_time,zone
1,A1,5,30,Zone1
2,A2,8,45,Zone2
3,A1,6,35,Zone1
4,A3,10,60,Zone3
5,A2,7,40,Zone2
"""
with open("delivery.csv","w") as f:
    f.write(csv_text)
print("delivery.csv created")
```

## E.1 — Question (a): Total delivery_time per zone, sorted desc

```python
rdd_raw = sc.textFile("delivery.csv")
header = rdd_raw.first()
rdd = rdd_raw.filter(lambda line: line != header)

# Indexes: 0=delivery_id, 1=agent_id, 2=distance, 3=delivery_time, 4=zone
pairs = rdd.map(lambda line: (line.split(",")[4], float(line.split(",")[3])))
totals = pairs.reduceByKey(lambda a, b: a + b)

# NEW: sort descending by total
sorted_desc = totals.sortBy(lambda kv: kv[1], ascending=False)

for zone, total in sorted_desc.collect():
    print(zone, "->", total)

import shutil, os
if os.path.exists("output_a"): shutil.rmtree("output_a")
sorted_desc.saveAsTextFile("output_a")
```

### What's new vs Set 1: just one line

```python
sorted_desc = totals.sortBy(lambda kv: kv[1], ascending=False)
```
- `sortBy(f)` → sort the RDD using function `f` to extract the sort key.
- `lambda kv: kv[1]` → for each tuple `(key, value)`, sort by `value` (which is at index 1).
- `ascending=False` → biggest first.

Expected output:
```
Zone2 -> 85.0   (45 + 40)
Zone1 -> 65.0   (30 + 35)
Zone3 -> 60.0
```

## E.2 — Question (b): Linear Regression distance → delivery_time

**Identical to Set 1 (b)**, just change file and column names:

```python
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression

df = spark.read.csv("delivery.csv", header=True, inferSchema=True)
df.show()

assembler = VectorAssembler(inputCols=["distance"], outputCol="features")
data = assembler.transform(df).select("features", df["delivery_time"].alias("label"))
data.show()

lr = LinearRegression(featuresCol="features", labelCol="label")
model = lr.fit(data)

predictions = model.transform(data)
predictions.select("features", "label", "prediction").show()

print("Coefficients:", model.coefficients)
print("Intercept:", model.intercept)
```

**Differences from Set 1 (b):** only `"rides.csv"` → `"delivery.csv"` and `"fare"` → `"delivery_time"`. Everything else identical.

## E.3 — Question (c): Graph Agent → Zone, degree centrality

**Identical to Set 1 (c)**, just rename columns:

```python
import networkx as nx
import pandas as pd

pdf = pd.read_csv("delivery.csv")
print(pdf)

G = nx.DiGraph()

for a in pdf["agent_id"].unique():
    G.add_node(a, type="agent")
for z in pdf["zone"].unique():
    G.add_node(z, type="zone")

for _, row in pdf.iterrows():
    G.add_edge(row["agent_id"], row["zone"])

print("Vertices:", list(G.nodes))
print("Edges:", list(G.edges))

centrality = nx.degree_centrality(G)
for node, score in centrality.items():
    print(f"{node}: {score:.3f}")

import matplotlib.pyplot as plt
nx.draw(G, with_labels=True, node_color="lightgreen", node_size=1500, arrows=True)
plt.show()
```

**Differences from Set 1 (c):** `rides.csv` → `delivery.csv`, `driver_id` → `agent_id`, `city` → `zone`. Everything else identical.

---

# PART F — Pattern Recognition Cheat Sheet

When you see a question on the exam, identify the type and apply the pattern.

## F.1 — Pattern: RDD reduceByKey

**Signal words:** "key-value pairs", "reduceByKey", "total per...", "count per...".

**Skeleton:**
```python
rdd = sc.textFile(FILE).filter(lambda l: l != HEADER_LINE)
pairs = rdd.map(lambda l: (l.split(",")[KEY_INDEX], TYPE(l.split(",")[VALUE_INDEX])))
result = pairs.reduceByKey(lambda a, b: COMBINE(a, b))
```

Fill in the blanks:
- `FILE` = the CSV name
- `HEADER_LINE` = whatever you got from `.first()`
- `KEY_INDEX` = column position to group by (0-based!)
- `VALUE_INDEX` = column position to combine
- `TYPE` = `float` or `int` (numbers) or remove it (strings)
- `COMBINE` = `+` (sum), `max`, `min`, `lambda a,b: a+1` (count), etc.

## F.2 — Pattern: Linear Regression

**Signal words:** "feature", "label", "Linear Regression", "coefficients", "intercept".

**Skeleton (5 lines):**
```python
df = spark.read.csv(FILE, header=True, inferSchema=True)
data = VectorAssembler(inputCols=[FEATURE_COL], outputCol="features").transform(df).select("features", df[LABEL_COL].alias("label"))
model = LinearRegression(featuresCol="features", labelCol="label").fit(data)
model.transform(data).show()
print(model.coefficients, model.intercept)
```

Fill in:
- `FILE` = the CSV name
- `FEATURE_COL` = column used as input (e.g. `"distance"`)
- `LABEL_COL` = column to predict (e.g. `"fare"`)

## F.3 — Pattern: NetworkX Graph

**Signal words:** "graph", "vertices", "edges", "degree centrality", "X → Y".

**Skeleton:**
```python
pdf = pd.read_csv(FILE)
G = nx.DiGraph()                                      # use nx.Graph() if no arrow
for x in pdf[COL_FROM].unique(): G.add_node(x)
for y in pdf[COL_TO].unique():   G.add_node(y)
for _, row in pdf.iterrows():
    G.add_edge(row[COL_FROM], row[COL_TO])
print(nx.degree_centrality(G))
```

Fill in:
- `FILE` = CSV name
- `COL_FROM` = column for source nodes (left of arrow)
- `COL_TO` = column for destination nodes (right of arrow)

---

# PART G — When Things Go Wrong

| Error you see | What's likely wrong | Fix |
|---|---|---|
| `NameError: name 'spark' is not defined` | You didn't run the SparkSession cell | Run the first cell |
| `Path output_a already exists` | You ran `saveAsTextFile` twice | The `shutil.rmtree(...)` line should handle this. Re-run that cell. |
| `ValueError: could not convert string to float: 'fare'` | You forgot to skip the header | Make sure the `filter(lambda l: l != header)` line ran |
| `IndexError: list index out of range` | Wrong column index in `.split(",")[N]` | Recount columns starting at 0 |
| `Column 'X' not found` | Typo in column name | `print(df.columns)` to see exact names |
| Notebook spinner stuck forever | Spark hung | Kernel menu → Restart Kernel → re-run from top |
| `ModuleNotFoundError: No module named 'pyspark'` | You're running plain Python, not in the spark-bda container | Use Jupyter inside Docker via `start.sh` |

---

# PART H — The 30-Second Pre-Exam Recap

1. `bash ~/Desktop/bdaexam/start.sh` → Jupyter opens.
2. New notebook → first cell = SparkSession (Part C).
3. Second cell = create CSV (Part D.0 / E.0).
4. Read question → identify pattern → apply skeleton (Part F).
5. Run cells with **Shift+Enter**. Read output. Move on.
6. Save with **Cmd+S** when done.

You've got this. 🚀
