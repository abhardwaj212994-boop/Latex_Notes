#!/usr/bin/env python3
"""
Demo script for RAG LaTeX Generator
Tests the installation and generates a sample document
"""

import os
import sys
from pathlib import Path


def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...\n")
    
    dependencies = {
        'anthropic': 'Anthropic API client',
        'requests': 'HTTP library',
        'dotenv': 'Environment variable management'
    }
    
    missing = []
    
    for module, description in dependencies.items():
        try:
            __import__(module if module != 'dotenv' else 'dotenv')
            print(f"✓ {module:12s} - {description}")
        except ImportError:
            print(f"✗ {module:12s} - {description} (MISSING)")
            missing.append(module)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies installed")
    return True


def check_api_key():
    """Check if Anthropic API key is configured"""
    print("\nChecking API key configuration...\n")
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print("✓ .env file exists")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'ANTHROPIC_API_KEY' in content and 'your_api_key_here' not in content:
                print("✓ API key appears to be configured in .env")
                return True
            else:
                print("⚠️  API key not configured in .env file")
    else:
        print("⚠️  .env file not found")
    
    # Check environment variable
    if os.environ.get('ANTHROPIC_API_KEY'):
        print("✓ API key found in environment variables")
        return True
    
    print("\n❌ API key not configured")
    print("\nTo configure:")
    print("1. Copy .env.example to .env")
    print("2. Edit .env and add your Anthropic API key")
    print("3. Get your key from: https://console.anthropic.com/")
    
    return False


def check_latex():
    """Check if LaTeX is installed"""
    print("\nChecking LaTeX installation...\n")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ['pdflatex', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ LaTeX (pdflatex) is installed")
            version_line = result.stdout.split('\n')[0]
            print(f"  Version: {version_line}")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️  LaTeX not found")
    print("\nLaTeX is required to compile generated .tex files to PDF")
    print("Install options:")
    print("  • Ubuntu/Debian: sudo apt-get install texlive-full")
    print("  • macOS: brew install mactex")
    print("  • Windows: Download MiKTeX from miktex.org")
    
    return False


def run_demo():
    """Run a simple demo generation"""
    print("\nRunning demo generation...\n")
    print("=" * 60)
    
    # Check if we can run the demo
    if not check_api_key():
        print("\n⚠️  Cannot run demo without API key")
        print("Configure your API key first, then run this demo again")
        return False
    
    try:
        from rag_latex_enhanced import EnhancedRAGLatexGenerator
        
        print("\n🚀 Generating sample notes on 'Binary Search Trees'")
        print("   This may take 2-3 minutes...\n")
        
        generator = EnhancedRAGLatexGenerator()
        output_file = generator.generate(
            "Binary Search Trees",
            "demo_binary_search_trees.tex"
        )
        
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("=" * 60)
        print(f"\nGenerated file: {output_file}")
        print("\nTo compile to PDF:")
        print(f"  pdflatex {output_file}")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure the generator scripts are in the current directory")
        return False
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_usage_examples():
    """Show usage examples"""
    print("\n" + "=" * 60)
    print("Usage Examples")
    print("=" * 60 + "\n")
    
    examples = [
        ("Basic usage", 
         'python rag_latex_enhanced.py "Machine Learning"'),
        
        ("Custom output file", 
         'python rag_latex_enhanced.py "Quantum Physics" -o quantum.tex'),
        
        ("With API key argument",
         'python rag_latex_enhanced.py "Neural Networks" --api-key sk-xxx'),
        
        ("Compile to PDF",
         'pdflatex machine_learning_notes.tex'),
    ]
    
    for title, command in examples:
        print(f"{title}:")
        print(f"  $ {command}\n")


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("RAG LaTeX Generator - Setup Verification & Demo")
    print("=" * 60 + "\n")
    
    # Run checks
    deps_ok = check_dependencies()
    api_ok = check_api_key()
    latex_ok = check_latex()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60 + "\n")
    
    if deps_ok and api_ok:
        print("✓ System is ready to generate LaTeX notes")
        if latex_ok:
            print("✓ System is ready to compile LaTeX to PDF")
        else:
            print("⚠️  LaTeX not installed (optional, for PDF compilation)")
        
        # Ask if user wants to run demo
        print("\n" + "-" * 60)
        response = input("\nRun demo generation? (y/n): ").strip().lower()
        if response == 'y':
            run_demo()
        else:
            show_usage_examples()
    else:
        print("❌ System not ready")
        if not deps_ok:
            print("   → Install dependencies: pip install -r requirements.txt")
        if not api_ok:
            print("   → Configure API key in .env file")
    
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
