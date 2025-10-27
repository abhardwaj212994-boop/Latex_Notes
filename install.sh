#!/bin/bash
# Automated Installation Script for RAG LaTeX Generator

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  RAG LaTeX Generator - Automated Installation          ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check Python installation
check_python() {
    echo "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
        return 0
    else
        print_error "Python 3 not found"
        print_info "Please install Python 3.8 or higher"
        return 1
    fi
}

# Check pip installation
check_pip() {
    echo "Checking pip installation..."
    if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
        PIP_CMD=$(command -v pip3 || command -v pip)
        print_success "pip found"
        return 0
    else
        print_error "pip not found"
        print_info "Install with: python3 -m ensurepip"
        return 1
    fi
}

# Install Python dependencies
install_dependencies() {
    echo ""
    echo "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        $PIP_CMD install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        return 1
    fi
}

# Setup environment file
setup_env() {
    echo ""
    echo "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env file from template"
            print_warning "IMPORTANT: Edit .env and add your Anthropic API key"
        else
            print_error ".env.example not found"
            return 1
        fi
    else
        print_info ".env file already exists"
    fi
}

# Check LaTeX installation
check_latex() {
    echo ""
    echo "Checking LaTeX installation..."
    
    if command -v pdflatex &> /dev/null; then
        LATEX_VERSION=$(pdflatex --version | head -n 1)
        print_success "LaTeX found: $LATEX_VERSION"
        return 0
    else
        print_warning "LaTeX not found (optional)"
        print_info "LaTeX is needed to compile .tex files to PDF"
        print_info "Install options:"
        print_info "  • Ubuntu/Debian: sudo apt-get install texlive-full"
        print_info "  • macOS: brew install mactex"
        print_info "  • Windows: Download MiKTeX from miktex.org"
        return 1
    fi
}

# Check Git installation
check_git() {
    echo ""
    echo "Checking Git installation..."
    
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_success "Git found: $GIT_VERSION"
        return 0
    else
        print_warning "Git not found (optional)"
        print_info "Git is needed for version control and GitHub integration"
        return 1
    fi
}

# Run tests
run_tests() {
    echo ""
    echo "Running verification tests..."
    
    if [ -f "demo.py" ]; then
        python3 demo.py
    else
        print_warning "demo.py not found, skipping tests"
    fi
}

# Print next steps
print_next_steps() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  Installation Complete! Next Steps:                     ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "1. Configure your API key:"
    echo "   • Edit .env file"
    echo "   • Add your Anthropic API key"
    echo "   • Get key from: https://console.anthropic.com/"
    echo ""
    echo "2. Run a demo:"
    echo "   python3 demo.py"
    echo ""
    echo "3. Generate your first notes:"
    echo "   python3 rag_latex_enhanced.py \"Machine Learning\""
    echo ""
    echo "4. Compile to PDF (if LaTeX installed):"
    echo "   pdflatex machine_learning_notes.tex"
    echo ""
    echo "5. Setup GitHub (optional):"
    echo "   python3 setup_github.py your_github_username"
    echo ""
    print_info "See README.md for detailed documentation"
    print_info "See QUICKSTART.md for quick reference"
    echo ""
}

# Main installation process
main() {
    print_header
    
    # Track installation success
    INSTALL_SUCCESS=true
    
    # Required checks
    check_python || INSTALL_SUCCESS=false
    check_pip || INSTALL_SUCCESS=false
    
    if [ "$INSTALL_SUCCESS" = true ]; then
        install_dependencies || INSTALL_SUCCESS=false
        setup_env
    fi
    
    # Optional checks
    check_latex
    check_git
    
    # Final status
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    
    if [ "$INSTALL_SUCCESS" = true ]; then
        print_success "Installation completed successfully!"
        print_next_steps
        exit 0
    else
        print_error "Installation encountered errors"
        print_info "Please fix the errors above and run the script again"
        exit 1
    fi
}

# Run main installation
main
