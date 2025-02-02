#!/usr/bin/env python3

# This file is python, not Java.
# but we got enough people complaining that the repo in github showed 100% python
# that I just changed the extension to .java - I think its funny. We can replace
# this file if either a json library is added to java or someone wants to do all
# the setup to pull in a json lib.

import json
import sys

def preprocess_content(context, content):
    options = context.get("config", {}).get("preprocessor", {}).get("features", {})
    newContent = []
    skipping = False
    for line in content.splitlines():
        if skipping:
            if line.strip() == "~ENDIF" or line.strip() == "~ ENDIF":
                skipping = False
            elif line.strip() == "~ELSE" or line.strip() == "~ ELSE":
                skipping = False
        elif line.strip().startswith("~IF ") or line.strip().startswith("~ IF "):
            if not options.get(line.split(" ", 2)[1].strip(), False):
                skipping = True
        elif line.strip() == "~ENDIF" or line.strip() == "~ ENDIF":
            continue
        elif line.strip() == "~ELSE" or line.strip() == "~ ELSE":
            skipping = True
            continue
        else:
            if options.get("simple_io", False) and options.get("toplevel_anonymous_class", False):
                newContent.append(line.replace("System.out.println", "printLine").replace("System.out.print", "print"))
            else:
                newContent.append(line)
        
    return "\n".join(newContent)

def preprocess_section(context, section):
    if "Chapter" in section:
        section["Chapter"]["content"] = \
            preprocess_content(context, section["Chapter"]["content"])
        for sub_section in section["Chapter"].get("sub_items", []):
            preprocess_section(context, sub_section)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "supports":
            sys.exit(0)

    json_input = json.load(sys.stdin)
    context, book = json_input
    
    with open("out.json", "w") as f:
        json.dump(json_input, f)

    for section in book["sections"]:
        preprocess_section(context, section)

    print(json.dumps(book))
