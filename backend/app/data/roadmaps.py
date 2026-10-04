"""Roadmap curriculum.

Line format inside each level:   Title | prerequisites | concept; concept; concept
  * prerequisites empty  -> depends on the previous topic in the roadmap (linear)
  * prerequisites "^"    -> no prerequisites
  * otherwise            -> comma-separated topic titles from the same roadmap
Levels: Beginner (difficulty 1), Intermediate (2), Advanced (3), Projects (4).
"""

LEVEL_DIFFICULTY = {"Beginner": 1, "Intermediate": 2, "Advanced": 3, "Projects": 4}
LEVEL_MINUTES = {"Beginner": 35, "Intermediate": 50, "Advanced": 70, "Projects": 300}

ROADMAPS: dict[str, dict] = {
"python": dict(name="Python", category="Language",
  docs="https://docs.python.org/3/",
  description="General-purpose language known for readability; used in automation, web backends, data and AI.",
  levels={
"Beginner": """
Python Introduction | ^ | what Python is; interpreted execution; REPL; use cases
Installation and Environment | | installing Python; PATH; running scripts; editors and IDEs
Variables | | assignment; naming rules; dynamic typing; reassignment
Data Types | | int and float; str; bool; None; type() and conversion
Input/Output | | print(); input(); f-strings; formatting output
Operators | Data Types | arithmetic operators; comparison operators; logical operators; operator precedence
Conditions | Operators | if/elif/else; truthiness; nested conditions; conditional expressions
Loops | Conditions | for loops; while loops; range(); break and continue
Functions | Loops | def and return; parameters and arguments; default arguments; scope
Lists | Loops | indexing and slicing; list methods; iteration; list comprehensions
Tuples | Lists | immutability; packing and unpacking; tuples as records
Sets | Lists | uniqueness; set operations; membership testing
Dictionaries | Lists | key-value pairs; dict methods; iterating items; nested dicts
Strings | Loops | string methods; slicing strings; immutability of str; join and split
Basic Error Handling | Functions | try/except; common exceptions; reading tracebacks
Basic File Handling | Strings, Basic Error Handling | open(); read and write; with statement; file modes
""",
"Intermediate": """
Modules | Functions | import; standard library; __name__ == '__main__'; module search path
Packages | Modules | package layout; __init__.py; relative imports
OOP | Functions, Dictionaries | objects and state; methods; why OOP; self
Classes | OOP | __init__; instance vs class attributes; dunder methods; dataclasses
Inheritance | Classes | subclassing; super(); method overriding; MRO
Polymorphism | Inheritance | duck typing; method overriding; abstract base classes
Encapsulation | Classes | naming conventions; properties; information hiding
Exceptions | Basic Error Handling, Classes | custom exceptions; raise; finally; exception chaining
File Handling | Basic File Handling, Exceptions | pathlib; CSV files; binary files; encodings
Iterators | Classes, Loops | iteration protocol; __iter__ and __next__; StopIteration
Generators | Iterators, Functions | yield; lazy evaluation; generator expressions
Decorators | Functions, Generators | functions as objects; closures; wrapping functions; functools.wraps
Virtual Environments | Packages | venv; activating environments; isolation
pip | Virtual Environments | installing packages; requirements.txt; version pinning
Testing | Functions, Modules | unittest; pytest; assertions; test discovery
JSON | Dictionaries, File Handling | json.loads; json.dumps; serialization
APIs | JSON, pip | HTTP basics; requests library; status codes; REST
Databases | Dictionaries | relational model; tables and rows; SQL basics
SQLite | Databases, Modules | sqlite3 module; parameterized queries; transactions
Git/GitHub | ^ | commits; branches; pull requests; .gitignore
""",
"Advanced": """
Advanced OOP | Polymorphism, Encapsulation | metaclasses; descriptors; __slots__; mixins
Advanced Decorators | Decorators, Classes | decorators with arguments; class decorators; stacking decorators
Context Managers | Exceptions, Generators | __enter__/__exit__; contextlib; resource cleanup
Async Programming | Generators, APIs | async/await; event loop; asyncio.gather; coroutines
Concurrency | Async Programming | threads; GIL; race conditions; locks
Multiprocessing | Concurrency | processes; Pool; shared state; CPU-bound work
Performance Optimization | Generators, Testing | profiling; algorithmic complexity; caching; built-ins
Memory Management | Advanced OOP | reference counting; garbage collection; weak references
Design Patterns | Advanced OOP | factory; strategy; observer; dependency injection
Architecture | Design Patterns, Packages | layered architecture; separation of concerns; configuration
Advanced Testing | Testing, Advanced Decorators | fixtures; mocking; parametrization; coverage
Production Practices | Architecture, Advanced Testing | logging; type hints; linting; packaging and deployment
""",
"Projects": """
CLI Calculator | Functions, Basic Error Handling | argument parsing; operator dispatch; input validation
To-Do CLI | Basic File Handling, Dictionaries | persistence to file; CRUD commands; CLI UX
Expense Tracker | File Handling, Classes | CSV storage; categories; monthly reports
REST API | APIs, Testing | FastAPI or Flask; routes; validation; tests
Database Application | SQLite, Classes | schema design; CRUD layer; queries
Full-Stack Application | REST API, Database Application | frontend client; backend API; authentication
AI-powered Capstone Project | Full-Stack Application, Async Programming | LLM or ML integration; evaluation; deployment
""",
}),

"java": dict(name="Java", category="Language", docs="https://docs.oracle.com/en/java/",
  description="Statically typed, object-oriented language on the JVM; dominant in enterprise backends and Android.",
  levels={
"Beginner": """
Java Basics | ^ | JDK and JVM; javac and java; main method; project structure
Variables and Primitive Types | | int long double boolean char; declarations; type casting
Operators and Expressions | | arithmetic; relational; logical; ternary
Control Flow | | if/else; switch expressions; loops; break and continue
Methods | | method signatures; parameters; return types; overloading
Arrays | Control Flow | array declaration; indexing; enhanced for; multi-dimensional arrays
Strings and StringBuilder | Arrays | String immutability; common methods; StringBuilder; equals vs ==
""",
"Intermediate": """
Classes and Objects | Methods | fields; constructors; this; access modifiers
OOP Principles | Classes and Objects | encapsulation; inheritance; polymorphism; abstraction
Interfaces and Abstract Classes | OOP Principles | interface contracts; default methods; abstract classes
Exceptions | Classes and Objects | checked vs unchecked; try/catch/finally; try-with-resources; custom exceptions
Collections | Interfaces and Abstract Classes, Arrays | List; Set; Map; iteration
Generics | Collections | type parameters; bounded types; wildcards; type erasure
Lambdas and Functional Interfaces | Interfaces and Abstract Classes | lambda syntax; Function and Predicate; method references
Streams | Lambdas and Functional Interfaces, Collections | map filter reduce; collectors; lazy pipelines
File I/O and NIO | Exceptions | Files and Path; readers and writers; serialization
Build Tools | ^ | Maven; Gradle; dependencies; build lifecycle
Unit Testing with JUnit | Classes and Objects, Build Tools | JUnit 5; assertions; test lifecycle; Mockito basics
""",
"Advanced": """
Multithreading | Lambdas and Functional Interfaces | Thread and Runnable; ExecutorService; synchronization; volatile
Concurrency Utilities | Multithreading | CompletableFuture; locks; concurrent collections; atomic variables
JVM Internals | OOP Principles | class loading; bytecode; JIT compilation
Memory and Garbage Collection | JVM Internals | heap and stack; GC algorithms; memory leaks
JDBC and Databases | Exceptions, Build Tools | JDBC; prepared statements; connection pools
Spring Boot | Generics, Build Tools | dependency injection; auto-configuration; beans
REST APIs with Spring | Spring Boot | controllers; request mapping; validation; error handling
Spring Data JPA | REST APIs with Spring, JDBC and Databases | entities; repositories; relationships
Design Patterns in Java | Interfaces and Abstract Classes | builder; singleton; strategy; factory
""",
"Projects": """
Bank Account Simulator | Collections, Exceptions | account classes; transactions; validation
Library Management System | Streams, File I/O and NIO | domain model; search with streams; persistence
Concurrent Web Crawler | Concurrency Utilities | thread pools; queues; rate limiting
Spring REST Service | Spring Data JPA, Unit Testing with JUnit | CRUD API; persistence; integration tests
Microservice Capstone | Spring REST Service, Multithreading | service boundaries; Docker; observability
""",
}),

"c": dict(name="C", category="Language", docs="https://en.cppreference.com/w/c",
  description="Low-level systems language; the foundation of operating systems, embedded software and runtimes.",
  levels={
"Beginner": """
C Basics and Compilation | ^ | gcc; compile and link; main(); headers
Variables and Data Types | | int char float double; sizeof; signed vs unsigned
Operators | | arithmetic; bitwise operators; logical; precedence
Control Flow | | if/else; switch; for while do-while
Functions | | prototypes; pass by value; return values; recursion
Arrays | Control Flow | declaration; indexing; arrays and loops; bounds
Strings in C | Arrays | char arrays; null terminator; string.h functions
""",
"Intermediate": """
Pointers | Functions, Arrays | addresses; dereferencing; pointer arithmetic; NULL
Pointers and Arrays | Pointers | array decay; pointer iteration; passing arrays
Dynamic Memory | Pointers | malloc and free; calloc and realloc; memory leaks
Structs | Pointers | struct definition; arrow operator; nested structs
Unions and Enums | Structs | unions; enums; typedef
File I/O | Strings in C, Pointers | fopen; fprintf and fscanf; binary files
Preprocessor | ^ | #define; macros; include guards; conditional compilation
Multi-file Programs and Make | Preprocessor, Functions | header files; linking; Makefiles
""",
"Advanced": """
Function Pointers | Pointers | callbacks; dispatch tables; qsort
Linked Data Structures | Dynamic Memory, Structs | linked lists; stacks; queues
Bit Manipulation | Operators | masks; flags; shifts
Undefined Behavior | Dynamic Memory | UB categories; sanitizers; defensive coding
Debugging with GDB and Valgrind | Dynamic Memory | breakpoints; backtraces; leak detection
POSIX Systems Programming | File I/O, Multi-file Programs and Make | processes; fork and exec; signals
Threads with pthreads | POSIX Systems Programming | pthread_create; mutexes; condition variables
""",
"Projects": """
Student Records CLI | Structs, File I/O | struct arrays; file persistence; menus
Custom Dynamic Array Library | Dynamic Memory, Multi-file Programs and Make | growable arrays; API design; tests
Mini Shell | POSIX Systems Programming | parsing commands; fork/exec; pipes
Multithreaded File Processor | Threads with pthreads | work queues; synchronization; performance
""",
}),

"cpp": dict(name="C++", category="Language", docs="https://en.cppreference.com/w/cpp",
  description="High-performance multi-paradigm language used in games, finance, browsers and systems.",
  levels={
"Beginner": """
C++ Basics | ^ | compiling with g++; main(); iostream; namespaces
Variables and Types | | fundamental types; auto; const; initialization
Operators and Control Flow | | operators; if/switch; loops
Functions | | declarations; overloading; default arguments; pass by reference
Arrays and std::string | Operators and Control Flow | C arrays; std::string; std::array
Pointers | Functions | addresses; dereference; nullptr; pointer arithmetic
References | Pointers | lvalue references; const references; references vs pointers
""",
"Intermediate": """
Memory and the Heap | Pointers | new and delete; stack vs heap; dangling pointers
Classes and Objects | References | members; constructors; destructors; access control
RAII | Classes and Objects, Memory and the Heap | resource ownership; destructors cleanup; scope-bound resources
Operator Overloading | Classes and Objects | overloadable operators; friend functions; stream operators
Inheritance and Polymorphism | Classes and Objects | virtual functions; override; abstract classes; vtables
STL Containers | Arrays and std::string, Classes and Objects | vector; map; unordered_map; set
STL Algorithms and Iterators | STL Containers | iterators; sort; find_if; transform
Exceptions | Classes and Objects | throw and catch; exception safety; noexcept
Templates | STL Containers | function templates; class templates; template instantiation
""",
"Advanced": """
Smart Pointers | RAII | unique_ptr; shared_ptr; weak_ptr; make_unique
Modern C++ Features | Templates, STL Algorithms and Iterators | lambdas; structured bindings; std::optional; constexpr
Move Semantics | Smart Pointers | rvalue references; std::move; move constructors; rule of five
Advanced Templates | Templates, Modern C++ Features | variadic templates; SFINAE; concepts
Concurrency | Move Semantics | std::thread; mutex; atomic; std::async
Performance and Profiling | Move Semantics, STL Algorithms and Iterators | cache locality; profiling; avoiding copies
Build Systems with CMake | Classes and Objects | CMakeLists; targets; linking libraries
""",
"Projects": """
Inventory Manager | STL Containers, Classes and Objects | class design; containers; file persistence
Matrix Library | Operator Overloading, Templates | operator overloading; templates; tests
Text Adventure Engine | Inheritance and Polymorphism, Smart Pointers | polymorphic entities; ownership; game loop
Thread Pool | Concurrency | task queue; worker threads; futures
High-Performance Capstone | Performance and Profiling, Build Systems with CMake | benchmarking; optimization; CMake project
""",
}),

"javascript": dict(name="JavaScript", category="Language", docs="https://developer.mozilla.org/en-US/docs/Web/JavaScript",
  description="The language of the web; runs in browsers and on servers via Node.js.",
  levels={
"Beginner": """
JavaScript Basics | ^ | running JS; console; script tags; strict mode
Variables and Types | | let const var; primitives; typeof; type coercion
Operators and Conditionals | | === vs ==; logical operators; if/else; switch
Loops | | for; while; for...of; for...in
Functions | | declarations; expressions; arrow functions; parameters
Arrays | Loops | array methods; map filter reduce; spread
Objects | Arrays | object literals; property access; destructuring; JSON
DOM Manipulation | Objects, Functions | querySelector; events; creating elements
""",
"Intermediate": """
ES6+ Features | Objects | template literals; destructuring; spread and rest; optional chaining
Scope and Hoisting | Functions | block scope; hoisting; temporal dead zone
Closures | Scope and Hoisting | lexical scope; function factories; private state
this and Prototypes | Objects, Closures | this binding; prototype chain; call apply bind
Classes | this and Prototypes | class syntax; extends; getters and setters
Error Handling | Functions | try/catch; Error types; throwing errors
Promises | Closures, Error Handling | promise states; then/catch; Promise.all
Async/Await | Promises | async functions; await; error handling with async
Fetch and APIs | Async/Await, DOM Manipulation | fetch; JSON responses; REST calls
Modules | ES6+ Features | import/export; module scope; bundlers
""",
"Advanced": """
Event Loop | Async/Await | call stack; task queue; microtasks
Node.js Fundamentals | Modules, Event Loop | node runtime; npm; fs module; Express basics
Testing JavaScript | Modules | Jest or Vitest; assertions; mocking
TypeScript Introduction | Classes, Modules | static types; interfaces; tsc
React Fundamentals | Modules, DOM Manipulation | components; props and state; hooks
Performance and Memory | Event Loop, Closures | debouncing; memory leaks; profiling
Security Basics | Fetch and APIs | XSS; CSRF; CORS
""",
"Projects": """
Interactive To-Do App | DOM Manipulation, Arrays | DOM rendering; events; localStorage
Weather Dashboard | Fetch and APIs | API integration; async UI; error states
Express REST API | Node.js Fundamentals | routes; middleware; validation
React Single-Page App | React Fundamentals, Fetch and APIs | routing; state management; API data
Full-Stack JS Capstone | React Single-Page App, Express REST API | auth; database; deployment
""",
}),

"typescript": dict(name="TypeScript", category="Language", docs="https://www.typescriptlang.org/docs/",
  description="JavaScript with a static type system for safer large-scale applications.",
  levels={
"Beginner": """
TypeScript Setup | ^ | tsc; tsconfig.json; compiling to JS
Basic Types | | string number boolean; arrays; tuples; any vs unknown
Functions and Types | | parameter types; return types; optional parameters
Interfaces | | object shapes; optional properties; readonly
Type Aliases and Unions | Interfaces | type aliases; union types; literal types
Type Narrowing | Type Aliases and Unions | typeof guards; in operator; discriminated unions
""",
"Intermediate": """
Classes in TypeScript | Interfaces | access modifiers; implements; abstract classes
Generics | Functions and Types, Interfaces | generic functions; generic constraints; generic interfaces
Enums and Const Assertions | Type Aliases and Unions | enums; as const; literal inference
Modules and Declaration Files | TypeScript Setup | import/export types; .d.ts files; DefinitelyTyped
Utility Types | Generics | Partial; Pick and Omit; Record; ReturnType
Strict Mode | Type Narrowing | strictNullChecks; noImplicitAny; exhaustive checks
""",
"Advanced": """
Conditional Types | Utility Types | extends conditionals; infer; distributive types
Mapped Types | Utility Types | keyof; mapped modifiers; key remapping
Template Literal Types | Mapped Types | string manipulation types; typed routes
Type-safe APIs | Generics, Strict Mode | typed fetch; runtime validation with zod; shared types
TypeScript with React | Generics | typed props; typed hooks; event types
TypeScript with Node.js | Modules and Declaration Files | typed Express; ts-node; build pipeline
""",
"Projects": """
Typed Utility Library | Generics, Utility Types | generic helpers; declaration output; tests
Typed REST Client | Type-safe APIs | generated types; error handling; retries
Full-Stack TypeScript App | TypeScript with React, TypeScript with Node.js | shared types; API; UI
""",
}),

"go": dict(name="Go", category="Language", docs="https://go.dev/doc/",
  description="Simple, fast, compiled language designed for concurrency and cloud infrastructure.",
  levels={
"Beginner": """
Go Setup and Tooling | ^ | go run; go build; go mod init; gofmt
Variables and Types | | var and :=; basic types; zero values; constants
Control Flow | | if; for (the only loop); switch
Functions | | multiple return values; named returns; variadic functions
Arrays and Slices | Control Flow | arrays; slices; append; len and cap
Maps | Arrays and Slices | map literals; lookup with ok; iteration
Structs | Maps | struct types; methods; pointer receivers
""",
"Intermediate": """
Pointers in Go | Structs | & and *; pointer receivers; no pointer arithmetic
Interfaces | Structs | implicit implementation; empty interface; type assertions
Error Handling | Functions | error values; errors.Is and As; wrapping errors
Packages and Modules | Go Setup and Tooling | package layout; exported names; go.mod dependencies
Testing in Go | Packages and Modules | testing package; table-driven tests; benchmarks
Goroutines | Functions | go keyword; scheduler; WaitGroup
Channels | Goroutines | unbuffered and buffered; select; closing channels
""",
"Advanced": """
Concurrency Patterns | Channels | worker pools; fan-in fan-out; pipelines
Context | Concurrency Patterns | cancellation; deadlines; request scoping
Generics in Go | Interfaces | type parameters; constraints; generic functions
HTTP Servers | Interfaces, Error Handling | net/http; handlers; middleware; JSON encoding
Databases with Go | HTTP Servers | database/sql; drivers; prepared statements
Profiling and Performance | Testing in Go | pprof; escape analysis; allocations
""",
"Projects": """
CLI Task Manager | Structs, Error Handling | flags; JSON persistence; commands
Concurrent URL Checker | Concurrency Patterns | worker pools; timeouts; reporting
REST Microservice | HTTP Servers, Databases with Go, Testing in Go | routing; persistence; tests
Distributed Job Queue Capstone | Context, REST Microservice | queues; retries; graceful shutdown
""",
}),

"rust": dict(name="Rust", category="Language", docs="https://doc.rust-lang.org/book/",
  description="Memory-safe systems language with zero-cost abstractions and fearless concurrency.",
  levels={
"Beginner": """
Rust Setup and Cargo | ^ | rustup; cargo new; cargo run; crates
Variables and Mutability | | let; mut; shadowing; constants
Data Types | | scalar types; tuples; arrays; type inference
Functions and Control Flow | | fn; expressions vs statements; if; loop while for
Ownership | Functions and Control Flow | ownership rules; move semantics; drop
Borrowing and References | Ownership | & and &mut; borrow rules; slices
Structs | Borrowing and References | struct definitions; impl blocks; methods
Enums and Pattern Matching | Structs | enums; match; Option; if let
""",
"Intermediate": """
Error Handling | Enums and Pattern Matching | Result; ? operator; panic vs recoverable errors
Collections | Borrowing and References | Vec; String; HashMap
Traits | Structs | trait definitions; implementing traits; trait bounds
Generics | Traits | generic functions; generic structs; monomorphization
Lifetimes | Generics, Borrowing and References | lifetime annotations; elision; 'static
Modules and Crates | Rust Setup and Cargo | mod; pub; use; workspaces
Closures and Iterators | Traits | closures; Fn traits; iterator adapters
Testing in Rust | Modules and Crates | #[test]; integration tests; cargo test
""",
"Advanced": """
Smart Pointers | Lifetimes | Box; Rc; RefCell; interior mutability
Fearless Concurrency | Smart Pointers, Closures and Iterators | threads; Arc and Mutex; Send and Sync
Async Rust | Fearless Concurrency | futures; async/await; tokio runtime
Advanced Traits | Generics | associated types; trait objects; dyn
Macros | Advanced Traits | macro_rules!; derive macros
Unsafe Rust | Smart Pointers | raw pointers; unsafe blocks; FFI
""",
"Projects": """
Command-Line Grep Clone | Error Handling, Collections | args parsing; file reading; tests
Linked List and Data Structures | Smart Pointers | ownership in data structures; Rc and RefCell
Multithreaded Web Server | Fearless Concurrency | TCP listener; thread pool; graceful shutdown
Async API Capstone | Async Rust, Testing in Rust | axum or actix; database; deployment
""",
}),

"kotlin": dict(name="Kotlin", category="Language", docs="https://kotlinlang.org/docs/home.html",
  description="Concise, null-safe JVM language; the preferred language for Android.",
  levels={
"Beginner": """
Kotlin Basics | ^ | kotlinc; main function; REPL; IntelliJ
Variables and Types | | val vs var; type inference; basic types
Null Safety | Variables and Types | nullable types; safe call ?.; elvis operator; !!
Control Flow | | if as expression; when; ranges; loops
Functions | | named arguments; default values; single-expression functions
Collections | Control Flow | List Set Map; mutable vs read-only; collection operations
""",
"Intermediate": """
Classes and Objects | Functions | primary constructors; properties; init blocks
Data Classes | Classes and Objects | copy; equals and hashCode; destructuring
Inheritance and Interfaces | Classes and Objects | open classes; override; interfaces
Sealed Classes | Inheritance and Interfaces | sealed hierarchies; exhaustive when
Lambdas and Higher-Order Functions | Functions, Collections | lambda syntax; it; function types
Extension Functions | Lambdas and Higher-Order Functions | extension functions; scope functions let apply also
Exceptions | Classes and Objects | try as expression; runCatching
Gradle for Kotlin | ^ | build.gradle.kts; dependencies; tasks
""",
"Advanced": """
Coroutines | Lambdas and Higher-Order Functions | suspend functions; launch and async; scopes
Flows | Coroutines | Flow builders; operators; StateFlow
Generics and Variance | Classes and Objects | in and out; reified types
DSLs in Kotlin | Extension Functions | lambdas with receivers; builders
Android Fundamentals | Coroutines, Gradle for Kotlin | activities; Jetpack Compose basics; ViewModel
Ktor Backend | Coroutines, Gradle for Kotlin | routing; serialization; testing
""",
"Projects": """
Notes CLI | Data Classes, Collections | CRUD; file persistence
Android Habit Tracker | Android Fundamentals, Flows | Compose UI; state; Room database
Ktor REST API Capstone | Ktor Backend, Sealed Classes | endpoints; auth; tests
""",
}),

"csharp": dict(name="C#", category="Language", docs="https://learn.microsoft.com/dotnet/csharp/",
  description="Modern object-oriented language on .NET for web, desktop, cloud and games (Unity).",
  levels={
"Beginner": """
C# and .NET Setup | ^ | dotnet CLI; project files; Main and top-level statements
Variables and Types | | value types; reference types; var; string interpolation
Control Flow | | if; switch expressions; loops
Methods | | parameters; ref and out; overloading; optional parameters
Arrays and Lists | Control Flow | arrays; List<T>; foreach
Strings | Arrays and Lists | string methods; StringBuilder; immutability
""",
"Intermediate": """
Classes and Objects | Methods | properties; constructors; access modifiers
Inheritance and Interfaces | Classes and Objects | base and derived; virtual and override; interfaces
Structs and Records | Classes and Objects | value semantics; records; with-expressions
Exceptions | Classes and Objects | try/catch/finally; custom exceptions; using statement
Generics | Arrays and Lists | generic methods; constraints; generic collections
Delegates and Events | Methods | delegates; Func and Action; events
LINQ | Generics, Delegates and Events | query syntax; method syntax; deferred execution
Unit Testing with xUnit | Classes and Objects | xUnit; assertions; test projects
""",
"Advanced": """
Async and Await | Delegates and Events | Task; async methods; cancellation tokens
Dependency Injection | Inheritance and Interfaces | service lifetimes; IServiceCollection
ASP.NET Core Web APIs | Dependency Injection, Async and Await | controllers; minimal APIs; middleware
Entity Framework Core | ASP.NET Core Web APIs, LINQ | DbContext; migrations; relationships
Memory and Performance | Structs and Records | GC; Span<T>; allocations
Pattern Matching | Structs and Records | type patterns; property patterns; switch expressions
""",
"Projects": """
Console Quiz Game | Classes and Objects, Arrays and Lists | game loop; scoring; file persistence
Inventory Web API | ASP.NET Core Web APIs, Entity Framework Core | CRUD; validation; migrations
Full-Stack .NET Capstone | Inventory Web API, Unit Testing with xUnit | auth; frontend; deployment
""",
}),

"sql": dict(name="SQL", category="Data", docs="https://www.postgresql.org/docs/current/sql.html",
  description="The language of relational databases: querying, aggregating and modeling data.",
  levels={
"Beginner": """
SQL Basics and Relational Model | ^ | tables rows columns; primary keys; SQL dialects
SELECT | | selecting columns; aliases; DISTINCT; LIMIT
Filtering with WHERE | | comparison operators; AND OR NOT; IN BETWEEN LIKE; NULL handling
Sorting | Filtering with WHERE | ORDER BY; ascending and descending; multiple sort keys
Aggregation | Filtering with WHERE | COUNT SUM AVG MIN MAX; aggregate over table
GROUP BY and HAVING | Aggregation | grouping; HAVING vs WHERE; grouped aggregates
""",
"Intermediate": """
JOINs | GROUP BY and HAVING | INNER JOIN; LEFT JOIN; join conditions; self joins
Subqueries | JOINs | scalar subqueries; IN subqueries; correlated subqueries
Data Modification | SELECT | INSERT; UPDATE; DELETE; UPSERT
Schema Design and DDL | SQL Basics and Relational Model | CREATE TABLE; data types; constraints; foreign keys
Normalization | Schema Design and DDL | 1NF 2NF 3NF; redundancy; denormalization trade-offs
Common Table Expressions | Subqueries | WITH clauses; readability; recursive CTEs
Set Operations and CASE | Subqueries | UNION; INTERSECT; CASE expressions
""",
"Advanced": """
Window Functions | Common Table Expressions, GROUP BY and HAVING | OVER; PARTITION BY; ROW_NUMBER RANK; running totals
Transactions and ACID | Data Modification | BEGIN COMMIT ROLLBACK; isolation levels; locking
Indexes | Schema Design and DDL, JOINs | B-tree indexes; composite indexes; index selectivity
Query Optimization | Indexes | EXPLAIN plans; avoiding full scans; query rewriting
Views and Stored Procedures | Common Table Expressions | views; materialized views; procedures and functions
Analytics SQL Patterns | Window Functions | cohorts; funnels; retention queries
""",
"Projects": """
Library Database Design | Normalization, JOINs | ER model; schema; seed data
Sales Analytics Report | Window Functions, Common Table Expressions | KPIs; ranking; time series
E-commerce Database Capstone | Query Optimization, Transactions and ACID | schema; indexing; transactional orders
""",
}),

"html-css": dict(name="HTML/CSS", category="Web", docs="https://developer.mozilla.org/en-US/docs/Web/HTML",
  description="The structure and styling layers of every web page.",
  levels={
"Beginner": """
HTML Document Structure | ^ | doctype; head and body; elements and attributes
Text and Links | | headings; paragraphs; anchors; lists
Images and Media | Text and Links | img; alt text; audio and video
Forms | Text and Links | inputs; labels; validation attributes
CSS Basics | HTML Document Structure | selectors; properties; cascade; specificity
Box Model | CSS Basics | margin; padding; border; box-sizing
""",
"Intermediate": """
Semantic HTML | Forms | header main nav article; landmarks; document outline
Flexbox | Box Model | flex container; axes; alignment; wrapping
CSS Grid | Flexbox | grid templates; areas; auto-fit and minmax
Responsive Design | CSS Grid | media queries; mobile-first; fluid units
Typography and Color | CSS Basics | font stacks; line-height; color contrast
Accessibility | Semantic HTML | ARIA basics; keyboard focus; screen readers
""",
"Advanced": """
CSS Custom Properties | Responsive Design | variables; theming; dark mode
Animations and Transitions | CSS Custom Properties | transitions; keyframes; reduced motion
CSS Architecture | CSS Custom Properties | BEM; utility-first CSS; Tailwind
Performance and Rendering | Animations and Transitions | critical CSS; layout thrash; paint
""",
"Projects": """
Personal Portfolio Page | Responsive Design, Semantic HTML | layout; responsive images; deployment
Landing Page Clone | CSS Grid, Typography and Color | pixel-careful layout; components
Accessible Component Library | Accessibility, CSS Architecture | buttons; modals; forms; docs
""",
}),

"react": dict(name="React", category="Web", docs="https://react.dev/learn",
  description="Component-based UI library for building interactive web applications.",
  levels={
"Beginner": """
React Setup and JSX | ^ | Vite; JSX syntax; rendering; components
Components and Props | | function components; props; composition
State with useState | Components and Props | state updates; re-rendering; lifting state
Events and Forms | State with useState | event handlers; controlled inputs; form submit
Lists and Keys | Components and Props | rendering arrays; keys; conditional rendering
""",
"Intermediate": """
useEffect and Side Effects | State with useState | effect dependencies; cleanup; data fetching
Context API | Components and Props | createContext; providers; avoiding prop drilling
React Router | Components and Props | routes; params; nested layouts
Custom Hooks | useEffect and Side Effects | extracting logic; hook rules
Data Fetching Patterns | useEffect and Side Effects | loading and error states; React Query
Styling in React | React Setup and JSX | CSS modules; Tailwind; component styling
""",
"Advanced": """
Performance Optimization | Custom Hooks | memo; useMemo and useCallback; profiling
State Management at Scale | Context API | reducers; Redux Toolkit or Zustand
Testing React | Custom Hooks | React Testing Library; user events; mocking fetch
TypeScript with React | Components and Props | typed props; typed hooks
Server Rendering and Next.js | React Router, Data Fetching Patterns | SSR; server components; routing
""",
"Projects": """
Movie Search App | Data Fetching Patterns | API search; debouncing; results UI
Kanban Board | State Management at Scale | drag and drop; persistence
Full-Stack React Capstone | Server Rendering and Next.js, Testing React | auth; database; deployment
""",
}),

"nodejs": dict(name="Node.js", category="Web", docs="https://nodejs.org/docs/latest/api/",
  description="JavaScript runtime for servers, CLIs and tooling.",
  levels={
"Beginner": """
Node.js Runtime | ^ | V8; node command; REPL; global objects
Modules and npm | | CommonJS vs ESM; npm init; package.json; scripts
File System | Modules and npm | fs promises; paths; reading and writing files
Events and Streams | File System | EventEmitter; readable and writable streams; pipes
HTTP Module | Events and Streams | createServer; requests and responses
""",
"Intermediate": """
Express Fundamentals | HTTP Module | routing; middleware; request parsing
REST API Design | Express Fundamentals | resources; status codes; validation
Databases with Node | REST API Design | PostgreSQL or MongoDB; ORMs; migrations
Authentication | REST API Design | sessions; JWT; password hashing
Error Handling and Logging | Express Fundamentals | error middleware; structured logs
Testing Node Apps | Express Fundamentals | Jest or Vitest; supertest
""",
"Advanced": """
Event Loop Deep Dive | Events and Streams | phases; microtasks; blocking the loop
Worker Threads and Clustering | Event Loop Deep Dive | worker_threads; cluster; CPU work
Caching and Performance | Databases with Node | Redis; caching strategies; profiling
Security | Authentication | OWASP risks; rate limiting; helmet
Deployment and Docker | Testing Node Apps | Dockerfiles; environment config; CI
""",
"Projects": """
CLI File Organizer | File System | argument parsing; file operations
URL Shortener API | Databases with Node, Authentication | persistence; redirects; analytics
Real-time Chat Capstone | Security, Worker Threads and Clustering | WebSockets; auth; scaling
""",
}),

"dsa": dict(name="Data Structures & Algorithms", category="Computer Science", docs="https://www.geeksforgeeks.org/data-structures/",
  description="Core problem-solving toolkit for interviews, competitive programming and efficient software.",
  levels={
"Beginner": """
Complexity Analysis | ^ | Big-O; time vs space; best/worst/average case
Arrays | Complexity Analysis | traversal; insertion and deletion cost; two pointers
Strings | Arrays | string traversal; palindromes; frequency counting
Recursion | Complexity Analysis | base case; call stack; recursion trees
Linked Lists | Arrays | singly linked; doubly linked; reversal; fast and slow pointers
Stacks | Linked Lists | LIFO; push and pop; balanced parentheses
Queues | Linked Lists | FIFO; circular queue; deque
""",
"Intermediate": """
Hashing | Arrays | hash maps; collisions; frequency maps
Sorting Algorithms | Recursion, Arrays | merge sort; quick sort; stability
Binary Search | Sorting Algorithms | sorted search; search on answer; boundaries
Sliding Window | Hashing | fixed window; variable window; subarray problems
Trees | Recursion, Queues | binary trees; traversals; height and depth
Binary Search Trees | Trees, Binary Search | insert and search; BST property; deletion
Heaps and Priority Queues | Trees | heapify; top-k problems; heap sort
""",
"Advanced": """
Graphs Basics | Trees, Hashing | adjacency list; BFS; DFS
Shortest Paths | Graphs Basics, Heaps and Priority Queues | Dijkstra; Bellman-Ford; 0-1 BFS
Topological Sort | Graphs Basics | DAGs; Kahn's algorithm; dependency ordering
Union-Find | Graphs Basics | disjoint sets; path compression; union by rank
Dynamic Programming | Recursion, Hashing | memoization; tabulation; state design
Advanced DP | Dynamic Programming | knapsack; LIS; DP on trees
Tries | Trees, Strings | prefix trees; autocomplete
Greedy Algorithms | Sorting Algorithms | exchange argument; interval scheduling
Backtracking | Recursion | permutations; subsets; pruning
""",
"Projects": """
Implement a Data Structures Library | Heaps and Priority Queues, Binary Search Trees | APIs; tests; complexity docs
Route Planner | Shortest Paths | graph modeling; Dijkstra; visualization
Interview Prep Capstone | Advanced DP, Backtracking, Union-Find | 50 mixed problems; timed practice; review log
""",
}),

"machine-learning": dict(name="Machine Learning", category="AI", docs="https://scikit-learn.org/stable/user_guide.html",
  description="Building models that learn patterns from data to make predictions.",
  levels={
"Beginner": """
What is Machine Learning | ^ | supervised vs unsupervised; features and labels; ML workflow
Python for ML | | NumPy arrays; pandas DataFrames; plotting basics
Math Foundations | ^ | vectors and matrices; derivatives; probability basics
Data Preprocessing | Python for ML | missing values; scaling; encoding categoricals
Linear Regression | Math Foundations, Data Preprocessing | least squares; loss functions; gradient descent
Train/Test Split and Evaluation | Linear Regression | train/test split; MSE; overfitting
""",
"Intermediate": """
Logistic Regression | Linear Regression | sigmoid; decision boundary; log loss
Classification Metrics | Logistic Regression | accuracy; precision and recall; F1; confusion matrix
Decision Trees | Train/Test Split and Evaluation | splits; Gini and entropy; depth control
Ensembles and Random Forests | Decision Trees | bagging; random forests; feature importance
Gradient Boosting | Ensembles and Random Forests | boosting; XGBoost; learning rate
Cross-Validation and Tuning | Classification Metrics | k-fold CV; grid search; data leakage
Clustering | Data Preprocessing | k-means; choosing k; hierarchical clustering
Dimensionality Reduction | Math Foundations | PCA; explained variance; t-SNE
""",
"Advanced": """
Neural Networks | Logistic Regression, Math Foundations | perceptrons; activation functions; backpropagation
Deep Learning with PyTorch | Neural Networks | tensors; autograd; training loops
CNNs for Vision | Deep Learning with PyTorch | convolutions; pooling; transfer learning
Sequence Models and Transformers | Deep Learning with PyTorch | RNNs; attention; transformers
NLP and Embeddings | Sequence Models and Transformers | tokenization; embeddings; fine-tuning
Model Deployment and MLOps | Cross-Validation and Tuning | serving models; monitoring; versioning
Responsible AI | Classification Metrics | bias and fairness; explainability; evaluation
""",
"Projects": """
House Price Predictor | Cross-Validation and Tuning | regression pipeline; feature engineering
Spam Classifier | Classification Metrics, NLP and Embeddings | text features; evaluation
Image Classifier | CNNs for Vision | transfer learning; augmentation
End-to-End ML Capstone | Model Deployment and MLOps, Responsible AI | data pipeline; model API; monitoring
""",
}),

"data-science": dict(name="Data Science", category="AI", docs="https://pandas.pydata.org/docs/",
  description="Turning raw data into insight through analysis, statistics and visualization.",
  levels={
"Beginner": """
Data Science Workflow | ^ | asking questions; data lifecycle; notebooks
Python and Jupyter | | Jupyter; Python refresher; libraries
NumPy | Python and Jupyter | arrays; vectorization; broadcasting
pandas Basics | NumPy | Series and DataFrame; selecting data; reading CSV
Descriptive Statistics | ^ | mean median mode; variance; distributions
""",
"Intermediate": """
Data Cleaning | pandas Basics | missing data; duplicates; type fixes
Data Wrangling | Data Cleaning | groupby; merge and join; pivot tables
Data Visualization | pandas Basics | matplotlib; seaborn; choosing charts
Exploratory Data Analysis | Data Visualization, Descriptive Statistics | univariate analysis; correlations; outliers
Probability and Distributions | Descriptive Statistics | probability rules; normal distribution; sampling
SQL for Data Science | pandas Basics | querying; joins; pandas read_sql
""",
"Advanced": """
Hypothesis Testing | Probability and Distributions | t-tests; p-values; confidence intervals
A/B Testing | Hypothesis Testing | experiment design; sample size; pitfalls
Regression Analysis | Exploratory Data Analysis | linear models; interpreting coefficients; residuals
Time Series Analysis | Data Wrangling | trends; seasonality; forecasting basics
Machine Learning for Analysts | Regression Analysis | scikit-learn; classification; model evaluation
Data Storytelling | Data Visualization | narrative; dashboards; stakeholder communication
""",
"Projects": """
Exploratory Analysis Report | Exploratory Data Analysis | cleaning; EDA; findings write-up
A/B Test Analysis | A/B Testing | experiment analysis; recommendation
Data Science Capstone | Machine Learning for Analysts, Data Storytelling | end-to-end analysis; model; dashboard
""",
}),
}

# Keyword map used for goal relevance in the recommender.
GOAL_KEYWORDS = {
    "placement": {"interview", "arrays", "linked", "trees", "graphs", "dynamic", "sorting", "complexity",
                  "oop", "classes", "collections", "stl", "recursion", "hashing", "sql", "join", "search"},
    "job_ready": {"testing", "git", "api", "rest", "databases", "production", "deployment", "docker",
                  "spring", "express", "architecture", "design patterns", "security"},
    "web_development": {"dom", "html", "css", "react", "api", "rest", "http", "express", "node",
                        "fetch", "json", "responsive", "routing"},
    "data_science": {"pandas", "numpy", "statistics", "sql", "visualization", "data", "json",
                     "regression", "analysis", "aggregation", "window"},
    "fundamentals": {"variables", "types", "conditions", "loops", "functions", "control flow",
                     "arrays", "strings", "basics", "operators", "memory", "pointers"},
    "project_building": {"project", "capstone", "api", "application", "cli", "testing", "git", "deployment"},
}

GOALS = list(GOAL_KEYWORDS)
INTERESTS = ["web", "data", "ai", "games", "systems", "mobile", "automation", "security", "cloud"]
INTEREST_KEYWORDS = {
    "web": {"web", "http", "api", "rest", "dom", "react", "express", "html", "css", "fetch", "server"},
    "data": {"data", "sql", "pandas", "json", "csv", "database", "analytics", "statistics", "aggregation"},
    "ai": {"ml", "machine", "neural", "model", "ai", "nlp", "llm", "regression", "classification"},
    "games": {"game", "graphics", "performance", "loop", "matrix", "adventure"},
    "systems": {"memory", "pointers", "concurrency", "threads", "performance", "jvm", "posix", "unsafe"},
    "mobile": {"android", "kotlin", "compose", "mobile"},
    "automation": {"cli", "file", "scripts", "automation", "os", "processor"},
    "security": {"security", "auth", "authentication", "xss", "csrf", "unsafe"},
    "cloud": {"docker", "deployment", "microservice", "cloud", "distributed", "mlops"},
}
