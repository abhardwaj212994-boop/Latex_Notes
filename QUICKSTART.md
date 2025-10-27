# RAG LaTeX Generator - Quick Reference

## 🚀 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/rag-latex-generator.git
cd rag-latex-generator

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## 📝 Basic Usage

### Generate Notes
```bash
# Basic usage
python rag_latex_enhanced.py "Machine Learning"

# Custom output filename
python rag_latex_enhanced.py "Quantum Computing" -o quantum.tex

# With API key as argument
python rag_latex_enhanced.py "Topic" --api-key your-key-here
```

### Compile LaTeX
```bash
# Compile to PDF
pdflatex your_notes.tex
pdflatex your_notes.tex  # Run twice for TOC

# Or use Makefile
make compile FILE=your_notes.tex
```

## 🎯 Common Tasks

### Run Demo
```bash
python demo.py
# or
make demo
```

### Clean Build Files
```bash
make clean
```

### Compile All Files
```bash
make compile-all
```

### Setup GitHub
```bash
python setup_github.py your_github_username
# or
make setup-github USER=your_github_username
```

## 📚 Topic Examples

```bash
# Computer Science
python rag_latex_enhanced.py "Data Structures"
python rag_latex_enhanced.py "Algorithms"
python rag_latex_enhanced.py "Operating Systems"

# Mathematics
python rag_latex_enhanced.py "Linear Algebra"
python rag_latex_enhanced.py "Calculus"
python rag_latex_enhanced.py "Probability Theory"

# Physics
python rag_latex_enhanced.py "Classical Mechanics"
python rag_latex_enhanced.py "Electromagnetism"
python rag_latex_enhanced.py "Quantum Mechanics"

# AI/ML
python rag_latex_enhanced.py "Neural Networks"
python rag_latex_enhanced.py "Deep Learning"
python rag_latex_enhanced.py "Reinforcement Learning"
```

## 🛠️ Configuration

### Environment Variables (.env)
```bash
ANTHROPIC_API_KEY=your_key_here
```

### Get API Key
Visit: https://console.anthropic.com/

## 📊 File Structure

```
rag-latex-generator/
├── rag_latex_enhanced.py     # Main generator
├── rag_latex_generator.py    # Basic version
├── demo.py                   # Demo/test script
├── setup_github.py           # GitHub setup
├── requirements.txt          # Dependencies
├── .env                      # API configuration
├── Makefile                  # Build automation
└── README.md                 # Documentation
```

## 🎨 Diagram Types Supported

- Flowcharts
- Architecture diagrams
- Graph structures
- Tree structures
- Concept maps
- Mind maps
- Network diagrams
- Mathematical plots

## ⚡ Pro Tips

1. **Run LaTeX twice**: Always compile twice for proper TOC and references
2. **Check output**: Review generated content before final use
3. **Customize**: Edit .tex files to add personal touches
4. **Version control**: Commit .tex files to track changes
5. **Batch process**: Create scripts for multiple topics

## 🐛 Troubleshooting

### API Key Issues
```bash
# Check if key is set
echo $ANTHROPIC_API_KEY

# Set temporarily
export ANTHROPIC_API_KEY=your_key_here
```

### LaTeX Compilation Errors
```bash
# Check LaTeX installation
pdflatex --version

# Install LaTeX (Ubuntu)
sudo apt-get install texlive-full
```

### Python Dependencies
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📞 Support

- Issues: https://github.com/yourusername/rag-latex-generator/issues
- Docs: https://github.com/yourusername/rag-latex-generator

## 🔗 Useful Links

- Anthropic API: https://docs.anthropic.com/
- LaTeX Documentation: https://www.latex-project.org/
- TikZ Manual: https://www.ctan.org/pkg/pgf

---

**Quick Start**: `make install && make demo`
