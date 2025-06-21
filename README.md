# Nyunda Interpreter

> An educational interpreter for a custom, Sundanese-inspired programming language, built from scratch in Python to demonstrate core compiler and optimization principles using well known algorithm.

---

## Table of Contents

- [About This Project](#about-this-project)
- [Language at a Glance](#language-at-a-glance)
- [Core Algorithms](#core-algorithms)
  - [1. Regex-Based Lexer](#1-regex-based-lexer)
  - [2. Recursive Descent Parser](#2-recursive-descent-parser)
  - [3. Greedy Best-First Search Optimizer](#3-greedy-best-first-search-optimizer)
  - [4. Dynamic Programming Evaluator](#4-dynamic-programming-evaluator)
- [How to Run](#how-to-run)
- [Usage & Flags](#usage--flags)

---

## About This Project <a name="about-this-project"></a>
<div align="right">(<a href="#table-of-contents">back to top</a>)</div>

The Nyunda Interpreter is a demonstration of fundamental language processing techniques. It was built as a practical exercise in applying algorithmic strategies to a real-world problem: creating a simple programming language.

The interpreter processes code in a four-stage pipeline:

1.  **Lexical Analysis**: A regex-based lexer scans the source code and converts it into a stream of tokens (e.g., `KEYWORD`, `IDENTIFIER`, `NUMBER`).
2.  **Parsing**: A recursive descent parser consumes the tokens to build an Abstract Syntax Tree (AST), a tree-like representation of the code's structure.
3.  **Optimization**: A **Greedy Best-First Search** algorithm traverses the AST, applying a set of rules to simplify expressions and reduce their calculated execution cost. This idea heavily inspired by Just-in-time (JIT) compilation.
4.  **Evaluation**: The final, optimized AST is walked by an interpreter, which uses **Dynamic Programming** (memoization) to evaluate expressions, avoiding redundant calculations.

The entire project is self-contained and written in Python, with a focus on clear implementation of each algorithmic component.

---

## Language at a Glance <a name="language-at-a-glance"></a>
<div align="right">(<a href="#table-of-contents">back to top</a>)</div>

The language uses Sundanese keywords for basic control flow and operations.

### Features
* **Variables**: Assign values using `=`.
* **Arithmetic**: `+`, `-`, `*`, `/`, `%`, `**`.
* **Comparisons**: `==`, `!=`, `>`, `<`, `>=`, `<=`.
* **Conditionals**: `upami` (if) and `sanes` (else).
* **Loops**: `bari` (while).
* **Output**: `cetak()` (print).

### Example: `factorial.nyunda`

```

# Ngitung faktorial tina hiji wilangan

# (Calculates the factorial of a number)

n = 7
hasil = 1
counter = 1

bari counter \<= n {
hasil = hasil \* counter
counter = counter + 1
}

# Kaluaran kedahna 5040

# (Output should be 5040)

cetak(hasil)

# Conto optimasi: `hasil * 1` bakal dioptimalkeun

# (Optimization example: `hasil * 1` will be optimized)

optimasi = hasil \* 1 + 0
cetak(optimasi)

````

---

## Core Algorithms <a name="core-algorithms"></a>
<div align="right">(<a href="#table-of-contents">back to top</a>)</div>

This project is built upon several key algorithmic techniques that work together to interpret code efficiently.

| Component | Algorithm / Technique | Purpose |
| :--- | :--- | :--- |
| **Lexer** | Regular Expressions | Tokenizes source code into a structured format. |
| **Parser** | Recursive Descent | Builds a structural representation (AST) of the code. |
| **Optimizer** | Greedy Best-First Search | Traverses the AST to find and apply cost-reducing simplifications. |
| **Evaluator** | Dynamic Programming | Evaluates expressions using memoization to prevent re-computation. |

### 1. Regex-Based Lexer
The lexer uses a prioritized list of compiled regular expressions to match and categorize segments of the source code. This approach is efficient and easily extensible for adding new keywords or symbols. It systematically converts plain text into a stream of `Token` objects that the parser can understand.

### 2. Recursive Descent Parser
The parser uses a set of mutually recursive functions to process the token stream. Each function corresponds to a specific part of the language's grammar (e.g., `parse_statement`, `parse_expression`). This top-down approach naturally handles operator precedence and constructs the Abstract Syntax Tree (AST) that represents the code's hierarchical structure.

### 3. Greedy Best-First Search Optimizer
Before execution, the AST is passed to an optimizer that attempts to reduce its computational cost. It uses a Greedy Best-First Search algorithm where:
- **State**: A specific version of the AST.
- **Cost**: A heuristic value calculated for each AST node based on its operation type (e.g., multiplication is more "expensive" than addition).
- **Goal**: To find an AST with the lowest total cost.

The search explores transformations such as:
- **Constant Folding**: `2 + 3` → `5`
- **Strength Reduction**: `x ** 2` → `x * x`
- **Algebraic Simplification**: `x * 1` → `x`, `y + 0` → `y`

### 4. Dynamic Programming Evaluator
The final, optimized AST is executed by an interpreter. When evaluating expressions, it uses a Dynamic Programming technique called **memoization**.
- A unique key is generated for each sub-expression based on its structure and the current values of its variables.
- When an expression is calculated, its result is stored in a cache (`memo_table`) with its corresponding key.
- If the same expression is encountered again under the same variable state, its result is retrieved from the cache instantly instead of being re-calculated. This provides a significant speed-up for code with repetitive computations.

---

## How to Run <a name="how-to-run"></a>
<div align="right">(<a href="#table-of-contents">back to top</a>)</div>

### Requirements
- Python 3.9+

### Installation & Execution
1.  Clone this repository:
    ```bash
    git clone https://github.com/l0stplains/Nyunda.git
    ```
2.  Navigate to the project directory:
    ```bash
    cd nyunda
    ```
3.  The project includes simple execution scripts. Make them executable (on Linux/macOS):
    ```bash
    chmod +x run.sh
    ```
4.  Run a Nyunda script file using the provided scripts:

    **On Linux/macOS:**
    ```bash
    ./run.sh examples/factorial.nyunda
    ```

    **On Windows:**
    ```bat
    run.bat examples\factorial.nyunda
    ```

---

## Usage & Flags <a name="usage--flags"></a>
<div align="right">(<a href="#table-of-contents">back to top</a>)</div>

The interpreter can be configured with command-line flags to control its behavior and reporting.

### Default Behavior
Running a script without any flags will execute the code and print only the output from the `cetak()` commands.
```bash
./run.sh examples/fibonacci.nyunda
````

### Command-Line Flags

You can append these flags after the file path to change how the interpreter runs.

| Flag | Alias | Description |
| :--- | :--- | :--- |
| `--verbose` | `-v` | Enables a detailed, step-by-step report of the entire interpretation pipeline, including final performance statistics for the optimization and evaluation algorithms. |
| `--no-greedy`| | Disables the Greedy Best-First Search optimization pass. The AST will be executed as-is. |
| `--no-dp` | | Disables the Dynamic Programming (memoization) evaluator. All expressions will be re-calculated every time they are encountered. |

### Examples with Flags

  - **Get a full performance report:**

    ```bash
    ./run.sh examples/factorial.nyunda --verbose
    ```

  - **Compare performance without DP:**

    ```bash
    ./run.sh examples/factorial.nyunda --verbose --no-dp
    ```

  - **Run with all optimizations disabled:**

    ```bash
    ./run.sh examples/factorial.nyunda --verbose --no-greedy --no-dp
    ```
