import os
import glob

def generate_index():
    # Find all html and pdf reports, and logs
    files = []
    files.extend(glob.glob("AutomationReport_*.html"))
    files.extend(glob.glob("AutomationReport_*.pdf"))
    files.extend(glob.glob("ExecutionLog_*.log"))
    
    # Sort files so newest are generally grouped
    files.sort(reverse=True)
    
    # Generate the list items
    list_items = ""
    for file in files:
        if file.endswith(".html"):
            label = f"View HTML report ({file})"
        elif file.endswith(".pdf"):
            label = f"Download PDF report ({file})"
        else:
            label = f"View execution log ({file})"
            
        list_items += f'        <li><a href="{file}">{label}</a></li>\n'

    # The HTML template
    html_content = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Automation Reports</title>
    <style>
      body {{
        font-family: Arial, sans-serif;
        line-height: 1.5;
        margin: 0;
        padding: 32px;
        color: #1f2933;
        background: #f7f9fb;
      }}

      main {{
        max-width: 840px;
        margin: 0 auto;
      }}

      h1 {{
        margin: 0 0 24px;
      }}

      ul {{
        list-style: none;
        padding: 0;
        margin: 0;
      }}

      li {{
        margin: 12px 0;
      }}

      a {{
        color: #0067b8;
        font-size: 18px;
        text-decoration: none;
      }}

      a:hover {{
        text-decoration: underline;
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>Automation Reports</h1>
      <ul>
{list_items}      </ul>
    </main>
  </body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("index.html has been successfully generated with all current reports!")

if __name__ == "__main__":
    generate_index()
