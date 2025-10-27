# Contributing to RAG LaTeX Generator

Thank you for your interest in contributing to the RAG LaTeX Generator! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, LaTeX version)
- Error messages or logs

### Suggesting Features

Feature requests are welcome! Please create an issue with:
- Clear description of the feature
- Use cases and benefits
- Possible implementation approach

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/rag-latex-generator.git
   cd rag-latex-generator
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clear, commented code
   - Follow existing code style
   - Add tests if applicable

4. **Test your changes**
   ```bash
   python demo.py
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add: clear description of your changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide a clear description
   - Reference any related issues
   - Include examples if applicable

## 📝 Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular
- Comment complex logic

### Example Function Structure

```python
def generate_content(topic: str, context: Dict) -> str:
    """
    Generate content for a specific topic.
    
    Args:
        topic: The topic to generate content for
        context: Dictionary containing research data
        
    Returns:
        Generated content as a string
        
    Raises:
        ValueError: If topic is empty
    """
    if not topic:
        raise ValueError("Topic cannot be empty")
    
    # Implementation here
    return content
```

## 🧪 Testing

- Test your changes with various topics
- Ensure LaTeX compiles without errors
- Verify TikZ diagrams render correctly
- Check for edge cases

## 🎨 Documentation

- Update README.md for new features
- Add examples for new functionality
- Update docstrings
- Include inline comments for complex logic

## 🌟 Areas for Contribution

### High Priority
- [ ] Add support for bibliography/citations (BibTeX)
- [ ] Improve diagram generation algorithms
- [ ] Add support for different LaTeX document classes
- [ ] Optimize API usage and caching

### Medium Priority
- [ ] Add more diagram types
- [ ] Support for custom LaTeX templates
- [ ] Multi-language content generation
- [ ] Web interface

### Ideas Welcome
- Integration with other AI models
- Export to other formats (Markdown, HTML)
- Collaborative editing features
- Cloud deployment options

## 🐛 Known Issues

Check the [Issues](https://github.com/yourusername/rag-latex-generator/issues) page for known bugs and planned features.

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 💬 Questions?

- Open an issue for questions
- Join discussions in existing issues
- Check README.md for documentation

## 🙏 Recognition

Contributors will be recognized in the README.md file.

Thank you for making RAG LaTeX Generator better!
