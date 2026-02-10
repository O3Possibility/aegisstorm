#!/usr/bin/env python3
"""
Generate HTML dashboard from constraint analysis
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import glob

def load_latest_analysis():
    """Load most recent constraint analysis"""
    constraint_dir = Path("data/constraints")
    
    if not constraint_dir.exists():
        return None
    
    # Get all analysis files
    files = sorted(constraint_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not files:
        return None
    
    with open(files[0]) as f:
        return json.load(f)

def generate_html(analysis):
    """Generate HTML dashboard"""
    
    if not analysis:
        html = generate_no_storms_html()
    else:
        html = generate_storm_dashboard_html(analysis)
    
    # Save to docs/ for GitHub Pages
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    with open(docs_dir / "index.html", 'w') as f:
        f.write(html)
    
    print(f"✓ Dashboard generated: docs/index.html")

def generate_no_storms_html():
    """HTML for no active storms"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hurricane Constraint Tracker</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .no-storms {
            background: white;
            padding: 40px;
            border-radius: 10px;
            text-align: center;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌀 Hurricane Constraint Tracker</h1>
        <p>Constraint-aware diagnostic analysis for Atlantic hurricanes</p>
    </div>
    
    <div class="no-storms">
        <h2>No Active Storms</h2>
        <p>No storms currently in watch zone (East Texas to Maine, within 300nm)</p>
        <p>System checks every 6 hours for new activity</p>
        <p><strong>Last check:</strong> """ + datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC') + """</p>
    </div>
    
    <div class="footer">
        <p>Data from NOAA National Hurricane Center | Constraint analysis experimental</p>
        <p>For official forecasts visit <a href="https://www.nhc.noaa.gov">nhc.noaa.gov</a></p>
    </div>
</body>
</html>"""

def generate_storm_dashboard_html(analysis):
    """Generate dashboard HTML for active storm"""
    
    storm_name = analysis['storm_name']
    nhc = analysis['nhc_advisory']
    constraints = analysis['constraints']
    insight = analysis['diagnostic_insight']
    
    # Format refusal risk with color
    risk_colors = {
        'LOW': '#28a745',
        'MODERATE': '#ffc107',
        'HIGH': '#fd7e14',
        'CRITICAL': '#dc3545'
    }
    risk_color = risk_colors.get(constraints['refusal_risk'], '#666')
    
    # Format regime
    regime = constraints['regime'].replace('_', ' ').title()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tracking: {storm_name} | Hurricane Constraint Tracker</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .header .subtitle {{
            opacity: 0.9;
            margin: 0;
        }}
        .card {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .card h2 {{
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .metric-label {{
            font-size: 0.85em;
            color: #666;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}
        .constraint-bars {{
            margin: 20px 0;
        }}
        .constraint-bar {{
            margin-bottom: 15px;
        }}
        .constraint-label {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 0.9em;
        }}
        .bar-container {{
            height: 30px;
            background: #e9ecef;
            border-radius: 5px;
            overflow: hidden;
        }}
        .bar-fill {{
            height: 100%;
            border-radius: 5px;
            transition: width 0.3s ease;
        }}
        .bar-I {{ background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); }}
        .bar-R {{ background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%); }}
        .bar-S {{ background: linear-gradient(90deg, #fa709a 0%, #fee140 100%); }}
        .bar-L {{ background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); }}
        .insight-box {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        .insight-box.critical {{
            background: #f8d7da;
            border-color: #dc3545;
        }}
        .regime-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            background: #667eea;
            color: white;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
        .timestamp {{
            font-size: 0.85em;
            color: #666;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌀 Tracking: {storm_name}</h1>
        <p class="subtitle">Constraint-aware diagnostic analysis</p>
    </div>
    
    <!-- NHC Advisory -->
    <div class="card">
        <h2>📊 NHC Advisory #{nhc['advisory_number']}</h2>
        <p><strong>{insight['nhc_summary']}</strong></p>
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Intensity</div>
                <div class="metric-value">{nhc['intensity_kt']:.0f} kt</div>
            </div>
            <div class="metric">
                <div class="metric-label">Pressure</div>
                <div class="metric-value">{nhc['pressure_mb']:.0f} mb</div>
            </div>
            <div class="metric">
                <div class="metric-label">Position</div>
                <div class="metric-value">{nhc['position']['lat']:.1f}°N, {abs(nhc['position']['lon']):.1f}°W</div>
            </div>
            <div class="metric">
                <div class="metric-label">Movement</div>
                <div class="metric-value">{nhc['movement']}</div>
            </div>
        </div>
        <div class="timestamp">Advisory time: {nhc['advisory_time'][:16].replace('T', ' ')} UTC</div>
    </div>
    
    <!-- Constraint Analysis -->
    <div class="card">
        <h2>🔬 Constraint Analysis</h2>
        <p><strong>{insight['constraint_summary']}</strong></p>
        
        <div class="constraint-bars">
            <div class="constraint-bar">
                <div class="constraint-label">
                    <span><strong>I</strong> (Thermodynamic Headroom)</span>
                    <span>{constraints['indicative_I']:.2f}</span>
                </div>
                <div class="bar-container">
                    <div class="bar-fill bar-I" style="width: {constraints['indicative_I']*100:.0f}%"></div>
                </div>
            </div>
            
            <div class="constraint-bar">
                <div class="constraint-label">
                    <span><strong>R</strong> (Environmental Favorability)</span>
                    <span>{constraints['relational_R']:.2f}</span>
                </div>
                <div class="bar-container">
                    <div class="bar-fill bar-R" style="width: {constraints['relational_R']*100:.0f}%"></div>
                </div>
            </div>
            
            <div class="constraint-bar">
                <div class="constraint-label">
                    <span><strong>S</strong> (Structural Coherence)</span>
                    <span>{constraints['semantic_S']:.2f}</span>
                </div>
                <div class="bar-container">
                    <div class="bar-fill bar-S" style="width: {constraints['semantic_S']*100:.0f}%"></div>
                </div>
            </div>
            
            <div class="constraint-bar">
                <div class="constraint-label">
                    <span><strong>L</strong> (Admissibility = I × R × S)</span>
                    <span>{constraints['admissibility_L']:.2f}</span>
                </div>
                <div class="bar-container">
                    <div class="bar-fill bar-L" style="width: {constraints['admissibility_L']*100:.0f}%"></div>
                </div>
            </div>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Refusal Risk</div>
                <div class="metric-value" style="color: {risk_color}">{constraints['refusal_risk']}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Regime</div>
                <div class="metric-value" style="font-size: 1.1em"><span class="regime-badge">{regime}</span></div>
            </div>
            <div class="metric">
                <div class="metric-label">Gradient Hazard</div>
                <div class="metric-value">{'⚠️ YES' if constraints['gradient_hazard'] else '✓ NO'}</div>
            </div>
            <div class="metric">
                <div class="metric-label">At % of Ceiling</div>
                <div class="metric-value">{insight['thermodynamic_ceiling_pct']:.0f}%</div>
            </div>
        </div>
    </div>
    
    <!-- Diagnostic Insight -->
    <div class="card">
        <h2>💡 Diagnostic Insight</h2>
        <div class="insight-box {'critical' if constraints['refusal_risk'] in ['HIGH', 'CRITICAL'] else ''}">
            <p><strong>Key Observation:</strong></p>
            <p>{insight['comparative_insight']}</p>
        </div>
        
        <p><strong>Forecast Implication:</strong></p>
        <p>{insight['forecast_implication']}</p>
        
        {f'<p><strong>Estimated Time to Peak:</strong> {insight["time_to_peak_estimate"]}</p>' if insight['time_to_peak_estimate'] else ''}
        
        <p><strong>Structural Trend:</strong> {insight['structural_trend'].capitalize()}</p>
        
        <div class="metrics" style="margin-top: 20px">
            <div class="metric">
                <div class="metric-label">Analysis Confidence</div>
                <div class="metric-value">{insight['confidence']:.0%}</div>
            </div>
        </div>
    </div>
    
    <!-- Environmental Context -->
    <div class="card">
        <h2>🌊 Environmental Context</h2>
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Sea Surface Temp</div>
                <div class="metric-value">{analysis['environmental']['sst_celsius']:.1f}°C</div>
            </div>
            <div class="metric">
                <div class="metric-label">Wind Shear</div>
                <div class="metric-value">{analysis['environmental']['wind_shear_kt']:.0f} kt</div>
            </div>
            <div class="metric">
                <div class="metric-label">Potential Intensity</div>
                <div class="metric-value">{analysis['environmental']['potential_intensity_kt']:.0f} kt</div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p><strong>⚠️ Experimental Analysis</strong></p>
        <p>This constraint-based diagnostic analysis is experimental and should not be used for decision-making.</p>
        <p>For official forecasts, visit <a href="https://www.nhc.noaa.gov" target="_blank">NOAA National Hurricane Center</a></p>
        <p style="margin-top: 20px; font-size: 0.85em">
            Analysis generated: {analysis['timestamp'][:16].replace('T', ' ')} UTC<br>
            Updates every 6 hours automatically
        </p>
    </div>
</body>
</html>"""
    
    return html

def main():
    """Main execution"""
    print("Generating dashboard...")
    
    # Load latest analysis
    analysis = load_latest_analysis()
    
    # Generate HTML
    generate_html(analysis)
    
    print("✓ Dashboard generation complete")

if __name__ == "__main__":
    main()
