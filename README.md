# RAG LaTeX Notes Generator 📚

An advanced Retrieval-Augmented Generation (RAG) pipeline that automatically generates comprehensive, publication-quality LaTeX notes with detailed TikZ diagrams for any topic.

## 🌟 Features

- **Intelligent Research**: Uses RAG techniques to gather and synthesize information about any topic
- **Comprehensive Notes**: Generates detailed, well-structured LaTeX documents
- **Beautiful Diagrams**: Automatically creates TikZ diagrams including:
  - Flowcharts and process diagrams
  - Architecture diagrams
  - Concept maps and mind maps
  - Mathematical graphs
  - Tree structures
  - Network diagrams
- **Professional Formatting**: Publication-quality LaTeX with proper theorem environments, equations, and styling
- **Customizable Output**: Full control over structure and content generation

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
- Anthropic API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/rag-latex-generator.git
   cd rag-latex-generator
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

### Basic Usage

```bash
# Generate notes on a topic
python rag_latex_enhanced.py "Machine Learning"

# Specify output filename
python rag_latex_enhanced.py "Quantum Computing" -o quantum_notes.tex

# Use custom API key
python rag_latex_enhanced.py "Neural Networks" --api-key your-api-key-here
```

### Compile the LaTeX

```bash
# Compile the generated LaTeX file
pdflatex machine_learning_notes.tex
pdflatex machine_learning_notes.tex  # Run twice for table of contents
```

## 📖 Usage Examples

### Example 1: Computer Science Topic
```bash
python rag_latex_enhanced.py "Data Structures and Algorithms"
```

Generates comprehensive notes covering:
- Arrays, linked lists, stacks, queues
- Trees and graphs
- Sorting and searching algorithms
- Time complexity analysis
- With visual diagrams for each structure

### Example 2: Mathematics Topic
```bash
python rag_latex_enhanced.py "Linear Algebra" -o linear_algebra.tex
```

Generates notes with:
- Vector spaces and transformations
- Matrices and determinants
- Eigenvalues and eigenvectors
- Mathematical proofs and theorems
- Geometric visualizations

### Example 3: Physics Topic
```bash
python rag_latex_enhanced.py "Quantum Mechanics Fundamentals"
```

Generates notes covering:
- Wave-particle duality
- Schrödinger equation
- Quantum states and operators
- Measurement and uncertainty
- Diagrams of quantum systems

## 🏗️ Architecture

```
rag-latex-generator/
├── rag_latex_enhanced.py     # Main enhanced pipeline
├── rag_latex_generator.py    # Basic pipeline
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── README.md                 # This file
├── setup_github.py           # GitHub integration script
└── examples/                 # Example outputs
    ├── machine_learning_notes.tex
    └── quantum_computing_notes.tex
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

### Command Line Options

```
usage: rag_latex_enhanced.py [-h] [-o OUTPUT] [--api-key API_KEY] topic

positional arguments:
  topic                 Topic to generate notes for

optional arguments:
  -h, --help           show this help message and exit
  -o, --output OUTPUT  Output filename
  --api-key API_KEY    Anthropic API key
```

## 📊 Pipeline Stages

The RAG pipeline consists of five main phases:

### Phase 1: Research & Information Gathering
- Generates comprehensive search queries
- Retrieves information from multiple sources
- Caches research data for content generation

### Phase 2: Document Planning & Outlining
- Analyzes research to create document structure
- Defines sections, subsections, and key points
- Plans diagram placements

### Phase 3: Content Generation
- Generates detailed content for each section
- Creates mathematical formulas and equations
- Writes examples and explanations

### Phase 4: Diagram Creation
- Generates TikZ code for visualizations
- Creates various diagram types (flowcharts, trees, graphs)
- Ensures diagrams match section content

### Phase 5: Document Assembly
- Combines all components
- Adds proper LaTeX formatting
- Generates table of contents and references

## 🎨 Diagram Types

The generator can create various TikZ diagrams:

- **Flowcharts**: Process flows, algorithms, decision trees
- **Architecture Diagrams**: System designs, component relationships
- **Graphs**: Networks, mathematical functions, data plots
- **Trees**: Hierarchies, parse trees, decision trees
- **Concept Maps**: Relationships between ideas
- **Mind Maps**: Topic organization and brainstorming

## 🔬 Advanced Features

### Custom Sections
Edit the generated `.tex` file to add custom sections or modify content.

### Multiple Topics
Generate notes for multiple related topics:

```bash
python rag_latex_enhanced.py "Deep Learning Fundamentals"
python rag_latex_enhanced.py "Convolutional Neural Networks"
python rag_latex_enhanced.py "Recurrent Neural Networks"
```

### Batch Processing
Create a script to generate multiple notes:

```bash
#!/bin/bash
topics=("Linear Algebra" "Calculus" "Probability Theory")
for topic in "${topics[@]}"; do
    python rag_latex_enhanced.py "$topic"
done
```

## 📝 LaTeX Document Structure

Generated documents include:

```latex
\documentclass[11pt,a4paper]{article}
% Professional packages and styling
\begin{document}
    \maketitle
    \abstract{...}
    \tableofcontents
    
    \section{Introduction}
        % Content with formulas
        \begin{theorem}...\end{theorem}
        \begin{figure}
            \begin{tikzpicture}
                % TikZ diagram
            \end{tikzpicture}
        \end{figure}
    
    \section{Main Topics}
        % More sections...
\end{document}
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Anthropic's Claude API](https://www.anthropic.com)
- TikZ for beautiful diagrams
- LaTeX for professional typesetting

## 📧 Contact

For questions or issues, please open an issue on GitHub or contact the maintainer.

## 🚦 Roadmap

- [ ] Support for multiple output formats (Markdown, HTML)
- [ ] Integration with citation management (BibTeX)
- [ ] Web interface for easier access
- [ ] Custom diagram templates
- [ ] Multi-language support
- [ ] Collaborative editing features
- [ ] Direct PDF generation
- [ ] Cloud deployment options

## 💡 Tips

1. **Run LaTeX twice**: Always compile twice to generate the table of contents correctly
2. **Check API limits**: Be aware of API rate limits when generating multiple documents
3. **Customize styling**: Edit the preamble section to match your preferred style
4. **Review content**: AI-generated content should be reviewed for accuracy
5. **Version control**: Commit generated `.tex` files to track changes

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'anthropic'`
- **Solution**: Run `pip install -r requirements.txt`

**Issue**: LaTeX compilation errors
- **Solution**: Ensure you have a complete LaTeX distribution installed

**Issue**: API key not found
- **Solution**: Check that your `.env` file exists and contains `ANTHROPIC_API_KEY`

**Issue**: Diagrams not rendering
- **Solution**: Ensure TikZ packages are installed in your LaTeX distribution

## 📚 Examples

See the `examples/` directory for sample generated documents on topics like:
- Machine Learning
- Quantum Computing
- Data Structures
- Linear Algebra
- And more!

---

**Made with ❤️ using RAG and LaTeX**

*Star ⭐ this repo if you find it useful!*
