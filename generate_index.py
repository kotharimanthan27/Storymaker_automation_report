import os
import glob
import re
import json

def parse_filename(filename):
    name, ext = os.path.splitext(filename)
    if name.startswith("AutomationReport_"):
        base = name[len("AutomationReport_"):]
    elif name.startswith("ExecutionLog_"):
        base = name[len("ExecutionLog_"):]
    else:
        base = name
        
    # Pattern: optional prefix followed by YYYYMMDD_HHMMSS
    match = re.match(r"^(.*?)_?(\d{8})_(\d{6})$", base)
    if match:
        prefix = match.group(1)
        date_str = match.group(2)
        time_str = match.group(3)
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        formatted_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
        return {
            "key": base,
            "prefix": prefix.strip("_") if prefix else "General",
            "date": formatted_date,
            "time": formatted_time,
            "timestamp": f"{date_str}_{time_str}"
        }
    return {
        "key": base,
        "prefix": "General",
        "date": "Unknown Date",
        "time": "Unknown Time",
        "timestamp": "00000000_000000"
    }

def generate_index():
    # Find all html, pdf reports, and logs
    html_files = glob.glob("AutomationReport_*.html")
    pdf_files = glob.glob("AutomationReport_*.pdf")
    log_files = glob.glob("ExecutionLog_*.log")
    
    # Group by base key
    reports = {}
    
    for f in html_files:
        info = parse_filename(f)
        key = info["key"]
        if key not in reports:
            reports[key] = {**info, "html": None, "pdf": None, "log": None}
        reports[key]["html"] = f

    for f in pdf_files:
        info = parse_filename(f)
        key = info["key"]
        if key not in reports:
            reports[key] = {**info, "html": None, "pdf": None, "log": None}
        reports[key]["pdf"] = f

    for f in log_files:
        info = parse_filename(f)
        key = info["key"]
        if key not in reports:
            reports[key] = {**info, "html": None, "pdf": None, "log": None}
        reports[key]["log"] = f

    # Sort reports by timestamp descending (newest first)
    sorted_keys = sorted(reports.keys(), key=lambda k: reports[k]["timestamp"], reverse=True)
    
    # Generate list items and collect unique categories for filtering
    categories = set()
    cards_html = ""
    
    for key in sorted_keys:
        rep = reports[key]
        category = rep["prefix"]
        categories.add(category)
        
        # Determine category badge class
        cat_lower = category.lower()
        badge_class = "badge-general"
        if "prod" in cat_lower:
            badge_class = "badge-prod"
        elif "beta" in cat_lower:
            badge_class = "badge-beta"
        elif "storymaker" in cat_lower:
            badge_class = "badge-storymaker"
            
        # Build action links
        links = []
        if rep["html"]:
            links.append(f'<a href="{rep["html"]}" class="btn btn-html" target="_blank">HTML Report</a>')
        else:
            links.append('<span class="btn btn-disabled">No HTML</span>')
            
        if rep["pdf"]:
            links.append(f'<a href="{rep["pdf"]}" class="btn btn-pdf" download>PDF Report</a>')
        else:
            links.append('<span class="btn btn-disabled">No PDF</span>')
            
        if rep["log"]:
            links.append(f'<a href="{rep["log"]}" class="btn btn-log" target="_blank">View Log</a>')
        else:
            links.append('<span class="btn btn-disabled">No Log</span>')
            
        links_str = "\n            ".join(links)
        
        cards_html += f"""
        <div class="report-card" data-category="{category}" data-search="{key.lower()}">
          <div class="card-header">
            <span class="badge {badge_class}">{category}</span>
            <span class="report-date">{rep["date"]} &middot; {rep["time"]}</span>
          </div>
          <h3 class="report-name">{key}</h3>
          <div class="card-actions">
            {links_str}
          </div>
        </div>"""

    # Generate category filter buttons
    filter_buttons = '<button class="filter-btn active" data-filter="all">All Reports</button>'
    for cat in sorted(list(categories)):
        filter_buttons += f'\n      <button class="filter-btn" data-filter="{cat}">{cat}</button>'

    # Modern Premium HTML template
    html_content = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Automation Dashboard | Storymaker Reports</title>
    <meta name="description" content="Dashboard for accessing automation reports and execution logs.">
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
      :root {{
        --bg-main: #f8fafc;
        --bg-card: #ffffff;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --border-color: #e2e8f0;
        --primary: #4f46e5;
        --primary-hover: #4338ca;
        --success: #10b981;
        --success-hover: #059669;
        --warning: #f59e0b;
        --warning-hover: #d97706;
        --disabled: #94a3b8;
        --disabled-bg: #f1f5f9;
        --font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      }}

      * {{
        box-sizing: border-box;
        margin: 0;
        padding: 0;
      }}

      body {{
        font-family: var(--font-family);
        background-color: var(--bg-main);
        color: var(--text-primary);
        line-height: 1.5;
        padding: 40px 24px;
        min-height: 100vh;
      }}

      main {{
        max-width: 1040px;
        margin: 0 auto;
      }}

      header {{
        margin-bottom: 40px;
        text-align: center;
      }}

      .header-title {{
        font-size: 36px;
        font-weight: 800;
        letter-spacing: -0.025em;
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
      }}

      .header-subtitle {{
        color: var(--text-secondary);
        font-size: 16px;
        font-weight: 500;
      }}

      /* Search and Filter Section */
      .controls {{
        display: flex;
        flex-direction: column;
        gap: 16px;
        background: var(--bg-card);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
        margin-bottom: 32px;
      }}

      .search-wrapper {{
        position: relative;
        width: 100%;
      }}

      .search-input {{
        width: 100%;
        padding: 14px 16px;
        font-family: var(--font-family);
        font-size: 15px;
        border: 1px solid var(--border-color);
        border-radius: 10px;
        background-color: #f8fafc;
        outline: none;
        transition: all 0.2s ease;
        color: var(--text-primary);
      }}

      .search-input:focus {{
        border-color: var(--primary);
        background-color: #fff;
        box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1);
      }}

      .filters-wrapper {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
      }}

      .filter-btn {{
        padding: 8px 16px;
        font-family: var(--font-family);
        font-size: 14px;
        font-weight: 600;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        background: #fff;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.2s ease;
      }}

      .filter-btn:hover {{
        border-color: #cbd5e1;
        color: var(--text-primary);
      }}

      .filter-btn.active {{
        background: var(--primary);
        border-color: var(--primary);
        color: #fff;
      }}

      /* Reports Grid */
      .reports-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 20px;
      }}

      .report-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
        display: flex;
        flex-direction: column;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }}

      .report-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
      }}

      .card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
      }}

      .badge {{
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 6px;
        letter-spacing: 0.05em;
      }}

      .badge-prod {{
        background-color: #d1fae5;
        color: #065f46;
      }}

      .badge-beta {{
        background-color: #fef3c7;
        color: #92400e;
      }}

      .badge-storymaker {{
        background-color: #ede9fe;
        color: #5b21b6;
      }}

      .badge-general {{
        background-color: #f1f5f9;
        color: #334155;
      }}

      .report-date {{
        font-size: 13px;
        font-weight: 500;
        color: var(--text-secondary);
      }}

      .report-name {{
        font-size: 17px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 24px;
        flex-grow: 1;
        word-break: break-all;
        line-height: 1.4;
      }}

      .card-actions {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-top: auto;
      }}

      .btn {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 10px 8px;
        font-size: 12px;
        font-weight: 700;
        border-radius: 8px;
        text-decoration: none;
        transition: all 0.2s ease;
        text-align: center;
        border: none;
        cursor: pointer;
      }}

      .btn-html {{
        background-color: var(--primary);
        color: #fff;
      }}

      .btn-html:hover {{
        background-color: var(--primary-hover);
      }}

      .btn-pdf {{
        background-color: var(--success);
        color: #fff;
      }}

      .btn-pdf:hover {{
        background-color: var(--success-hover);
      }}

      .btn-log {{
        background-color: #f1f5f9;
        color: var(--text-secondary);
        border: 1px solid var(--border-color);
      }}

      .btn-log:hover {{
        background-color: #e2e8f0;
        color: var(--text-primary);
      }}

      .btn-disabled {{
        background-color: var(--disabled-bg);
        color: var(--disabled);
        cursor: not-allowed;
      }}

      /* Empty State */
      .empty-state {{
        grid-column: 1 / -1;
        text-align: center;
        padding: 48px 24px;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        display: none;
      }}

      .empty-state h4 {{
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 8px;
      }}

      .empty-state p {{
        font-size: 14px;
        color: var(--text-secondary);
      }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <h1 class="header-title">Storymaker Reports</h1>
        <p class="header-subtitle">Access your latest automation test runs, pdf reports, and execution logs</p>
      </header>

      <section class="controls">
        <div class="search-wrapper">
          <input type="text" id="search-input" class="search-input" placeholder="Search reports by filename or tag...">
        </div>
        <div class="filters-wrapper">
          {filter_buttons}
        </div>
      </section>

      <section class="reports-grid" id="reports-grid">
        {cards_html}
        <div class="empty-state" id="empty-state">
          <h4>No Reports Found</h4>
          <p>Try adjusting your search query or category filter</p>
        </div>
      </section>
    </main>

    <script>
      const searchInput = document.getElementById('search-input');
      const filterButtons = document.querySelectorAll('.filter-btn');
      const reportCards = document.querySelectorAll('.report-card');
      const emptyState = document.getElementById('empty-state');

      let activeFilter = 'all';
      let searchQuery = '';

      function filterReports() {{
        let visibleCount = 0;
        
        reportCards.forEach(card => {{
          const cardCategory = card.getAttribute('data-category');
          const cardSearch = card.getAttribute('data-search');
          
          const matchesFilter = (activeFilter === 'all' || cardCategory === activeFilter);
          const matchesSearch = cardSearch.includes(searchQuery);

          if (matchesFilter && matchesSearch) {{
            card.style.display = 'flex';
            visibleCount++;
          }} else {{
            card.style.display = 'none';
          }}
        }});

        if (visibleCount === 0) {{
          emptyState.style.display = 'block';
        }} else {{
          emptyState.style.display = 'none';
        }}
      }}

      searchInput.addEventListener('input', (e) => {{
        searchQuery = e.target.value.toLowerCase().trim();
        filterReports();
      }});

      filterButtons.forEach(btn => {{
        btn.addEventListener('click', () => {{
          filterButtons.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          activeFilter = btn.getAttribute('data-filter');
          filterReports();
        }});
      }});
    </script>
  </body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("index.html has been successfully generated with all current reports!")

if __name__ == "__main__":
    generate_index()
