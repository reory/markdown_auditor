#The goal here is a script that scans .md files for broken internal links, 
# missing image alt-text, and inconsistent heading structures.

# Run the script - python auditor.py C:\Users\Admin\Desktop\code

import os
import re
import sys
from pathlib import Path
from loguru import logger
from tqdm import tqdm

logger.remove()
logger.add(
    sys.stderr, 
    format="<blue>{time:HH:mm:ss}</blue> | <level>{level: <8}</level> | "
           "<level>{message}</level>"
)
logger.add(
    "audit_history.log",
    rotation="1MB", 
    retention="10 days"
)

def audit_markdown(directory):
    """
    Scans a directory for markdown files and audits them for common issues.
    """

    # Convert string input to a Path object for easier math
    base_path = Path(directory).resolve()
    logger.info(f" 🕵🏽 Auditing Markdown in: {base_path}")

    ignore_folders = {
        'node_modules', '.git', '.venv', 
        'env', '__pycache__', '.web', '.vscode'
    }
    
    md_files = []
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in ignore_folders]

        for file in files:
            if file.lower().endswith(".md"):
                md_files.append(Path(root) / file)

    if not md_files:
        logger.info("No markdown files found to audit.")
        return

    issues_found = []
    
    # Audit the files using tqdm. Shows the progress bar in the terminal
    for path in tqdm(
        md_files, 
        desc="Scanning Docs", 
        unit="file", 
        colour="blue"
    ):
        with open(path, 'r', encoding="utf-8") as f:
            content = f.read()

        # Regex pattern for missing alt-text and empty links
        alt_misses = len(re.findall(r'\!\[\]\(.*?\)', content))
        empty_links = len(re.findall(r'\[.*?\]\(\)', content))
                    
        if alt_misses > 0 or empty_links > 0:
            rel_path = path.relative_to(base_path)

            # Store the issue to print later so not to interrupt tqdm
            issues_found.append(
                f"File: {rel_path} | [!] Alt-Miss: {alt_misses} | "
                f"Empty-Links: {empty_links}"
            )
    # Log the results - print call left blank so logs dont squsih tqdm bar
    print()

    if issues_found:
        for issue in issues_found:
            logger.warning(issue)
    
    else:
        logger.success(" ✅ No issues found")


if __name__ == "__main__":
    # Use command line arguments or default to current directory
    target_folder = sys.argv[1] if len(sys.argv) > 1 else '.'
    audit_markdown(target_folder)

