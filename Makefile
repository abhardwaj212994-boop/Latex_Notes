# Makefile for RAG LaTeX Generator

.PHONY: help install demo clean compile-all test setup-github

# Default target
help:
	@echo "RAG LaTeX Generator - Makefile Commands"
	@echo "========================================"
	@echo ""
	@echo "Available targets:"
	@echo "  make install       - Install Python dependencies"
	@echo "  make demo          - Run demo generation"
	@echo "  make test          - Run verification tests"
	@echo "  make compile       - Compile a LaTeX file (use FILE=filename.tex)"
	@echo "  make compile-all   - Compile all .tex files in current directory"
	@echo "  make clean         - Remove generated files"
	@echo "  make setup-github  - Setup and push to GitHub (use USER=username)"
	@echo ""
	@echo "Examples:"
	@echo "  make install"
	@echo "  make demo"
	@echo "  make compile FILE=notes.tex"
	@echo "  make setup-github USER=yourusername"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"
	@echo ""
	@echo "Next steps:"
	@echo "1. Copy .env.example to .env"
	@echo "2. Add your Anthropic API key to .env"
	@echo "3. Run: make demo"

# Run demo
demo:
	@echo "Running demo..."
	python demo.py

# Run tests
test:
	@echo "Running verification tests..."
	python demo.py

# Compile a single LaTeX file
compile:
ifndef FILE
	@echo "Error: Please specify FILE=filename.tex"
	@echo "Example: make compile FILE=notes.tex"
	@exit 1
endif
	@echo "Compiling $(FILE)..."
	pdflatex $(FILE)
	pdflatex $(FILE)
	@echo "✓ Compiled successfully"
	@echo "Output: $(basename $(FILE)).pdf"

# Compile all .tex files
compile-all:
	@echo "Compiling all .tex files..."
	@for file in *.tex; do \
		if [ -f "$$file" ]; then \
			echo "Compiling $$file..."; \
			pdflatex "$$file" > /dev/null 2>&1; \
			pdflatex "$$file" > /dev/null 2>&1; \
			echo "✓ $$file -> $${file%.tex}.pdf"; \
		fi \
	done
	@echo "✓ All files compiled"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -f *.aux *.log *.out *.toc *.synctex.gz *.fls *.fdb_latexmk
	@echo "✓ Cleaned LaTeX auxiliary files"
	@echo ""
	@echo "To also remove PDFs: rm -f *.pdf"
	@echo "To also remove .tex: rm -f *_notes.tex"

# Setup GitHub
setup-github:
ifndef USER
	@echo "Error: Please specify USER=your_github_username"
	@echo "Example: make setup-github USER=johndoe"
	@exit 1
endif
	@echo "Setting up GitHub repository..."
	python setup_github.py $(USER)

# Generate notes for a topic
generate:
ifndef TOPIC
	@echo "Error: Please specify TOPIC='Your Topic'"
	@echo "Example: make generate TOPIC='Machine Learning'"
	@exit 1
endif
	@echo "Generating notes for: $(TOPIC)"
	python rag_latex_enhanced.py "$(TOPIC)"

# Quick start - install and run demo
quickstart: install
	@echo ""
	@echo "⚠️  Before running demo:"
	@echo "1. Copy .env.example to .env"
	@echo "2. Add your Anthropic API key to .env"
	@echo ""
	@read -p "Press Enter when ready to continue..." dummy
	$(MAKE) demo
