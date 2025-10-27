#!/usr/bin/env python3
"""
RAG-based LaTeX Notes Generator
Generates comprehensive LaTeX notes with TikZ diagrams for any given topic
"""

import os
import json
import re
from typing import List, Dict, Tuple
import anthropic
from datetime import datetime


class RAGLatexGenerator:
    """Main class for generating LaTeX notes using RAG approach"""
    
    def __init__(self, api_key: str = None):
        """Initialize the generator with Anthropic API key"""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Set it as environment variable.")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
    def research_topic(self, topic: str) -> List[Dict[str, str]]:
        """
        Research the topic by generating comprehensive search queries
        and gathering information
        """
        print(f"🔍 Researching topic: {topic}")
        
        # Generate research queries
        queries = self._generate_search_queries(topic)
        
        # Gather information from searches
        research_data = []
        for query in queries:
            print(f"  → Searching: {query}")
            result = self._search_web(query)
            if result:
                research_data.append({
                    "query": query,
                    "content": result
                })
        
        return research_data
    
    def _generate_search_queries(self, topic: str) -> List[str]:
        """Generate comprehensive search queries for the topic"""
        queries = [
            f"{topic} comprehensive guide",
            f"{topic} fundamentals and basics",
            f"{topic} advanced concepts",
            f"{topic} practical examples",
            f"{topic} diagrams and visualizations",
            f"{topic} key theorems and principles",
            f"{topic} applications and use cases"
        ]
        return queries
    
    def _search_web(self, query: str) -> str:
        """Simulate web search - in real implementation, use actual search API"""
        # This would integrate with actual search APIs
        # For now, return a placeholder
        return f"Research content for: {query}"
    
    def generate_latex_structure(self, topic: str, research_data: List[Dict]) -> Dict:
        """
        Generate the structure of the LaTeX document based on research
        """
        print(f"📝 Generating document structure...")
        
        prompt = f"""Based on the following research data about '{topic}', create a comprehensive 
        LaTeX document structure with sections, subsections, and content outline.
        
        Research data:
        {json.dumps(research_data, indent=2)}
        
        Generate a detailed structure with:
        1. Document title and abstract
        2. Main sections (5-8 sections)
        3. Subsections for each main section
        4. Content outline for each subsection
        5. Suggested TikZ diagrams for each section (what to visualize)
        
        Return as JSON with structure:
        {{
            "title": "...",
            "abstract": "...",
            "sections": [
                {{
                    "title": "...",
                    "content": "...",
                    "subsections": [...],
                    "diagram_suggestions": [...]
                }}
            ]
        }}
        """
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract JSON from response
        response_text = message.content[0].text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {}
    
    def generate_section_content(self, topic: str, section: Dict, research_data: List[Dict]) -> str:
        """Generate detailed LaTeX content for a section"""
        print(f"  ✍️  Generating content for: {section['title']}")
        
        prompt = f"""Generate comprehensive LaTeX content for the following section about '{topic}'.
        
        Section: {section['title']}
        Outline: {section.get('content', '')}
        
        Research context:
        {json.dumps(research_data[:3], indent=2)}
        
        Requirements:
        - Write detailed, academic-quality content
        - Include mathematical formulas where appropriate (use LaTeX math mode)
        - Add examples and explanations
        - Use proper LaTeX formatting (\\textbf, \\emph, etc.)
        - Include itemize/enumerate lists where helpful
        - Write 3-5 paragraphs minimum
        - Be technically accurate and comprehensive
        
        Return ONLY the LaTeX content, no additional formatting or markdown.
        """
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text.strip()
    
    def generate_tikz_diagram(self, topic: str, diagram_description: str, section_context: str) -> str:
        """Generate TikZ code for a diagram"""
        print(f"  🎨 Generating TikZ diagram: {diagram_description}")
        
        prompt = f"""Generate TikZ/LaTeX code for the following diagram about '{topic}'.
        
        Diagram description: {diagram_description}
        Context: {section_context}
        
        Requirements:
        - Create a complete TikZ picture environment
        - Make it visually appealing and informative
        - Use appropriate shapes, arrows, and labels
        - Include colors for clarity
        - Add a caption
        - Make it publication-quality
        - Use \\begin{{figure}}[htbp] environment
        
        Return ONLY the complete LaTeX figure code with TikZ, no markdown.
        """
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text.strip()
    
    def compile_latex_document(self, topic: str, structure: Dict, 
                               section_contents: List[str], 
                               diagrams: List[str]) -> str:
        """Compile all components into a complete LaTeX document"""
        print(f"📄 Compiling final LaTeX document...")
        
        latex_doc = self._get_latex_header(topic, structure.get('abstract', ''))
        
        # Add each section with content and diagrams
        for i, section in enumerate(structure.get('sections', [])):
            latex_doc += f"\n\\section{{{section['title']}}}\n\n"
            
            # Add section content
            if i < len(section_contents):
                latex_doc += section_contents[i] + "\n\n"
            
            # Add diagram if available
            if i < len(diagrams) and diagrams[i]:
                latex_doc += diagrams[i] + "\n\n"
        
        latex_doc += self._get_latex_footer()
        
        return latex_doc
    
    def _get_latex_header(self, topic: str, abstract: str) -> str:
        """Generate LaTeX document header"""
        return f"""\\documentclass[12pt,a4paper]{{article}}

% Packages
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{amsmath,amssymb,amsthm}}
\\usepackage{{graphicx}}
\\usepackage{{tikz}}
\\usepackage{{xcolor}}
\\usepackage{{hyperref}}
\\usepackage{{geometry}}
\\usepackage{{fancyhdr}}
\\usepackage{{tcolorbox}}
\\usepackage{{enumitem}}

% TikZ libraries
\\usetikzlibrary{{shapes,arrows,positioning,calc,patterns,decorations.pathreplacing}}
\\usetikzlibrary{{shadows,trees,mindmap,backgrounds}}

% Page geometry
\\geometry{{margin=1in}}

% Header and footer
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\rhead{{\\thepage}}
\\lhead{{{topic}}}

% Theorem environments
\\newtheorem{{theorem}}{{Theorem}}[section]
\\newtheorem{{lemma}}[theorem]{{Lemma}}
\\newtheorem{{proposition}}[theorem]{{Proposition}}
\\newtheorem{{corollary}}[theorem]{{Corollary}}
\\theoremstyle{{definition}}
\\newtheorem{{definition}}{{Definition}}[section]
\\newtheorem{{example}}{{Example}}[section]

% Title information
\\title{{\\textbf{{Comprehensive Notes on {topic}}}}}
\\author{{Generated by RAG LaTeX Generator}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
{abstract}
\\end{{abstract}}

\\tableofcontents
\\newpage

"""
    
    def _get_latex_footer(self) -> str:
        """Generate LaTeX document footer"""
        return """
\\end{document}
"""
    
    def generate_notes(self, topic: str, output_file: str = None) -> str:
        """
        Main method to generate comprehensive LaTeX notes for a topic
        """
        print(f"\n{'='*60}")
        print(f"🚀 Starting RAG LaTeX Generation for: {topic}")
        print(f"{'='*60}\n")
        
        # Step 1: Research the topic
        research_data = self.research_topic(topic)
        
        # Step 2: Generate document structure
        structure = self.generate_latex_structure(topic, research_data)
        
        # Step 3: Generate content for each section
        section_contents = []
        for section in structure.get('sections', []):
            content = self.generate_section_content(topic, section, research_data)
            section_contents.append(content)
        
        # Step 4: Generate TikZ diagrams
        diagrams = []
        for section in structure.get('sections', []):
            diagram_suggestions = section.get('diagram_suggestions', [])
            if diagram_suggestions:
                diagram = self.generate_tikz_diagram(
                    topic, 
                    diagram_suggestions[0], 
                    section.get('content', '')
                )
                diagrams.append(diagram)
            else:
                diagrams.append("")
        
        # Step 5: Compile final document
        latex_document = self.compile_latex_document(
            topic, structure, section_contents, diagrams
        )
        
        # Step 6: Save to file
        if output_file is None:
            output_file = f"{topic.replace(' ', '_').lower()}_notes.tex"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(latex_document)
        
        print(f"\n✅ LaTeX notes generated successfully!")
        print(f"📁 Output file: {output_file}")
        print(f"\nTo compile: pdflatex {output_file}")
        
        return output_file


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate comprehensive LaTeX notes with TikZ diagrams using RAG"
    )
    parser.add_argument(
        "topic",
        type=str,
        help="Topic to generate notes for"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output LaTeX file name (default: <topic>_notes.tex)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Anthropic API key (or set ANTHROPIC_API_KEY env variable)"
    )
    
    args = parser.parse_args()
    
    try:
        generator = RAGLatexGenerator(api_key=args.api_key)
        output_file = generator.generate_notes(args.topic, args.output)
        print(f"\n🎉 Success! Your notes are ready in: {output_file}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
