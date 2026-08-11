import urllib.request
import json
import re
import datetime
import os

USERNAME = "Algorift169"
README_PATH = os.path.join(os.path.dirname(__file__), "../../README.md")

def fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Python-GitHub-Readme-Updater", "Accept": "application/vnd.github.v3+json"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_recent_activity():
    events_url = f"https://api.github.com/users/{USERNAME}/events/public"
    repos_url = f"https://api.github.com/users/{USERNAME}/repos?sort=pushed&per_page=10"
    
    events = fetch_json(events_url) or []
    repos = fetch_json(repos_url) or []
    
    latest_commit_msg = None
    latest_commit_repo = None
    latest_commit_url = None
    latest_commit_time = None

    for ev in events:
        if ev.get("type") == "PushEvent":
            payload = ev.get("payload", {})
            commits = payload.get("commits", [])
            if commits:
                latest_commit = commits[-1]
                latest_commit_msg = latest_commit.get("message", "").split("\n")[0]
                repo_name = ev.get("repo", {}).get("name", "").split("/")[-1]
                latest_commit_repo = repo_name
                latest_commit_url = f"https://github.com/{ev.get('repo', {}).get('name')}"
                latest_commit_time = ev.get("created_at")
                break

    active_repos = []
    for r in repos:
        name = r.get("name")
        if name and name.lower() != USERNAME.lower():
            desc = r.get("description") or "No description provided."
            url = r.get("html_url")
            lang = r.get("language") or "Code"
            stars = r.get("stargazers_count", 0)
            active_repos.append({
                "name": name,
                "url": url,
                "description": desc,
                "language": lang,
                "stars": stars
            })
        if len(active_repos) >= 4:
            break

    return {
        "latest_commit_msg": latest_commit_msg,
        "latest_commit_repo": latest_commit_repo,
        "latest_commit_url": latest_commit_url,
        "latest_commit_time": latest_commit_time,
        "active_repos": active_repos
    }

def format_dynamic_section(data):
    lines = []
    lines.append("<div align=\"center\">")
    lines.append("  <table>")
    lines.append("    <tr>")
    lines.append("      <td width=\"50%\" valign=\"top\">")
    lines.append("        <h4 align=\"center\">🔨 Currently Working On</h4>")
    
    if data["latest_commit_repo"] and data["latest_commit_msg"]:
        repo = data["latest_commit_repo"]
        url = data["latest_commit_url"]
        msg = data["latest_commit_msg"]
        lines.append(f"        <p><b>Active Repository:</b> <a href=\"{url}\"><b>{repo}</b></a></p>")
        lines.append(f"        <p><b>Latest Commit:</b> <code>{msg}</code></p>")
    elif data["active_repos"]:
        top_repo = data["active_repos"][0]
        lines.append(f"        <p><b>Active Repository:</b> <a href=\"{top_repo['url']}\"><b>{top_repo['name']}</b></a></p>")
        lines.append(f"        <p><i>{top_repo['description']}</i></p>")
    else:
        lines.append("        <p>Building open-source software and linux utilities.</p>")
        
    lines.append("      </td>")
    lines.append("      <td width=\"50%\" valign=\"top\">")
    lines.append("        <h4 align=\"center\">🚀 Recent Projects</h4>")
    lines.append("        <ul>")
    for r in data["active_repos"][:3]:
        lines.append(f"          <li><a href=\"{r['url']}\"><b>{r['name']}</b></a> - {r['description']} (<code>{r['language']}</code>)</li>")
    lines.append("        </ul>")
    lines.append("      </td>")
    lines.append("    </tr>")
    lines.append("  </table>")
    lines.append("</div>")
    lines.append("")
    lines.append(f"*(⚡ Automatically updated via GitHub Actions)*")
    
    return "\n".join(lines)

def update_readme():
    if not os.path.exists(README_PATH):
        print(f"File not found: {README_PATH}")
        return

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "<!-- RECENT_WORK_START -->"
    end_marker = "<!-- RECENT_WORK_END -->"

    if start_marker not in content or end_marker not in content:
        print("Markers not found in README.md")
        return

    data = get_recent_activity()
    dynamic_md = format_dynamic_section(data)

    pattern = re.compile(rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
    new_content = pattern.sub(f"{start_marker}\n{dynamic_md}\n{end_marker}", content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("README.md updated successfully with dynamic content!")

if __name__ == "__main__":
    update_readme()
