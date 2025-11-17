#!/usr/bin/env python3
"""
Repository Audit Script
This script generates a comprehensive audit report of the Coding_team repository.
"""

import os
import re
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import ast

class RepositoryAuditor:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.file_data = []
        self.audit_results = {
            'file_tree': [],
            'scripts_analysis': [],
            'todos': [],
            'placeholders': [],
            'documentation': [],
            'tests': [],
            'completeness': []
        }
        
    def scan_repository(self):
        """Scan the repository and collect file information."""
        print("Scanning repository...")
        
        # Directories to ignore
        ignore_dirs = {'.git', '__pycache__', 'venv', 'coding_team_venv', '.vscode', 'node_modules'}
        
        for root, dirs, files in os.walk(self.repo_path):
            # Remove ignored directories from the walk
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.repo_path)
                
                file_info = {
                    'path': str(rel_path),
                    'name': file,
                    'extension': file_path.suffix,
                    'size': file_path.stat().st_size if file_path.exists() else 0,
                    'directory': str(rel_path.parent)
                }
                
                self.file_data.append(file_info)
                
    def analyze_python_file(self, file_path):
        """Analyze a Python file for various metrics."""
        analysis = {
            'path': str(file_path),
            'purpose': 'Unknown',
            'functions': [],
            'classes': [],
            'todos': [],
            'placeholders': [],
            'imports': [],
            'docstring': None,
            'line_count': 0,
            'completeness_score': 0,
            'has_main': False
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                analysis['line_count'] = len(lines)
                
                # Extract TODOs
                todos = re.findall(r'#\s*TODO[:\s]+(.*)', content, re.IGNORECASE)
                analysis['todos'] = todos
                
                # Extract placeholders (common patterns)
                placeholder_patterns = [
                    r'placeholder',
                    r'example\s+\w+',
                    r'replace\s+this',
                    r'fill\s+in',
                    r'set\s+\w+\s+data',
                    r'None\s*#\s*TODO'
                ]
                
                for pattern in placeholder_patterns:
                    placeholders = re.findall(pattern, content, re.IGNORECASE)
                    if placeholders:
                        analysis['placeholders'].extend(placeholders)
                
                # Try to parse with AST
                try:
                    tree = ast.parse(content)
                    
                    # Extract module docstring
                    if ast.get_docstring(tree):
                        analysis['docstring'] = ast.get_docstring(tree)
                        # Try to extract purpose from docstring
                        if analysis['docstring']:
                            first_line = analysis['docstring'].split('\n')[0]
                            analysis['purpose'] = first_line[:200]
                    
                    # Extract functions and classes
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            func_info = {
                                'name': node.name,
                                'args': [arg.arg for arg in node.args.args],
                                'has_docstring': ast.get_docstring(node) is not None
                            }
                            analysis['functions'].append(func_info)
                            
                            if node.name == 'main' or node.name == '__main__':
                                analysis['has_main'] = True
                                
                        elif isinstance(node, ast.ClassDef):
                            class_info = {
                                'name': node.name,
                                'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                                'has_docstring': ast.get_docstring(node) is not None
                            }
                            analysis['classes'].append(class_info)
                            
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                analysis['imports'].append(alias.name)
                                
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                analysis['imports'].append(node.module)
                                
                except SyntaxError as e:
                    analysis['parse_error'] = str(e)
                
                # Calculate completeness score (0-100)
                score = 0
                if analysis['docstring']:
                    score += 20
                if analysis['functions'] or analysis['classes']:
                    score += 20
                if not analysis['todos']:
                    score += 20
                if not analysis['placeholders']:
                    score += 20
                if len([f for f in analysis['functions'] if f['has_docstring']]) > 0:
                    score += 20
                    
                analysis['completeness_score'] = score
                
        except Exception as e:
            analysis['error'] = str(e)
            
        return analysis
    
    def analyze_all_scripts(self):
        """Analyze all Python scripts in the repository."""
        print("Analyzing Python scripts...")
        
        for file_info in self.file_data:
            if file_info['extension'] == '.py':
                file_path = self.repo_path / file_info['path']
                analysis = self.analyze_python_file(file_path)
                self.audit_results['scripts_analysis'].append(analysis)
                
                # Collect TODOs
                if analysis['todos']:
                    for todo in analysis['todos']:
                        self.audit_results['todos'].append({
                            'file': file_info['path'],
                            'todo': todo
                        })
                
                # Collect placeholders
                if analysis['placeholders']:
                    for placeholder in analysis['placeholders']:
                        self.audit_results['placeholders'].append({
                            'file': file_info['path'],
                            'placeholder': placeholder
                        })
                
                # Assess completeness
                self.audit_results['completeness'].append({
                    'file': file_info['path'],
                    'score': analysis['completeness_score'],
                    'has_docstring': analysis['docstring'] is not None,
                    'has_todos': len(analysis['todos']) > 0,
                    'has_placeholders': len(analysis['placeholders']) > 0,
                    'function_count': len(analysis['functions']),
                    'class_count': len(analysis['classes'])
                })
    
    def check_documentation(self):
        """Check for documentation files."""
        print("Checking documentation...")
        
        doc_extensions = {'.md', '.txt', '.rst', '.pdf', '.docx'}
        
        for file_info in self.file_data:
            if file_info['extension'] in doc_extensions:
                self.audit_results['documentation'].append({
                    'path': file_info['path'],
                    'type': file_info['extension'],
                    'size': file_info['size']
                })
    
    def check_tests(self):
        """Check for test files."""
        print("Checking for tests...")
        
        test_patterns = ['test_', '_test', 'tests', 'testing']
        
        for file_info in self.file_data:
            if any(pattern in file_info['name'].lower() for pattern in test_patterns):
                self.audit_results['tests'].append({
                    'path': file_info['path'],
                    'name': file_info['name']
                })
    
    def generate_file_tree_dataframe(self):
        """Generate a DataFrame representing the file tree."""
        print("Generating file tree DataFrame...")
        
        df = pd.DataFrame(self.file_data)
        self.audit_results['file_tree'] = df
        return df
    
    def generate_report(self, output_dir):
        """Generate comprehensive audit report."""
        print("Generating comprehensive report...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. File Tree DataFrame
        file_tree_df = self.generate_file_tree_dataframe()
        file_tree_path = output_path / f'file_tree_{timestamp}.csv'
        file_tree_df.to_csv(file_tree_path, index=False)
        print(f"✓ File tree saved to: {file_tree_path}")
        
        # 2. Scripts Analysis Report
        scripts_df = pd.DataFrame(self.audit_results['scripts_analysis'])
        scripts_path = output_path / f'scripts_analysis_{timestamp}.csv'
        if not scripts_df.empty:
            # Flatten complex columns for CSV
            scripts_simple = scripts_df.copy()
            scripts_simple['function_count'] = scripts_simple['functions'].apply(lambda x: len(x) if isinstance(x, list) else 0)
            scripts_simple['class_count'] = scripts_simple['classes'].apply(lambda x: len(x) if isinstance(x, list) else 0)
            scripts_simple['todo_count'] = scripts_simple['todos'].apply(lambda x: len(x) if isinstance(x, list) else 0)
            scripts_simple['placeholder_count'] = scripts_simple['placeholders'].apply(lambda x: len(x) if isinstance(x, list) else 0)
            
            scripts_simple[['path', 'purpose', 'line_count', 'completeness_score', 
                          'function_count', 'class_count', 'todo_count', 
                          'placeholder_count', 'has_main']].to_csv(scripts_path, index=False)
            print(f"✓ Scripts analysis saved to: {scripts_path}")
        
        # 3. TODOs Report
        todos_df = pd.DataFrame(self.audit_results['todos'])
        todos_path = output_path / f'todos_{timestamp}.csv'
        if not todos_df.empty:
            todos_df.to_csv(todos_path, index=False)
            print(f"✓ TODOs saved to: {todos_path}")
        
        # 4. Placeholders Report
        placeholders_df = pd.DataFrame(self.audit_results['placeholders'])
        placeholders_path = output_path / f'placeholders_{timestamp}.csv'
        if not placeholders_df.empty:
            placeholders_df.to_csv(placeholders_path, index=False)
            print(f"✓ Placeholders saved to: {placeholders_path}")
        
        # 5. Completeness Report
        completeness_df = pd.DataFrame(self.audit_results['completeness'])
        completeness_path = output_path / f'completeness_{timestamp}.csv'
        if not completeness_df.empty:
            completeness_df.to_csv(completeness_path, index=False)
            print(f"✓ Completeness report saved to: {completeness_path}")
        
        # 6. Documentation Report
        docs_df = pd.DataFrame(self.audit_results['documentation'])
        docs_path = output_path / f'documentation_{timestamp}.csv'
        if not docs_df.empty:
            docs_df.to_csv(docs_path, index=False)
            print(f"✓ Documentation report saved to: {docs_path}")
        
        # 7. Tests Report
        tests_df = pd.DataFrame(self.audit_results['tests'])
        tests_path = output_path / f'tests_{timestamp}.csv'
        if not tests_df.empty:
            tests_df.to_csv(tests_path, index=False)
            print(f"✓ Tests report saved to: {tests_path}")
        
        # 8. Generate comprehensive Markdown report
        self.generate_markdown_report(output_path, timestamp)
        
        return output_path
    
    def generate_markdown_report(self, output_path, timestamp):
        """Generate a comprehensive Markdown report."""
        report_path = output_path / f'AUDIT_REPORT_{timestamp}.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Repository Audit Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            total_files = len(self.file_data)
            python_files = len([f for f in self.file_data if f['extension'] == '.py'])
            total_todos = len(self.audit_results['todos'])
            total_placeholders = len(self.audit_results['placeholders'])
            
            f.write(f"- **Total Files:** {total_files}\n")
            f.write(f"- **Python Files:** {python_files}\n")
            f.write(f"- **Total TODOs:** {total_todos}\n")
            f.write(f"- **Total Placeholders:** {total_placeholders}\n")
            f.write(f"- **Documentation Files:** {len(self.audit_results['documentation'])}\n")
            f.write(f"- **Test Files:** {len(self.audit_results['tests'])}\n\n")
            
            # Repository Structure
            f.write("## Repository Structure\n\n")
            f.write("### Directory Overview\n\n")
            
            # Group files by directory
            dirs = defaultdict(list)
            for file_info in self.file_data:
                dirs[file_info['directory']].append(file_info['name'])
            
            for dir_path in sorted(dirs.keys()):
                files = dirs[dir_path]
                f.write(f"**{dir_path or 'Root'}/** ({len(files)} files)\n")
            
            f.write("\n")
            
            # Scripts Analysis
            f.write("## Scripts Analysis\n\n")
            
            # Group by directory
            agents_scripts = defaultdict(list)
            helpers_scripts = []
            docs_scripts = []
            root_scripts = []
            
            for analysis in self.audit_results['scripts_analysis']:
                path = analysis['path']
                if 'Agents' in path:
                    agent_dir = path.split('/')[1] if '/' in path else 'Agents'
                    agents_scripts[agent_dir].append(analysis)
                elif 'helpers' in path:
                    helpers_scripts.append(analysis)
                elif 'docs' in path:
                    docs_scripts.append(analysis)
                else:
                    root_scripts.append(analysis)
            
            # Agents Scripts
            f.write("### Agents Directory\n\n")
            for agent_dir in sorted(agents_scripts.keys()):
                f.write(f"#### {agent_dir}\n\n")
                for script in agents_scripts[agent_dir]:
                    self.write_script_details(f, script)
            
            # Helpers Scripts
            if helpers_scripts:
                f.write("### Helpers Directory\n\n")
                for script in helpers_scripts:
                    self.write_script_details(f, script)
            
            # Docs Scripts
            if docs_scripts:
                f.write("### Docs Directory\n\n")
                for script in docs_scripts:
                    self.write_script_details(f, script)
            
            # Root Scripts
            if root_scripts:
                f.write("### Root Level Scripts\n\n")
                for script in root_scripts:
                    self.write_script_details(f, script)
            
            # TODOs Section
            f.write("\n## TODOs and Action Items\n\n")
            if self.audit_results['todos']:
                f.write("| File | TODO Item |\n")
                f.write("|------|----------|\n")
                for todo in self.audit_results['todos']:
                    f.write(f"| {todo['file']} | {todo['todo']} |\n")
            else:
                f.write("✓ No TODOs found.\n")
            
            f.write("\n")
            
            # Placeholders Section
            f.write("## Placeholders\n\n")
            if self.audit_results['placeholders']:
                # Group by file
                placeholders_by_file = defaultdict(list)
                for placeholder in self.audit_results['placeholders']:
                    placeholders_by_file[placeholder['file']].append(placeholder['placeholder'])
                
                f.write("Files containing placeholders that need to be updated with actual requirements:\n\n")
                for file_path in sorted(placeholders_by_file.keys()):
                    f.write(f"**{file_path}**\n")
                    for placeholder in placeholders_by_file[file_path]:
                        f.write(f"  - {placeholder}\n")
                    f.write("\n")
            else:
                f.write("✓ No obvious placeholders found.\n")
            
            f.write("\n")
            
            # Documentation Coverage
            f.write("## Documentation Coverage\n\n")
            if self.audit_results['documentation']:
                f.write("| Path | Type | Size (bytes) |\n")
                f.write("|------|------|-------------|\n")
                for doc in self.audit_results['documentation']:
                    f.write(f"| {doc['path']} | {doc['type']} | {doc['size']} |\n")
            else:
                f.write("⚠ No documentation files found.\n")
            
            f.write("\n")
            
            # Test Coverage
            f.write("## Test Coverage\n\n")
            if self.audit_results['tests']:
                f.write("| Path | Name |\n")
                f.write("|------|------|\n")
                for test in self.audit_results['tests']:
                    f.write(f"| {test['path']} | {test['name']} |\n")
            else:
                f.write("⚠ No dedicated test files found.\n")
                f.write("\nNote: Helper scripts `api_testing.py` and `unit_test_runner.py` exist but no test suite is implemented.\n")
            
            f.write("\n")
            
            # Completeness Assessment
            f.write("## Completeness Assessment\n\n")
            if self.audit_results['completeness']:
                avg_score = sum(c['score'] for c in self.audit_results['completeness']) / len(self.audit_results['completeness'])
                f.write(f"**Average Completeness Score:** {avg_score:.1f}/100\n\n")
                
                # Show scripts below 50% completeness
                incomplete = [c for c in self.audit_results['completeness'] if c['score'] < 50]
                if incomplete:
                    f.write("### Scripts Requiring Attention (< 50% complete)\n\n")
                    f.write("| File | Score | Issues |\n")
                    f.write("|------|-------|--------|\n")
                    for item in sorted(incomplete, key=lambda x: x['score']):
                        issues = []
                        if not item['has_docstring']:
                            issues.append('No docstring')
                        if item['has_todos']:
                            issues.append('Has TODOs')
                        if item['has_placeholders']:
                            issues.append('Has placeholders')
                        if item['function_count'] == 0 and item['class_count'] == 0:
                            issues.append('No functions/classes')
                        
                        f.write(f"| {item['file']} | {item['score']}/100 | {', '.join(issues)} |\n")
            
            f.write("\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            f.write("### High Priority\n\n")
            if total_todos > 0:
                f.write(f"1. **Address {total_todos} TODO items** - Review and complete pending tasks\n")
            if total_placeholders > 0:
                f.write(f"2. **Replace {total_placeholders} placeholders** - Update with actual implementation\n")
            if not self.audit_results['tests']:
                f.write("3. **Implement test suite** - No dedicated tests found, create unit/integration tests\n")
            
            f.write("\n### Medium Priority\n\n")
            incomplete_count = len([c for c in self.audit_results['completeness'] if c['score'] < 50])
            if incomplete_count > 0:
                f.write(f"1. **Complete {incomplete_count} scripts** - Scripts with < 50% completeness score\n")
            
            f.write("2. **Add documentation** - Add module and function docstrings where missing\n")
            f.write("3. **Code review** - Review agent implementations for consistency\n")
            
            f.write("\n### Low Priority\n\n")
            f.write("1. **Standardize code formatting** - Apply consistent style across all modules\n")
            f.write("2. **Add type hints** - Improve code documentation with type annotations\n")
            f.write("3. **Create integration examples** - Show how agents work together\n")
            
            f.write("\n---\n\n")
            f.write("*End of Report*\n")
        
        print(f"✓ Comprehensive report saved to: {report_path}")
        return report_path
    
    def write_script_details(self, f, script):
        """Write detailed script information to the report."""
        f.write(f"##### {Path(script['path']).name}\n\n")
        f.write(f"- **Path:** `{script['path']}`\n")
        f.write(f"- **Purpose:** {script['purpose']}\n")
        f.write(f"- **Lines of Code:** {script['line_count']}\n")
        f.write(f"- **Completeness Score:** {script['completeness_score']}/100\n")
        f.write(f"- **Functions:** {len(script['functions'])}\n")
        f.write(f"- **Classes:** {len(script['classes'])}\n")
        f.write(f"- **TODOs:** {len(script['todos'])}\n")
        f.write(f"- **Placeholders:** {len(script['placeholders'])}\n")
        
        if script['docstring']:
            f.write(f"- **Has Documentation:** ✓\n")
        else:
            f.write(f"- **Has Documentation:** ✗\n")
        
        if script['has_main']:
            f.write(f"- **Executable:** ✓\n")
        
        # List functions
        if script['functions']:
            f.write(f"\n**Functions:**\n")
            for func in script['functions'][:5]:  # Show first 5
                doc_status = "✓" if func['has_docstring'] else "✗"
                f.write(f"  - `{func['name']}({', '.join(func['args'])})` {doc_status}\n")
            if len(script['functions']) > 5:
                f.write(f"  - ... and {len(script['functions']) - 5} more\n")
        
        # List classes
        if script['classes']:
            f.write(f"\n**Classes:**\n")
            for cls in script['classes']:
                doc_status = "✓" if cls['has_docstring'] else "✗"
                f.write(f"  - `{cls['name']}` {doc_status} ({len(cls['methods'])} methods)\n")
        
        f.write("\n")
    
    def run_full_audit(self):
        """Run the complete audit process."""
        print("="*60)
        print("Starting Repository Audit")
        print("="*60)
        
        self.scan_repository()
        self.analyze_all_scripts()
        self.check_documentation()
        self.check_tests()
        
        output_dir = self.repo_path / 'audits'
        report_path = self.generate_report(output_dir)
        
        print("="*60)
        print("Audit Complete!")
        print(f"Reports saved to: {output_dir}")
        print("="*60)
        
        return report_path


def main():
    """Main entry point for the audit script."""
    repo_path = Path(__file__).parent.parent
    auditor = RepositoryAuditor(repo_path)
    auditor.run_full_audit()


if __name__ == '__main__':
    main()
