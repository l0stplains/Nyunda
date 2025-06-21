# main.py
"""
The main entry point for the Nyunda interpreter.

This script can be run in two ways:
1. With a file path argument: It will execute the specified .nyunda file.
   Example: python main.py examples/factorial.nyunda

2. Without arguments: It will run a comprehensive internal demo of all
   the interpreter's algorithmic features.

This script supports flags to control execution behavior:
  --verbose       : Show detailed execution analysis.
  --no-greedy     : Disable Greedy Best-First Search optimization.
  --no-dp         : Disable Dynamic Programming for evaluation.
"""
import sys
import os
import argparse
from src import NyundaLexer, NyundaParser, GreedyBestFirstOptimizer, NyundaInterpreter

def run_file(filepath: str, verbose: bool, use_greedy: bool, use_dp: bool):
    """Lexes, parses, optimizes, and interprets a .nyunda file based on flags."""
    if not os.path.exists(filepath):
        print(f"Error: File not found at '{filepath}'")
        sys.exit(1)
        
    if verbose:
        print(f"--- Running Nyunda file: {filepath} ---")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    # Instantiate core components based on flags
    lexer = NyundaLexer()
    parser = NyundaParser()
    interpreter = NyundaInterpreter(use_dp=use_dp)
    
    # Pipeline
    
    # 1. Tokenization
    if verbose: print("Step 1: Tokenizing source code...")
    tokens = lexer.tokenize(code)

    # 2. Parsing
    if verbose: print("Step 2: Parsing tokens to generate initial AST...")
    ast = parser.parse(tokens)
    if verbose: print(f"         Initial AST Cost: {ast.cost}")

    # 3. Optimization (Conditional)
    optimized_ast = ast
    optimizer = None
    if use_greedy:
        optimizer = GreedyBestFirstOptimizer()
        if verbose: print("Step 3: Optimizing AST with Greedy Best-First Search...")
        optimized_ast, transformations = optimizer.optimize(ast)
        if verbose:
            if transformations:
                print(f"         Transformations applied: {', '.join(transformations)}")
            else:
                print("         No profitable transformations found.")
            print(f"         Optimized AST Cost: {optimized_ast.cost}")
    else:
        if verbose: print("Step 3: Greedy AST Optimization disabled by flag.")

    # 4. Execution
    if verbose: 
        print("Step 4: Executing final AST...")
        print("--- Program Output ---")

    interpreter.interpret(optimized_ast)
    
    if verbose:
        print("--- End Program Output ---")
        print("\nExecution finished.")
    
    # Final Statistics
    if verbose:
        print("\n--- Performance & Optimization Report ---")
        
        # Optimizer stats
        print("Greedy Optimization:")
        if use_greedy and optimizer:
            opt_stats = optimizer.get_stats()
            print(f"  - Search States Explored: {opt_stats['states_explored']}")
            print(f"  - Transformations Applied: {opt_stats['transformations_applied']}")
        else:
            print("  - Status: Disabled")
            
        # DP stats
        dp_stats = interpreter.get_dp_stats()
        print("Dynamic Programming:")
        if use_dp:
            print(f"  - Status: Enabled")
            print(f"  - Subproblems Solved: {dp_stats['subproblems_solved']}")
            print(f"  - Cache Hits: {dp_stats['cache_hits']}")
            print(f"  - Hit Rate: {dp_stats['hit_rate']}")
        else:
            print("  - Status: Disabled")


def comprehensive_algorithm_demo(verbose: bool, use_greedy: bool, use_dp: bool):
    """Runs an internal demo script with the specified flags."""
    print("--- Running Internal Interpreter Demo ---")
    
    factorial_code = '''
# Ngitung faktorial 6
n = 6
hasil = 1

# Ieu loop pikeun ngitung faktorial
bari n > 0 {
  hasil = hasil * n
  n = n - 1
}

# Ieu bakal dicitak ka konsol
cetak(hasil) # Output kedahna 720
'''
    
    temp_file = "demo.nyunda"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(factorial_code)
        
        run_file(
            filepath=temp_file,
            verbose=verbose,
            use_greedy=use_greedy,
            use_dp=use_dp
        )
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Nyunda Interpreter: Executes .nyunda language files.",
        formatter_class=argparse.RawTextHelpFormatter # For better help text formatting
    )
    
    parser.add_argument(
        'filepath', 
        nargs='?', 
        default=None, 
        help='The path to the .nyunda file to execute.\nIf not provided, a built-in demo will run.'
    )
    
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true', 
        help='Enable detailed output, including pipeline steps,\nperformance reports, and optimization details.'
    )
    
    parser.add_argument(
        '--no-greedy', 
        action='store_true', 
        help='Disable the Greedy Best-First Search AST optimization pass.'
    )
    
    parser.add_argument(
        '--no-dp', 
        action='store_true', 
        help='Disable the Dynamic Programming (memoization) expression evaluator.'
    )

    args = parser.parse_args()

    # Determine runtime configuration from flags
    config = {
        "verbose": args.verbose,
        "use_greedy": not args.no_greedy,
        "use_dp": not args.no_dp
    }

    if args.filepath:
        run_file(filepath=args.filepath, **config)
    else:
        # If running the demo, it's most useful to see the detailed report.
        if not args.verbose:
            print("No file provided. Running internal demo in verbose mode to be illustrative.")
            print("Use 'python main.py --help' for all options.")
        config["verbose"] = True # Force verbose for demo
        comprehensive_algorithm_demo(**config)

