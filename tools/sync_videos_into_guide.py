#!/usr/bin/env python3
"""
sync_videos_into_guide.py
Embeds LEARNING_VIDEOS.md into the guide as an in-page section, replacing any
previously embedded copy. Keeps a single source of truth for the video catalog.

Usage: python3 tools/sync_videos_into_guide.py
"""
import re
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDE = os.path.join(REPO, 'CVS_Health100_GenAI_TechDeepDive.md')
VIDEOS = os.path.join(REPO, 'LEARNING_VIDEOS.md')
MARKER = '## 🎥 Learning Videos & Courses'
REPO_BASE = 'https://github.com/naramsettisiva/genAIPrepration/tree/main/'


def demote_and_absolutize(text):
    """Demote headings one level and make relative repo links absolute."""
    out, in_code = [], False
    for ln in text.split('\n'):
        if ln.strip().startswith('```'):
            in_code = not in_code
        if not in_code and ln.startswith('#'):
            ln = '#' + ln
        out.append(ln)
    body = '\n'.join(out)

    # Relative repo paths -> absolute GitHub URLs
    body = re.sub(r'\]\((labs/[^)]*|aws_solutions/[^)]*)\)',
                  lambda m: f']({REPO_BASE}{m.group(1)})', body)
    return body


def main():
    guide = open(GUIDE).read()
    videos = open(VIDEOS).read()

    embed = demote_and_absolutize(videos).strip()

    if MARKER in guide:
        # Replace existing embedded section (marker -> end of file)
        head = guide.split(MARKER)[0].rstrip()
        guide = head + '\n\n' + embed + '\n'
        action = 'replaced'
    else:
        guide = guide.rstrip() + '\n\n---\n\n' + embed + '\n'
        action = 'appended'

    open(GUIDE, 'w').write(guide)
    print(f"✅ {action} embedded video section ({len(embed.splitlines())} lines)")
    print(f"   guide is now {len(guide.splitlines())} lines")


if __name__ == '__main__':
    main()
