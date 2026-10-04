"""Local educational knowledge base (sample content) indexed by the RAG pipeline.

Each entry: (skill_slug, topic_title, analogy, body). Bodies may contain one ```code``` block.
All roadmap topic descriptions are also indexed automatically, so every topic is retrievable.
"""

KNOWLEDGE = [
("python", "Variables", "A variable is a sticky label you put on a box; you can peel it off and stick it on a different box.",
"""A variable in Python is a name bound to an object. Assignment `x = 10` creates the integer object 10 and binds the name x to it. Python is dynamically typed: the type belongs to the object, not the name, so `x = 'ten'` later is legal. Names should be lowercase_with_underscores, can't start with a digit, and can't be keywords.
```python
score = 42
name = "Asha"
score = score + 8   # rebinding: score now refers to 50
print(name, score)
```
Common mistakes: using a variable before assigning it (NameError) and shadowing built-ins like `list` or `str`."""),
("python", "Conditions", "An if-statement is a railway switch: the train follows exactly one track depending on the signal.",
"""Conditions choose which block runs. Python evaluates `if`, then each `elif` in order, and runs `else` only if nothing matched. Any value can be tested: empty containers, 0, None and False are falsy.
```python
marks = 72
if marks >= 85:
    grade = "A"
elif marks >= 70:
    grade = "B"
else:
    grade = "C"
```
Indentation defines the block. Use `and`/`or`/`not` to combine conditions, and prefer `if items:` over `if len(items) > 0:`."""),
("python", "Loops", "A for-loop is a conveyor belt: each item arrives in turn and you do the same job on it.",
"""`for` iterates over any iterable (lists, strings, ranges, dicts). `while` repeats as long as a condition is true. `break` exits the loop; `continue` skips to the next iteration. `range(start, stop, step)` excludes stop.
```python
total = 0
for n in range(1, 6):
    if n == 3:
        continue
    total += n        # 1 + 2 + 4 + 5
print(total)          # 12
```
Use `enumerate()` when you need the index and `zip()` to walk two sequences together. Watch for while-loops whose condition never becomes false."""),
("python", "Functions", "A function is a recipe card: write it once, then cook from it whenever you like with different ingredients.",
"""Functions package reusable logic. Parameters receive arguments; `return` sends a value back (otherwise None is returned). Variables created inside a function are local to it.
```python
def area(width, height=1):
    \"\"\"Return the area of a rectangle.\"\"\"
    return width * height

print(area(3, 4))   # 12
print(area(5))      # 5, uses the default height
```
Avoid mutable default arguments like `def f(items=[])`: the list is created once and shared. Use `items=None` and create a new list inside."""),
("python", "Lists", "A list is a numbered row of lockers; you can open any locker by its number and swap what's inside.",
"""Lists are ordered, mutable sequences. Index from 0; negative indices count from the end. Slicing `a[1:3]` returns a new list. Useful methods: append, extend, insert, pop, remove, sort.
```python
nums = [5, 2, 9]
nums.append(1)
nums.sort()                 # [1, 2, 5, 9]
squares = [n * n for n in nums if n % 2]   # comprehension: [1, 25, 81]
```
Lists are mutable, so two names can refer to the same list; use `nums.copy()` when you need an independent copy."""),
("python", "Dictionaries", "A dictionary is a phone book: you look things up by name, not by position.",
"""Dicts map hashable keys to values with average O(1) lookup. Access with `d[key]` (KeyError if missing) or `d.get(key, default)`. Iterate with `.items()`.
```python
stock = {"apple": 3, "pear": 0}
stock["kiwi"] = 7
for fruit, qty in stock.items():
    if qty == 0:
        print("restock", fruit)
```
Keys must be immutable (str, int, tuple). Since Python 3.7 dicts preserve insertion order."""),
("python", "OOP", "A class is a blueprint for a house; each object is an actual house built from it, with its own furniture.",
"""Object-oriented programming bundles data (attributes) and behavior (methods) into objects. A class defines the structure; instances hold their own state. `self` is the instance a method acts on.
```python
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount

acc = Account("Ravi")
acc.deposit(100)
```
OOP helps when many functions share the same data. The pillars are encapsulation, inheritance, polymorphism and abstraction."""),
("python", "Inheritance", "Inheritance is a family recipe that a child copies and then tweaks one step of.",
"""A subclass inherits attributes and methods from its parent and can override them. `super()` calls the parent's version.
```python
class Animal:
    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):
        return "Woof"
```
Prefer composition when the relationship is 'has-a' rather than 'is-a'. Python resolves methods using the MRO (method resolution order)."""),
("python", "Decorators", "A decorator is gift wrapping: the present inside is the same, but it now arrives with extra behavior around it.",
"""A decorator is a function that takes a function and returns a new function, usually adding behavior before/after the call. `@decorator` above a def is shorthand for `func = decorator(func)`.
```python
import functools, time

def timer(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        print(f"{fn.__name__} took {time.perf_counter() - start:.3f}s")
        return result
    return wrapper

@timer
def slow_sum(n):
    return sum(range(n))
```
Decorators rely on closures: `wrapper` remembers `fn` from the enclosing scope. Use functools.wraps to keep the original name and docstring."""),
("python", "Generators", "A generator is a tap, not a bucket: water flows only when you open it, one cup at a time.",
"""A function containing `yield` returns a generator. Values are produced lazily on each `next()` call, so memory stays constant even for huge sequences.
```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

for x in countdown(3):
    print(x)   # 3 2 1
```
Generator expressions `(x*x for x in data)` are the lazy cousin of list comprehensions."""),
("python", "Async Programming", "Async is a chef starting the rice, then chopping vegetables while it cooks, instead of staring at the pot.",
"""`async def` defines a coroutine; `await` pauses it until an awaitable completes, letting the event loop run other tasks. It shines for I/O-bound work like network calls.
```python
import asyncio

async def fetch(i):
    await asyncio.sleep(1)      # stands in for a network call
    return i * 2

async def main():
    results = await asyncio.gather(*(fetch(i) for i in range(5)))
    print(results)              # finishes in ~1s, not 5s

asyncio.run(main())
```
Async doesn't make CPU-bound code faster; use multiprocessing for that."""),
("python", "Exceptions", "Exceptions are fire alarms: they interrupt normal flow and travel up until someone responds.",
"""Raise exceptions for exceptional conditions and catch the most specific type you can handle. `else` runs if no exception occurred; `finally` always runs.
```python
class InsufficientFunds(Exception):
    pass

try:
    withdraw(500)
except InsufficientFunds as e:
    print("Declined:", e)
finally:
    log_attempt()
```
Avoid bare `except:`; it hides bugs, including KeyboardInterrupt."""),
("java", "Classes and Objects", "A class is a cookie cutter; objects are the cookies.",
"""A Java class declares fields and methods. Constructors initialize new objects; access modifiers (private, public) control visibility.
```java
public class Student {
    private final String name;
    private int credits;

    public Student(String name) { this.name = name; }

    public void addCredits(int c) {
        if (c < 0) throw new IllegalArgumentException("negative");
        credits += c;
    }
}
```
Keep fields private and expose behavior through methods (encapsulation)."""),
("java", "Collections", "Collections are different kinds of containers: a list is a queue at a counter, a set is a guest list, a map is a coat check.",
"""The Collections Framework provides List (ordered, duplicates), Set (unique), and Map (key-value). Program to interfaces: `List<String> names = new ArrayList<>();`
```java
Map<String, Integer> counts = new HashMap<>();
for (String w : words) {
    counts.merge(w, 1, Integer::sum);
}
```
ArrayList gives O(1) random access; LinkedList O(1) insertion at ends; HashMap O(1) average lookup."""),
("java", "Streams", "A stream is an assembly line: items pass stations (filter, map) and are boxed at the end (collect).",
"""Streams process collections declaratively. Intermediate ops (filter, map, sorted) are lazy; a terminal op (collect, sum, forEach) triggers execution.
```java
List<String> top = students.stream()
    .filter(s -> s.getScore() >= 80)
    .map(Student::getName)
    .sorted()
    .collect(Collectors.toList());
```
Streams can be consumed once. Avoid side effects inside lambdas."""),
("java", "Multithreading", "Threads are several cooks in one kitchen; without rules they grab the same knife.",
"""Prefer ExecutorService over raw threads. Protect shared mutable state with synchronized, locks or atomic classes.
```java
ExecutorService pool = Executors.newFixedThreadPool(4);
Future<Integer> f = pool.submit(() -> expensive());
System.out.println(f.get());
pool.shutdown();
```
Race conditions occur when threads read-modify-write shared data without synchronization."""),
("cpp", "Pointers", "A pointer is a street address written on paper; the house is the actual data.",
"""A pointer stores a memory address. `&x` takes an address; `*p` dereferences. Use `nullptr` for 'no object'.
```cpp
int x = 10;
int* p = &x;
*p = 20;            // x is now 20
int* q = nullptr;   // never dereference q
```
Prefer references for non-null aliases and smart pointers for ownership."""),
("cpp", "Smart Pointers", "A smart pointer is a hotel key card that automatically deactivates when you check out.",
"""unique_ptr owns exclusively and frees memory when it goes out of scope; shared_ptr uses reference counting; weak_ptr observes without owning.
```cpp
#include <memory>
auto node = std::make_unique<Node>(42);
std::shared_ptr<Config> cfg = std::make_shared<Config>();
```
Avoid raw new/delete in modern C++. Break shared_ptr cycles with weak_ptr."""),
("cpp", "STL Containers", "STL containers are specialized storage units, each shaped for a different access pattern.",
"""vector is the default sequence container (contiguous, cache-friendly). map is a sorted tree (O(log n)); unordered_map is a hash table (O(1) average).
```cpp
std::vector<int> v{3, 1, 2};
std::sort(v.begin(), v.end());
std::unordered_map<std::string, int> freq;
for (auto& w : words) ++freq[w];
```
Reserve capacity with v.reserve(n) when the size is known."""),
("cpp", "Move Semantics", "Moving is handing over your house keys instead of building an identical house.",
"""Move semantics transfer resources from temporaries instead of copying them. std::move casts to an rvalue reference, enabling the move constructor.
```cpp
std::vector<std::string> a = load();
std::vector<std::string> b = std::move(a);  // a is valid but unspecified
```
Follow the rule of zero/five: either let the compiler generate special members or define all five."""),
("javascript", "Closures", "A closure is a backpack: a function carries the variables from where it was born wherever it goes.",
"""A closure is a function that remembers variables from its enclosing scope even after that scope has finished.
```javascript
function makeCounter() {
  let count = 0;
  return () => ++count;
}
const next = makeCounter();
next(); // 1
next(); // 2
```
Closures enable private state, factories and callbacks. Beware of capturing loop variables with var; use let."""),
("javascript", "Promises", "A promise is a restaurant buzzer: you get it now, and it lights up later with your order or an apology.",
"""A Promise represents a future value: pending, then fulfilled or rejected. Chain with .then/.catch or use async/await.
```javascript
fetch("/api/topics")
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));
```
Promise.all runs in parallel and fails fast; Promise.allSettled waits for all."""),
("javascript", "Async/Await", "await is a bookmark: the function pauses there and the rest of the program keeps reading.",
"""async functions always return a Promise. await pauses the function until the promise settles. Use try/catch for errors.
```javascript
async function loadUser(id) {
  try {
    const res = await fetch(`/users/${id}`);
    if (!res.ok) throw new Error(res.status);
    return await res.json();
  } catch (e) {
    console.error("failed", e);
  }
}
```
Run independent requests with Promise.all instead of awaiting them one by one."""),
("javascript", "DOM Manipulation", "The DOM is the page's family tree; JavaScript can add, move or remove relatives.",
"""The DOM represents HTML as a tree of nodes. Select with querySelector, change content with textContent, react to users with addEventListener.
```javascript
const btn = document.querySelector("#add");
btn.addEventListener("click", () => {
  const li = document.createElement("li");
  li.textContent = "New task";
  document.querySelector("#list").append(li);
});
```
Prefer textContent over innerHTML with user input to avoid XSS."""),
("sql", "JOINs", "A join is a matchmaker pairing rows from two tables that share a key.",
"""JOIN combines rows from tables using a condition. INNER JOIN keeps matches; LEFT JOIN keeps all rows from the left table.
```sql
SELECT s.name, c.title
FROM students s
LEFT JOIN enrollments e ON e.student_id = s.id
LEFT JOIN courses c ON c.id = e.course_id;
```
Always join on keys, and check for accidental row multiplication with one-to-many relations."""),
("sql", "GROUP BY and HAVING", "GROUP BY is sorting coins into piles by value, then counting each pile.",
"""GROUP BY collapses rows into groups; aggregates compute per group. WHERE filters rows before grouping, HAVING filters groups after.
```sql
SELECT department, AVG(salary) AS avg_salary
FROM employees
WHERE active = 1
GROUP BY department
HAVING AVG(salary) > 50000;
```
Every non-aggregated column in SELECT must appear in GROUP BY."""),
("sql", "Window Functions", "A window function is a rolling spotlight: each row stays on stage while nearby rows are lit up for the calculation.",
"""Window functions compute over a set of rows related to the current row without collapsing them.
```sql
SELECT name, dept, salary,
       RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS dept_rank,
       SUM(salary) OVER (ORDER BY hired_on) AS running_total
FROM employees;
```
Use them for rankings, running totals and period-over-period comparisons."""),
("sql", "Indexes", "An index is the index at the back of a book: jump to the page instead of reading every page.",
"""Indexes (usually B-trees) speed up lookups, joins and ordering on indexed columns at the cost of slower writes and extra storage.
```sql
CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);
```
Composite indexes follow the leftmost-prefix rule. Check with EXPLAIN."""),
("dsa", "Linked Lists", "A linked list is a treasure hunt: each clue tells you where the next clue is.",
"""A linked list stores nodes that point to the next node. Insertion/deletion at a known node is O(1), but access by index is O(n).
```python
class Node:
    def __init__(self, val, nxt=None):
        self.val, self.next = val, nxt

def reverse(head):
    prev = None
    while head:
        head.next, prev, head = prev, head, head.next
    return prev
```
Classic techniques: dummy head nodes and fast/slow pointers (cycle detection, middle node)."""),
("dsa", "Complexity Analysis", "Big-O is how a recipe's cooking time grows when you cook for 10 guests versus 1000.",
"""Big-O describes how running time or memory grows with input size n, ignoring constants. O(1) constant, O(log n) halving, O(n) one pass, O(n log n) efficient sorting, O(n^2) nested loops.
```python
def has_duplicate(xs):          # O(n) time, O(n) space
    seen = set()
    for x in xs:
        if x in seen:
            return True
        seen.add(x)
    return False
```
Trade space for time with hashing; always state both complexities in interviews."""),
("dsa", "Binary Search", "Binary search is finding a word in a dictionary by opening to the middle and discarding half each time.",
"""On sorted data, compare with the middle element and discard half. O(log n).
```python
def search(a, target):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target: return mid
        if a[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1
```
Off-by-one errors are the main risk; decide whether hi is inclusive or exclusive and stay consistent."""),
("dsa", "Dynamic Programming", "DP is keeping a notebook of answers so you never solve the same subproblem twice.",
"""DP solves problems with overlapping subproblems and optimal substructure. Define the state, the transition, and the base cases, then memoize (top-down) or tabulate (bottom-up).
```python
from functools import lru_cache

@lru_cache(None)
def climb(n):                  # ways to climb n stairs with steps of 1 or 2
    if n <= 1:
        return 1
    return climb(n - 1) + climb(n - 2)
```
Start from the brute-force recursion, then add caching."""),
("dsa", "Graphs Basics", "A graph is a city map: intersections are nodes and roads are edges.",
"""Represent graphs with adjacency lists. BFS explores level by level (shortest path in unweighted graphs); DFS goes deep first (cycles, components, topological order).
```python
from collections import deque
def bfs(graph, start):
    seen, q = {start}, deque([start])
    while q:
        node = q.popleft()
        for nb in graph[node]:
            if nb not in seen:
                seen.add(nb); q.append(nb)
    return seen
```
Mark nodes visited when enqueuing, not when dequeuing, to avoid duplicates."""),
("machine-learning", "Linear Regression", "Linear regression is drawing the straightest line through a scatter of points that keeps everyone as close as possible.",
"""Linear regression models y = w·x + b and fits w, b by minimizing mean squared error, either in closed form or with gradient descent.
```python
from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(X_train, y_train)
print(model.coef_, model.intercept_)
print(model.score(X_test, y_test))  # R^2
```
Check residuals for patterns; they signal a missing non-linear relationship."""),
("machine-learning", "Ensembles and Random Forests", "A random forest is asking a crowd of slightly different experts and taking a vote.",
"""A random forest trains many decision trees on bootstrap samples with random feature subsets and averages their votes, reducing variance compared with a single tree.
```python
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=0)
rf.fit(X_train, y_train)
print(rf.feature_importances_)
```
Forests need little preprocessing and give feature importances, but can be large and slower to predict."""),
("machine-learning", "Classification Metrics", "Precision asks 'of the alarms raised, how many were real fires?'; recall asks 'of the real fires, how many raised an alarm?'",
"""Accuracy can mislead on imbalanced data. Precision = TP/(TP+FP); recall = TP/(TP+FN); F1 is their harmonic mean. The confusion matrix shows all four outcomes.
```python
from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred))
```
Pick the metric that matches the cost of mistakes in your domain."""),
("machine-learning", "Neural Networks", "A neural network is a team passing a message down a line, each person adjusting it slightly, then learning from how wrong the final message was.",
"""A neural network stacks layers of weighted sums followed by non-linear activations. Training minimizes a loss by computing gradients with backpropagation and updating weights with an optimizer like SGD or Adam.
```python
import torch.nn as nn
model = nn.Sequential(nn.Linear(10, 32), nn.ReLU(), nn.Linear(32, 1))
```
Watch for overfitting: use validation data, regularization and early stopping."""),
]
