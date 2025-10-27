# RAG LaTeX Generator - Complete Setup Guide

## 📦 What's Included

Your RAG LaTeX Generator project is ready! Here's what you have:

### Core Scripts
- `rag_latex_enhanced.py` - Main enhanced generator with full features
- `rag_latex_generator.py` - Basic version for learning
- `demo.py` - Test and demo script
- `setup_github.py` - GitHub integration script
- `install.sh` - Automated installation script

### Configuration Files
- `requirements.txt` - Python dependencies
- `.env.example` - API key configuration template
- `.gitignore` - Git exclusions
- `Makefile` - Build automation

### Documentation
- `README.md` - Main documentation
- `QUICKSTART.md` - Quick reference guide
- `CONTRIBUTING.md` - Contribution guidelines
- `PROJECT_OVERVIEW.md` - Technical overview
- `LICENSE` - MIT License

## 🚀 Quick Start (5 Minutes)

### Step 1: Setup Project Directory
```bash
# Create a directory for your project
mkdir rag-latex-generator
cd rag-latex-generator

# Copy all files from this outputs folder to your directory
```

### Step 2: Install Dependencies
```bash
# Run the automated installation
bash install.sh

# OR manually:
pip install -r requirements.txt
```

### Step 3: Configure API Key
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Anthropic API key
# Get your key from: https://console.anthropic.com/
nano .env  # or use your preferred editor
```

### Step 4: Test the Installation
```bash
# Run the demo
python3 demo.py

# This will check your setup and optionally generate a sample document
```

### Step 5: Generate Your First Notes
```bash
# Generate notes on any topic
python3 rag_latex_enhanced.py "Machine Learning"

# Compile to PDF (requires LaTeX)
pdflatex machine_learning_notes.tex
pdflatex machine_learning_notes.tex  # Run twice for TOC
```

## 🐙 Push to GitHub

### Method 1: Using the Setup Script (Easiest)

```bash
# Initialize git and push to GitHub
python3 setup_github.py YOUR_GITHUB_USERNAME

# This will:
# 1. Initialize git repository
# 2. Add all files
# 3. Create initial commit
# 4. Add GitHub remote
# 5. Push to GitHub
```

**Note**: You must first create an empty repository on GitHub:
1. Go to https://github.com/new
2. Create repository named `rag-latex-generator`
3. Don't initialize with README, .gitignore, or license
4. Then run the setup script

### Method 2: Manual Setup

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: RAG LaTeX Generator"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/rag-latex-generator.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Method 3: Using Makefile

```bash
# If you have Make installed
make setup-github USER=YOUR_GITHUB_USERNAME
```

## 🔑 Getting Your Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (it starts with `sk-ant-`)
6. Add it to your `.env` file:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

## 📖 Usage Examples

### Generate Different Types of Notes

```bash
# Computer Science
python3 rag_latex_enhanced.py "Data Structures and Algorithms"
python3 rag_latex_enhanced.py "Operating Systems"

# Mathematics  
python3 rag_latex_enhanced.py "Linear Algebra"
python3 rag_latex_enhanced.py "Calculus and Analysis"

# Physics
python3 rag_latex_enhanced.py "Quantum Mechanics"
python3 rag_latex_enhanced.py "Electromagnetism"

# Custom filename
python3 rag_latex_enhanced.py "Neural Networks" -o my_notes.tex
```

### Compile to PDF

```bash
# Single file
pdflatex your_notes.tex
pdflatex your_notes.tex  # Run twice for TOC

# Using Make
make compile FILE=your_notes.tex

# Compile all .tex files
make compile-all
```

### Clean Up Build Files

```bash
# Remove auxiliary files
make clean

# Or manually
rm -f *.aux *.log *.out *.toc *.synctex.gz
```

## 🛠️ System Requirements

### Required
- Python 3.8 or higher
- Internet connection (for API calls)
- Anthropic API key

### Optional (for PDF compilation)
- LaTeX distribution:
  - **Ubuntu/Debian**: `sudo apt-get install texlive-full`
  - **macOS**: `brew install mactex`
  - **Windows**: Download MiKTeX from https://miktex.org

## 📊 Project Structure

```
rag-latex-generator/
├── rag_latex_enhanced.py      # Main generator
├── rag_latex_generator.py     # Basic version
├── demo.py                    # Demo/test script
├── setup_github.py            # GitHub setup
├── install.sh                 # Installation script
├── requirements.txt           # Dependencies
├── .env                       # Your API key (create from .env.example)
├── .env.example              # Template
├── .gitignore                # Git exclusions
├── Makefile                  # Build automation
├── README.md                 # Main documentation
├── QUICKSTART.md             # Quick reference
├── CONTRIBUTING.md           # Contribution guide
├── PROJECT_OVERVIEW.md       # Technical overview
└── LICENSE                   # MIT License
```

## 🎯 What the Generator Does

1. **Research Phase**: Gathers comprehensive information about your topic
2. **Planning Phase**: Creates a structured document outline
3. **Content Generation**: Writes detailed sections with formulas and examples
4. **Diagram Creation**: Generates beautiful TikZ diagrams
5. **Assembly**: Compiles everything into a professional LaTeX document

**Result**: A complete, publication-quality LaTeX document with:
- Title page and abstract
- Table of contents
- Multiple detailed sections
- Mathematical formulas
- TikZ diagrams
- Professional formatting
- Theorem environments
- Examples and explanations

## ⏱️ Generation Time

- Simple topics: ~3-5 minutes
- Complex topics: ~5-7 minutes
- Includes: research, planning, content, diagrams, and assembly

## 💡 Pro Tips

1. **Run LaTeX Twice**: Always compile twice for proper cross-references and TOC
2. **Review Content**: AI-generated content should be reviewed for accuracy
3. **Customize**: Feel free to edit the generated .tex files
4. **Version Control**: Commit your .tex files to track changes
5. **Batch Processing**: Create scripts to generate multiple topics

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"
```bash
pip install -r requirements.txt
```

### "ANTHROPIC_API_KEY not found"
```bash
# Make sure you have .env file with your API key
cp .env.example .env
# Edit .env and add your key
```

### "LaTeX Error: File not found"
```bash
# Make sure LaTeX is installed
pdflatex --version

# Install if needed (Ubuntu)
sudo apt-get install texlive-full
```

### GitHub Push Fails
```bash
# Make sure repository exists on GitHub first
# Then check your authentication:
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Use personal access token if needed
```

## 📚 Learning Resources

- **Anthropic API**: https://docs.anthropic.com/
- **LaTeX Tutorial**: https://www.overleaf.com/learn
- **TikZ Manual**: https://www.ctan.org/pkg/pgf
- **Git Basics**: https://git-scm.com/book/en/v2

## 🤝 Contributing

Want to improve the generator? See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📞 Support

- Read [README.md](README.md) for comprehensive documentation
- Check [QUICKSTART.md](QUICKSTART.md) for quick reference
- Review [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for technical details
- Open issues on GitHub for bugs or questions

## 🎉 You're All Set!

Your RAG LaTeX Generator is ready to create amazing notes on any topic!

### Next Steps:
1. ✅ Install dependencies: `bash install.sh`
2. ✅ Configure API key in `.env`
3. ✅ Run demo: `python3 demo.py`
4. ✅ Generate your first notes
5. ✅ Push to GitHub (optional)

**Happy Note Taking! 📚✨**

---

Need help? Check the documentation files or visit the repository on GitHub.
