#!/usr/bin/env python3
"""
DroxAI Code Generation Agent - Web UI

A simple web interface for the code generation agent.
Run with: python web_ui.py

Then open http://localhost:8000 in your browser.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading

from agent import CodeGenerationAgent, UnlimitedCodeAgent


class CodeGenRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the web UI."""
    
    # Class variables for agent
    agent = CodeGenerationAgent()
    unlimited_agent = UnlimitedCodeAgent()
    
    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == '/' or self.path == '/index.html':
            self.serve_html()
        elif self.path == '/api/agents':
            self.send_json({'agents': ['standard', 'unlimited']})
        else:
            self.send_404()
    
    def do_POST(self) -> None:
        """Handle POST requests."""
        if self.path == '/api/generate':
            self.handle_generate()
        elif self.path == '/api/analyze':
            self.handle_analyze()
        elif self.path == '/api/benchmark':
            self.handle_benchmark()
        else:
            self.send_404()
    
    def handle_generate(self) -> None:
        """Handle code generation request."""
        try:
            # Parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            requirement = data.get('requirement', '')
            use_unlimited = data.get('unlimited', False)
            
            if not requirement:
                self.send_json({'error': 'Requirement is required'}, 400)
                return
            
            # Choose agent
            agent = self.unlimited_agent if use_unlimited else self.agent
            
            # Analyze
            analysis = agent.analyze_requirements(requirement)
            
            # Generate
            code = agent.generate_code(requirement)
            
            # Validate
            validation = agent._validate_code(code)
            
            # Response
            response = {
                'success': True,
                'code': code,
                'analysis': {
                    'complexity_score': analysis['complexity_score'],
                    'code_type': analysis['code_type'],
                    'architecture': analysis['architecture'],
                },
                'validation': {
                    'valid': validation['valid'],
                    'errors': validation['errors'],
                },
                'stats': {
                    'code_length': len(code),
                    'lines': len(code.split('\n')),
                }
            }
            
            self.send_json(response)
            
        except json.JSONDecodeError:
            self.send_json({'error': 'Invalid JSON'}, 400)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_analyze(self) -> None:
        """Handle requirement analysis request."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            requirement = data.get('requirement', '')
            
            if not requirement:
                self.send_json({'error': 'Requirement is required'}, 400)
                return
            
            # Analyze
            analysis = self.agent.analyze_requirements(requirement)
            
            response = {
                'success': True,
                'analysis': analysis
            }
            
            self.send_json(response)
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_benchmark(self) -> None:
        """Handle benchmark request."""
        try:
            test_cases = [
                ("Simple", "Create a function that adds two numbers"),
                ("Medium", "Create a class for data processing with file I/O"),
                ("Complex", "Build a web API with authentication and database"),
            ]
            
            results = []
            
            for name, requirement in test_cases:
                analysis = self.agent.analyze_requirements(requirement)
                code = self.agent.generate_code(requirement)
                validation = self.agent._validate_code(code)
                
                score = (analysis['complexity_score'] * 0.35 + 
                        min(len(code) / 200, 100) * 0.25 + 
                        (100 if validation['valid'] else 0) * 0.20 +
                        100 * 0.20)
                
                results.append({
                    'name': name,
                    'complexity': analysis['complexity_score'],
                    'code_length': len(code),
                    'valid': validation['valid'],
                    'score': score
                })
            
            avg_score = sum(r['score'] for r in results) / len(results)
            
            response = {
                'success': True,
                'results': results,
                'average_score': avg_score
            }
            
            self.send_json(response)
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def serve_html(self) -> None:
        """Serve the HTML interface."""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DroxAI Code Generation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #1e3c72;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #1e3c72;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
        }
        
        textarea, input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-family: monospace;
            font-size: 0.9em;
        }
        
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        textarea:focus, input:focus {
            outline: none;
            border-color: #2a5298;
            box-shadow: 0 0 0 3px rgba(42,82,152,0.1);
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        input[type="checkbox"] {
            width: auto;
        }
        
        button {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #2a5298;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .output {
            background: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .stat-box {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            border-left: 4px solid #2a5298;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .stat-value {
            color: #1e3c72;
            font-weight: bold;
            font-size: 1.3em;
        }
        
        .error {
            background: #fee;
            color: #c33;
            padding: 12px;
            border-radius: 5px;
            border-left: 4px solid #c33;
            margin-top: 10px;
        }
        
        .success {
            background: #efe;
            color: #3c3;
            padding: 12px;
            border-radius: 5px;
            border-left: 4px solid #3c3;
            margin-top: 10px;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 DroxAI Code Generation</h1>
            <p>Generate production-ready code from natural language requirements</p>
        </div>
        
        <div class="main-content">
            <!-- Input Card -->
            <div class="card">
                <h2>Generate Code</h2>
                <form id="generateForm">
                    <div class="form-group">
                        <label for="requirement">Requirements:</label>
                        <textarea id="requirement" placeholder="E.g., Create a REST API with authentication and database integration..." required></textarea>
                    </div>
                    
                    <div class="form-group checkbox-group">
                        <input type="checkbox" id="unlimited">
                        <label for="unlimited">Use Unlimited Agent (larger code)</label>
                    </div>
                    
                    <button type="button" onclick="generateCode()">Generate Code</button>
                    <button type="button" onclick="analyzeOnly()" style="background: #666; margin-left: 10px;">Analyze Only</button>
                    <button type="button" onclick="runBenchmark()" style="background: #2a8800; margin-left: 10px;">Run Benchmark</button>
                    
                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        <p>Generating... this may take a moment</p>
                    </div>
                </form>
            </div>
            
            <!-- Output Card -->
            <div class="card">
                <h2>Generated Code</h2>
                <div id="output" style="display: none;">
                    <div class="output" id="codeOutput"></div>
                    <div class="stats" id="stats"></div>
                </div>
                <div id="noOutput" style="color: #999; text-align: center; padding: 40px;">
                    Generated code will appear here
                </div>
            </div>
        </div>
        
        <!-- Analysis Card (full width) -->
        <div class="card">
            <h2>Analysis & Benchmark Results</h2>
            <div id="analysis" style="display: none;">
                <div id="analysisOutput"></div>
            </div>
            <div id="noAnalysis" style="color: #999; text-align: center; padding: 40px;">
                Analysis results will appear here
            </div>
        </div>
    </div>
    
    <script>
        async function generateCode() {
            const requirement = document.getElementById('requirement').value.trim();
            const unlimited = document.getElementById('unlimited').checked;
            
            if (!requirement) {
                alert('Please enter a requirement');
                return;
            }
            
            showLoading();
            hideAnalysis();
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({requirement, unlimited})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayCode(data);
                } else {
                    showError(data.error);
                }
            } catch (error) {
                showError('Error generating code: ' + error.message);
            } finally {
                hideLoading();
            }
        }
        
        async function analyzeOnly() {
            const requirement = document.getElementById('requirement').value.trim();
            
            if (!requirement) {
                alert('Please enter a requirement');
                return;
            }
            
            showLoading();
            hideOutput();
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({requirement})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayAnalysis(data.analysis);
                } else {
                    showError(data.error);
                }
            } catch (error) {
                showError('Error analyzing: ' + error.message);
            } finally {
                hideLoading();
            }
        }
        
        async function runBenchmark() {
            showLoading();
            hideOutput();
            hideAnalysis();
            
            try {
                const response = await fetch('/api/benchmark', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayBenchmark(data);
                } else {
                    showError(data.error);
                }
            } catch (error) {
                showError('Error running benchmark: ' + error.message);
            } finally {
                hideLoading();
            }
        }
        
        function displayCode(data) {
            document.getElementById('codeOutput').textContent = data.code;
            document.getElementById('stats').innerHTML = `
                <div class="stat-box">
                    <div class="stat-label">Complexity</div>
                    <div class="stat-value">${data.analysis.complexity_score}/100</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Code Length</div>
                    <div class="stat-value">${data.stats.code_length.toLocaleString()}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Lines</div>
                    <div class="stat-value">${data.stats.lines}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Valid</div>
                    <div class="stat-value">${data.validation.valid ? '✓' : '✗'}</div>
                </div>
            `;
            document.getElementById('output').style.display = 'block';
            document.getElementById('noOutput').style.display = 'none';
        }
        
        function displayAnalysis(analysis) {
            let html = '<table style="width: 100%; border-collapse: collapse;">';
            for (const [key, value] of Object.entries(analysis)) {
                html += `<tr style="border-bottom: 1px solid #ddd;"><td style="padding: 10px; font-weight: bold;">${key}:</td><td style="padding: 10px;">${JSON.stringify(value)}</td></tr>`;
            }
            html += '</table>';
            document.getElementById('analysisOutput').innerHTML = html;
            document.getElementById('analysis').style.display = 'block';
            document.getElementById('noAnalysis').style.display = 'none';
        }
        
        function displayBenchmark(data) {
            let html = '<table style="width: 100%; border-collapse: collapse;">';
            html += '<tr style="background: #f5f5f5;"><th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Test</th><th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Complexity</th><th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Code Len</th><th style="padding: 10px; text-align: center; border-bottom: 2px solid #ddd;">Valid</th><th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Score</th></tr>';
            
            for (const result of data.results) {
                html += `<tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 10px;">${result.name}</td>
                    <td style="padding: 10px; text-align: right;">${result.complexity}/100</td>
                    <td style="padding: 10px; text-align: right;">${result.code_length.toLocaleString()}</td>
                    <td style="padding: 10px; text-align: center;">${result.valid ? '✓' : '✗'}</td>
                    <td style="padding: 10px; text-align: right; font-weight: bold;">${result.score.toFixed(2)}</td>
                </tr>`;
            }
            
            html += `<tr style="background: #f5f5f5; font-weight: bold;">
                <td style="padding: 10px;">AVERAGE</td>
                <td style="padding: 10px; text-align: right;"></td>
                <td style="padding: 10px; text-align: right;"></td>
                <td style="padding: 10px; text-align: center;"></td>
                <td style="padding: 10px; text-align: right;">${data.average_score.toFixed(2)}</td>
            </tr>`;
            
            html += '</table>';
            document.getElementById('analysisOutput').innerHTML = html;
            document.getElementById('analysis').style.display = 'block';
            document.getElementById('noAnalysis').style.display = 'none';
        }
        
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }
        
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }
        
        function hideOutput() {
            document.getElementById('output').style.display = 'none';
            document.getElementById('noOutput').style.display = 'block';
        }
        
        function hideAnalysis() {
            document.getElementById('analysis').style.display = 'none';
            document.getElementById('noAnalysis').style.display = 'block';
        }
        
        function showError(message) {
            const output = document.getElementById('codeOutput');
            output.parentElement.innerHTML = `<div class="error">${message}</div>`;
            document.getElementById('output').style.display = 'block';
            document.getElementById('noOutput').style.display = 'none';
        }
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html_content)))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_json(self, data: Dict[str, Any], status_code: int = 200) -> None:
        """Send JSON response."""
        response = json.dumps(data)
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def send_404(self) -> None:
        """Send 404 response."""
        self.send_json({'error': 'Not found'}, 404)
    
    def log_message(self, format, *args) -> None:
        """Suppress default logging."""
        pass


def main() -> None:
    """Main entry point."""
    port = 8000
    server = HTTPServer(('localhost', port), CodeGenRequestHandler)
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║          DroxAI Code Generation Agent - Web UI               ║
╚══════════════════════════════════════════════════════════════╝

🚀 Server running on http://localhost:{port}

Commands:
  - Generate Code: Enter requirements and click "Generate Code"
  - Analyze Only: Click "Analyze Only" to see requirements analysis
  - Run Benchmark: Click "Run Benchmark" to test performance

Press Ctrl+C to stop.
    """)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        server.shutdown()


if __name__ == '__main__':
    main()
