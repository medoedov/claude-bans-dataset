"""Search public GitHub issue threads for self-reports by Claude users."""
from pathlib import Path
import json
import sys
import time
import requests

queries=['repo:anthropics/claude-code is:issue Russia suspended','repo:anthropics/claude-code is:issue Russia verification','repo:anthropics/claude-code is:issue Russia billing','repo:anthropics/claude-code is:issue Russia VPN subscription','is:issue "Russian passport" "Claude"','is:issue "российский паспорт" "Claude"','repo:anthropics/claude-code is:issue "Russian citizen"','repo:anthropics/claude-code is:issue "Moscow" account suspended']


if __name__=="__main__":
    tmp=Path(sys.argv[1])
    hits={}
    coverage={}
    with requests.Session() as s:
        for q in queries:
            resp=s.get("https://api.github.com/search/issues",params={"q":q,"per_page":100},timeout=20)
            if resp.ok:
                data=resp.json()
                coverage[q]=data["total_count"]
                for item in data["items"]:
                    hits[item["html_url"]]={"url":item["html_url"],"date":item["created_at"][:10],
                                            "title":item["title"],"text":item["body"] or "","comments":item["comments_url"],"count":item["comments"]}
            else:
                coverage[q]=resp.status_code
            time.sleep(2)
    (tmp/"github-hits.json").write_text(json.dumps(list(hits.values()),ensure_ascii=False),encoding="utf-8")
    (tmp/"github-coverage.json").write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding="utf-8")
    print(coverage)
