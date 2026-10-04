"""Hand-written multiple-choice question bank.

Tuple: (topic_title, difficulty 1-3, question, options, answer_index, explanation)
Topics without enough hand-written questions are topped up by the structural
question generator in services/quiz.py.
"""

Q = dict()

Q["python"] = [
("Variables", 1, "What does `x = 5; x = 'five'` demonstrate in Python?", ["A syntax error", "Dynamic typing: a name can be rebound to a value of another type", "Static typing", "Constant declaration"], 1, "Python names are labels bound to objects; rebinding to a different type is allowed."),
("Variables", 1, "Which is a valid Python variable name?", ["2nd_value", "second-value", "second_value", "class"], 2, "Names can't start with a digit, contain hyphens, or be reserved keywords like `class`."),
("Data Types", 1, "What is `type(3 / 2)`?", ["int", "float", "decimal", "str"], 1, "`/` is true division and always returns a float in Python 3 (1.5)."),
("Data Types", 1, "What does `int('7') + 3` evaluate to?", ["'73'", "10", "TypeError", "7.3"], 1, "`int('7')` converts the string to 7; 7 + 3 = 10."),
("Input/Output", 1, "What does `input()` return?", ["An int if you type digits", "Always a str", "A list", "None"], 1, "`input()` always returns a string; convert with int()/float() when needed."),
("Operators", 1, "What is `7 // 2`?", ["3.5", "3", "4", "1"], 1, "`//` is floor division."),
("Operators", 1, "What is `7 % 3`?", ["2", "1", "2.33", "0"], 1, "`%` gives the remainder: 7 = 2*3 + 1."),
("Conditions", 1, "Which value is falsy in Python?", ["'0'", "[0]", "0", "' '"], 2, "0, '', [], {}, None and False are falsy; '0' and [0] are non-empty and truthy."),
("Loops", 1, "How many times does `for i in range(2, 8, 2):` run?", ["3", "4", "6", "8"], 0, "range(2, 8, 2) yields 2, 4, 6."),
("Loops", 1, "What does `break` do inside a loop?", ["Skips to the next iteration", "Exits the nearest enclosing loop", "Exits the program", "Restarts the loop"], 1, "`continue` skips; `break` exits the loop."),
("Functions", 1, "What does a function return if it has no return statement?", ["0", "None", "An empty string", "It raises an error"], 1, "Python functions implicitly return None."),
("Functions", 2, "Why is `def f(items=[]):` a common bug?", ["Lists aren't allowed as defaults", "The default list is created once and shared across calls", "It makes items immutable", "It's a syntax error"], 1, "Default values are evaluated once at definition time; use `None` and create the list inside."),
("Lists", 1, "What is `[1, 2, 3, 4][1:3]`?", ["[1, 2, 3]", "[2, 3]", "[2, 3, 4]", "[1, 2]"], 1, "Slices include the start index and exclude the stop index."),
("Lists", 2, "What does `[x*x for x in range(4) if x % 2 == 0]` produce?", ["[0, 4]", "[0, 1, 4, 9]", "[4]", "[1, 9]"], 0, "Even x are 0 and 2; their squares are 0 and 4."),
("Tuples", 1, "Which statement about tuples is true?", ["They are mutable", "They can't hold mixed types", "They are immutable sequences", "They can't be dictionary keys"], 2, "Tuples are immutable, so (hashable) tuples can be dict keys."),
("Sets", 1, "What is `len({1, 2, 2, 3, 3, 3})`?", ["6", "3", "1", "Error"], 1, "Sets keep only unique elements."),
("Dictionaries", 1, "What does `d.get('k', 0)` do when 'k' is missing?", ["Raises KeyError", "Returns 0", "Adds 'k' to d", "Returns None always"], 1, "`get` returns the default when the key is absent, without modifying the dict."),
("Strings", 1, "What does `'a,b,c'.split(',')` return?", ["'abc'", "['a', 'b', 'c']", "('a','b','c')", "['a,b,c']"], 1, "split returns a list of substrings."),
("Basic Error Handling", 1, "Which exception does `int('abc')` raise?", ["TypeError", "ValueError", "KeyError", "SyntaxError"], 1, "The type is right (str) but the value can't be parsed, so ValueError."),
("Basic File Handling", 1, "Why use `with open(...) as f:`?", ["It's faster", "It guarantees the file is closed, even on errors", "It opens the file in binary mode", "It's required for reading"], 1, "The context manager closes the file automatically."),
("Modules", 2, "What does `if __name__ == '__main__':` guard?", ["Code that runs only when the file is executed directly", "Code that runs on import", "Class definitions", "Private functions"], 0, "When imported, __name__ is the module name, so the block is skipped."),
("OOP", 2, "In a method, what does `self` refer to?", ["The class", "The current instance", "The parent class", "The module"], 1, "`self` is the instance the method was called on."),
("Classes", 2, "What's the difference between a class attribute and an instance attribute?", ["No difference", "Class attributes are shared by all instances; instance attributes are per object", "Instance attributes are shared", "Class attributes can't be read from instances"], 1, "Attributes set on the class are shared; those set on self are per instance."),
("Inheritance", 2, "What does `super().__init__()` do in a subclass?", ["Creates a new parent object", "Calls the parent class initializer on the current instance", "Deletes the parent", "Imports the parent"], 1, "It delegates to the next class in the MRO."),
("Polymorphism", 2, "Duck typing means...", ["Objects are checked by class name", "Any object with the needed methods can be used", "Only subclasses are accepted", "Types are declared explicitly"], 1, "'If it walks like a duck...' — behavior matters, not declared type."),
("Generators", 2, "What does a function containing `yield` return when called?", ["A list", "A generator object", "None", "The first yielded value"], 1, "Calling it creates a lazy generator; values are produced on iteration."),
("Decorators", 2, "`@timer` above `def f():` is equivalent to...", ["f = timer", "f = timer(f)", "timer = f(timer)", "f()"], 1, "A decorator is a callable that receives the function and returns a replacement."),
("Exceptions", 2, "When does a `finally` block run?", ["Only if no exception occurred", "Only if an exception occurred", "Always, after try/except", "Never with return"], 2, "finally always runs, even with return or an unhandled exception."),
("JSON", 2, "`json.loads('{\"a\": 1}')` returns...", ["A str", "A dict", "A JSON object type", "A tuple"], 1, "loads parses JSON text into Python objects; objects become dicts."),
("Testing", 2, "In pytest, a test function is discovered if its name...", ["Ends with _test", "Starts with test", "Is in uppercase", "Contains assert"], 1, "pytest collects functions named test_* in files named test_*.py or *_test.py."),
("Context Managers", 3, "Which methods make a class usable in a `with` statement?", ["__init__ and __del__", "__enter__ and __exit__", "__open__ and __close__", "__iter__ and __next__"], 1, "The context manager protocol is __enter__/__exit__."),
("Async Programming", 3, "What happens if you call an `async def` function without awaiting it?", ["It runs synchronously", "You get a coroutine object that hasn't run", "It raises SyntaxError", "It runs in a thread"], 1, "Coroutines only run when awaited or scheduled on the event loop."),
("Concurrency", 3, "Why don't threads speed up CPU-bound pure-Python code in CPython?", ["Threads are disabled", "The GIL lets only one thread execute Python bytecode at a time", "Threads use too much memory", "Python has no threads"], 1, "Use multiprocessing for CPU-bound work; threads help I/O-bound work."),
("Memory Management", 3, "CPython frees most objects primarily via...", ["Manual free()", "Reference counting, plus a cycle collector", "Only a mark-and-sweep GC", "The OS"], 1, "Reference counts drop to zero → immediate deallocation; the GC handles cycles."),
("Design Patterns", 3, "The Strategy pattern is best described as...", ["Ensuring one instance exists", "Swapping interchangeable algorithms behind a common interface", "Notifying subscribers", "Building complex objects step by step"], 1, "Strategy encapsulates interchangeable behaviors."),
]

Q["java"] = [
("Variables and Primitive Types", 1, "Which is a primitive type in Java?", ["String", "Integer", "int", "ArrayList"], 2, "int is primitive; Integer is its wrapper class."),
("Control Flow", 1, "What does `for (int i = 0; i < 3; i++)` iterate over?", ["0,1,2", "1,2,3", "0,1,2,3", "1,2"], 0, "Starts at 0, stops before 3."),
("Strings and StringBuilder", 1, "Why compare strings with `.equals()` instead of `==`?", ["== is slower", "== compares references, equals compares content", "equals is required by the compiler", "They're identical"], 1, "== checks object identity."),
("Classes and Objects", 2, "What is a constructor?", ["A method that returns the class", "A special method that initializes a new object", "A static factory", "A destructor"], 1, "Constructors share the class name and have no return type."),
("OOP Principles", 2, "Which principle hides internal state behind methods?", ["Inheritance", "Encapsulation", "Polymorphism", "Abstraction"], 1, "Encapsulation restricts direct access to fields."),
("Exceptions", 2, "Which must be declared or caught?", ["RuntimeException", "NullPointerException", "Checked exceptions like IOException", "Errors"], 2, "The compiler enforces handling of checked exceptions."),
("Collections", 2, "Which collection disallows duplicates?", ["ArrayList", "LinkedList", "HashSet", "Vector"], 2, "Set implementations store unique elements."),
("Generics", 2, "What does `List<? extends Number>` allow?", ["Adding any Number", "Reading elements as Number", "Only Integer", "Nothing"], 1, "Upper-bounded wildcards are safe to read from (producer extends)."),
("Streams", 2, "Stream intermediate operations like `filter` are...", ["Executed immediately", "Lazy until a terminal operation runs", "Always parallel", "Mutating the source"], 1, "Nothing executes until a terminal op like collect()."),
("Multithreading", 3, "What does `synchronized` provide?", ["Faster execution", "Mutual exclusion and memory visibility", "Automatic parallelism", "Deadlock prevention"], 1, "Only one thread holds the monitor at a time."),
("Memory and Garbage Collection", 3, "Where are objects created with `new` allocated?", ["Stack", "Heap", "Metaspace", "Registers"], 1, "Objects live on the heap; local references live on the stack."),
("Spring Boot", 3, "Dependency injection in Spring means...", ["Classes create their own dependencies", "The container supplies dependencies to beans", "Using static singletons", "Importing jars"], 1, "The IoC container wires beans together."),
]

Q["cpp"] = [
("Variables and Types", 1, "What does `auto x = 3.0;` deduce?", ["int", "float", "double", "auto"], 2, "Floating literals without a suffix are double."),
("Functions", 1, "`void f(int& x)` passes x...", ["By value", "By reference", "By pointer", "As const"], 1, "Changes to x affect the caller's variable."),
("Pointers", 1, "What does `*p` do when p is `int*`?", ["Gets p's address", "Dereferences p to access the int", "Multiplies p", "Declares a pointer"], 1, "Unary * dereferences."),
("References", 1, "A reference must be...", ["Initialized when declared", "Nullable", "Reseated later", "Heap allocated"], 0, "References bind once, at initialization."),
("Memory and the Heap", 2, "What is the problem with `new` without `delete`?", ["Compile error", "Memory leak", "Stack overflow", "Nothing"], 1, "Heap memory stays allocated."),
("RAII", 2, "RAII ties resource lifetime to...", ["Global variables", "Object lifetime (constructor acquires, destructor releases)", "The garbage collector", "Threads"], 1, "Resources are released deterministically when objects go out of scope."),
("Inheritance and Polymorphism", 2, "Why make a base class destructor `virtual`?", ["Speed", "So deleting via a base pointer calls the derived destructor", "Required by STL", "To prevent inheritance"], 1, "Otherwise behavior is undefined when deleting through a base pointer."),
("STL Containers", 2, "Average lookup in `std::unordered_map` is...", ["O(log n)", "O(1)", "O(n)", "O(n log n)"], 1, "It's a hash table."),
("Templates", 2, "Templates are instantiated at...", ["Runtime", "Compile time", "Link time only", "Load time"], 1, "The compiler generates code per used type."),
("Smart Pointers", 3, "Which smart pointer expresses sole ownership?", ["shared_ptr", "weak_ptr", "unique_ptr", "auto_ptr"], 2, "unique_ptr is move-only and owns exclusively."),
("Move Semantics", 3, "What does `std::move(x)` actually do?", ["Moves memory", "Casts x to an rvalue reference so it may be moved from", "Copies x", "Deletes x"], 1, "It's a cast; the move constructor does the work."),
("Concurrency", 3, "What prevents a data race on a shared counter?", ["volatile", "std::mutex or std::atomic", "static", "inline"], 1, "volatile does not provide atomicity in C++."),
]

Q["javascript"] = [
("Variables and Types", 1, "Which declaration can't be reassigned?", ["var", "let", "const", "function"], 2, "const bindings can't be reassigned (objects can still be mutated)."),
("Operators and Conditionals", 1, "What is `'5' == 5`?", ["true", "false", "TypeError", "undefined"], 0, "== coerces types; === would be false."),
("Arrays", 1, "What does `[1,2,3].map(x => x * 2)` return?", ["[2,4,6]", "6", "[1,2,3]", "undefined"], 0, "map returns a new transformed array."),
("Objects", 1, "`const {a} = {a: 1, b: 2}` sets a to...", ["{a:1}", "1", "undefined", "2"], 1, "Object destructuring."),
("DOM Manipulation", 1, "Which selects the first element matching a CSS selector?", ["getElementsByClassName", "querySelector", "querySelectorAll", "getElement"], 1, "querySelector returns the first match."),
("Closures", 2, "A closure is...", ["A closed function", "A function plus the lexical scope it was created in", "An IIFE", "A class"], 1, "Inner functions keep access to outer variables."),
("Scope and Hoisting", 2, "Accessing a `let` variable before its declaration throws because of...", ["Hoisting to undefined", "The temporal dead zone", "Strict mode", "Garbage collection"], 1, "let/const are hoisted but uninitialized."),
("this and Prototypes", 2, "Arrow functions get `this` from...", ["The caller", "The enclosing lexical scope", "The global object always", "bind()"], 1, "Arrow functions don't have their own this."),
("Promises", 2, "`Promise.all` rejects when...", ["All promises reject", "Any promise rejects", "Never", "The last one rejects"], 1, "It fails fast on the first rejection."),
("Async/Await", 2, "`await` can be used...", ["Anywhere", "Inside async functions (and top-level modules)", "Only in loops", "Only with fetch"], 1, "It pauses the async function until the promise settles."),
("Event Loop", 3, "Which runs first: a resolved promise's `.then` callback or `setTimeout(fn, 0)`?", ["setTimeout", "The promise callback (microtask)", "Random", "Both at once"], 1, "Microtasks drain before the next macrotask."),
("Modules", 2, "What does `export default` allow?", ["Multiple defaults", "One default export imported without braces", "Only functions", "CommonJS only"], 1, "`import x from './m.js'` gets the default export."),
]

Q["sql"] = [
("SELECT", 1, "Which keyword removes duplicate rows from results?", ["UNIQUE", "DISTINCT", "DIFFERENT", "GROUP"], 1, "SELECT DISTINCT."),
("Filtering with WHERE", 1, "How do you test for missing values?", ["= NULL", "IS NULL", "== NULL", "NULL()"], 1, "NULL is not equal to anything, including NULL."),
("Sorting", 1, "Default ORDER BY direction is...", ["DESC", "ASC", "Random", "Insertion order"], 1, "Ascending."),
("Aggregation", 1, "`COUNT(col)` counts...", ["All rows", "Non-NULL values in col", "Distinct values", "NULLs"], 1, "COUNT(*) counts rows; COUNT(col) skips NULLs."),
("GROUP BY and HAVING", 1, "HAVING filters...", ["Rows before grouping", "Groups after aggregation", "Joins", "Columns"], 1, "WHERE filters rows; HAVING filters groups."),
("JOINs", 2, "A LEFT JOIN returns...", ["Only matching rows", "All left rows plus matches (NULLs where none)", "All right rows", "A cross product"], 1, "Unmatched left rows get NULLs for right columns."),
("Subqueries", 2, "A correlated subquery...", ["Runs once", "References columns from the outer query", "Can't use WHERE", "Is always faster"], 1, "It's evaluated per outer row (logically)."),
("Common Table Expressions", 2, "A CTE is introduced with...", ["WITH", "TEMP", "DEFINE", "AS TABLE"], 0, "WITH name AS (...) SELECT ..."),
("Window Functions", 3, "How do window functions differ from GROUP BY aggregates?", ["They're slower", "They compute over a window without collapsing rows", "They need HAVING", "They only work on dates"], 1, "Each row keeps its identity; OVER defines the window."),
("Transactions and ACID", 3, "The 'I' in ACID stands for...", ["Integrity", "Isolation", "Indexing", "Idempotence"], 1, "Concurrent transactions shouldn't interfere."),
("Indexes", 3, "An index generally speeds up...", ["Writes", "Reads/filters on indexed columns", "Schema changes", "Backups"], 1, "At the cost of extra write work and storage."),
("Query Optimization", 3, "`EXPLAIN` shows...", ["Table contents", "The query execution plan", "Permissions", "Indexes to create"], 1, "Use it to spot full scans and bad joins."),
]

Q["dsa"] = [
("Complexity Analysis", 1, "Binary search on n sorted items is...", ["O(n)", "O(log n)", "O(1)", "O(n log n)"], 1, "The search space halves each step."),
("Arrays", 1, "Inserting at the front of a dynamic array costs...", ["O(1)", "O(n)", "O(log n)", "O(n^2)"], 1, "All elements shift."),
("Linked Lists", 1, "Which is O(1) in a singly linked list with a head pointer?", ["Access the k-th element", "Insert at head", "Search", "Insert at tail without a tail pointer"], 1, "Only the head pointer changes."),
("Stacks", 1, "Which structure checks balanced parentheses naturally?", ["Queue", "Stack", "Heap", "Set"], 1, "Push openers, pop on closers."),
("Recursion", 1, "What prevents infinite recursion?", ["A loop", "A base case", "A global", "Memoization"], 1, "The base case stops the recursion."),
("Hashing", 2, "Two-sum in O(n) typically uses...", ["Sorting", "A hash map of seen values", "Recursion", "A heap"], 1, "Look up target - x as you scan."),
("Sorting Algorithms", 2, "Merge sort's worst-case time is...", ["O(n^2)", "O(n log n)", "O(n)", "O(log n)"], 1, "It always splits evenly."),
("Trees", 2, "BFS on a tree uses a...", ["Stack", "Queue", "Heap", "Hash map"], 1, "Level by level."),
("Heaps and Priority Queues", 2, "Finding the k largest of n items with a min-heap of size k is...", ["O(n log k)", "O(n^2)", "O(k)", "O(log n)"], 0, "Each of n items costs O(log k)."),
("Dynamic Programming", 3, "DP applies when a problem has...", ["No recursion", "Overlapping subproblems and optimal substructure", "Only sorted input", "Graphs"], 1, "Cache subproblem results."),
("Shortest Paths", 3, "Dijkstra's algorithm fails with...", ["Cycles", "Negative edge weights", "Undirected graphs", "Many nodes"], 1, "Use Bellman-Ford for negative weights."),
]

Q["machine-learning"] = [
("What is Machine Learning", 1, "Predicting house prices from labeled examples is...", ["Unsupervised learning", "Supervised regression", "Clustering", "Reinforcement learning"], 1, "Labels are continuous values."),
("Data Preprocessing", 1, "Why scale features for gradient descent?", ["Required by Python", "So features on different scales don't dominate/slow convergence", "To remove outliers", "To add features"], 1, "Similar scales give better-conditioned optimization."),
("Train/Test Split and Evaluation", 1, "High training accuracy but low test accuracy suggests...", ["Underfitting", "Overfitting", "Perfect model", "Data leakage fixed"], 1, "The model memorized the training data."),
("Classification Metrics", 2, "In fraud detection with rare positives, accuracy is misleading because...", ["It's always low", "Predicting all negatives already scores high", "It ignores true negatives", "It needs probabilities"], 1, "Use precision, recall, F1 or PR-AUC."),
("Ensembles and Random Forests", 2, "Random forests reduce variance by...", ["Boosting errors", "Averaging many decorrelated trees", "Pruning a single tree", "Using linear models"], 1, "Bagging + random feature subsets."),
("Cross-Validation and Tuning", 2, "Fitting a scaler on the full dataset before splitting causes...", ["Faster training", "Data leakage", "Underfitting", "Nothing"], 1, "Test-set statistics leak into training."),
("Neural Networks", 3, "Backpropagation computes...", ["Predictions", "Gradients of the loss w.r.t. weights via the chain rule", "Batch sizes", "Activations only"], 1, "Gradients then drive the optimizer."),
("Sequence Models and Transformers", 3, "Self-attention lets each token...", ["See only the previous token", "Weigh every other token when building its representation", "Skip training", "Avoid embeddings"], 1, "That's the core transformer operation."),
]

Q["c"] = [
("Variables and Data Types", 1, "`sizeof(char)` is always...", ["1", "2", "4", "Platform dependent"], 0, "By definition in the C standard."),
("Strings in C", 1, "C strings end with...", ["\\n", "A null terminator '\\0'", "EOF", "Their length"], 1, "Functions like strlen scan for '\\0'."),
("Pointers", 2, "What does `&x` give?", ["x's value", "x's address", "A copy", "x squared"], 1, "The address-of operator."),
("Dynamic Memory", 2, "Every successful malloc should be paired with...", ["delete", "free", "release", "Nothing"], 1, "Otherwise memory leaks."),
("Structs", 2, "Given `struct P *p`, access field x with...", ["p.x", "p->x", "*p.x", "p::x"], 1, "-> dereferences and accesses."),
("Undefined Behavior", 3, "Reading past the end of an array is...", ["Always a crash", "Undefined behavior", "Returns 0", "A compile error"], 1, "Anything can happen."),
]

Q["go"] = [
("Variables and Types", 1, "The zero value of an int in Go is...", ["nil", "0", "undefined", "random"], 1, "Every type has a zero value."),
("Control Flow", 1, "Go's only looping keyword is...", ["while", "for", "loop", "repeat"], 1, "for covers all loop forms."),
("Error Handling", 2, "Idiomatic Go signals failures by...", ["Exceptions", "Returning an error value", "Panicking always", "Global flags"], 1, "Check `if err != nil`."),
("Interfaces", 2, "A type implements an interface when...", ["It declares `implements`", "It has all the interface's methods", "It embeds it", "It's registered"], 1, "Implementation is implicit."),
("Channels", 2, "Sending on an unbuffered channel blocks until...", ["Forever", "A receiver is ready", "The buffer fills", "The goroutine exits"], 1, "Unbuffered channels synchronize sender and receiver."),
("Context", 3, "context.Context is mainly used for...", ["Logging", "Cancellation, deadlines and request-scoped values", "Dependency injection", "Configuration"], 1, "Propagate it through call chains."),
]

Q["rust"] = [
("Variables and Mutability", 1, "Variables in Rust are by default...", ["Mutable", "Immutable", "Global", "Static"], 1, "Use `mut` to allow mutation."),
("Ownership", 1, "After `let b = a;` where a is a String, a is...", ["Still usable", "Moved and no longer usable", "Copied", "Cloned"], 1, "String doesn't implement Copy."),
("Borrowing and References", 2, "At a given time you can have...", ["Many &mut", "One &mut or any number of &", "Only one &", "No references"], 1, "The borrow rules prevent data races."),
("Enums and Pattern Matching", 1, "Rust represents an optional value with...", ["null", "Option<T>", "Maybe", "undefined"], 1, "Some(T) or None."),
("Error Handling", 2, "The `?` operator...", ["Panics", "Returns early with the error if a Result is Err", "Ignores errors", "Unwraps Options only"], 1, "It propagates errors."),
("Fearless Concurrency", 3, "To share mutable state across threads you commonly use...", ["Rc<RefCell<T>>", "Arc<Mutex<T>>", "Box<T>", "&mut T"], 1, "Arc is thread-safe; Rc isn't Send."),
]
