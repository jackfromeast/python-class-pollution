"""
@description
--------------------
Given the repo's source code, this script helps to classify whether 
1. Has any web interface (acceping user input from the web)
2. Has any local interface (acceping user input from the arguments or reading from files)
"""
import os
import re
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ROUTE_REGEX = {
  # Matches assignments like `route_name="..."` or `route_name='...'`
  "route_name=": r"route_name=['\"][^'\"]*['\"]",
  
  # Matches function calls like `add_route(..., "route_name")`
  "add_route": r"add_route\(.*,\s*['\"][^'\"]*['\"]",
  
  # Matches `add_handlers("...", ...)`
  "add_handlers": r"add_handlers\(r?['\"][^'\"]*['\"].*\)",
  
  # Matches decorators like `@get("...")`, `@post("...")`, `@route("...")`
  "@get/post/route": r"@(get|post|route)\(['\"][^'\"]*['\"]",
  
  # Matches `.route("...")` in Flask-like apps
  ".route": r"\.route\(['\"][^'\"]*['\"]",
  
  # Matches decorators like `@module.get("...")`, `@module.post("...")`
  ".get/.post/.api_route": r"@\S*\.(get|post|api_route)\(['\"][^'\"]*['\"]",
  
  # Matches Django URL patterns like `path("...", ...)` or `re_path("...", ...)`
  "django_path": r"\bpath\(['\"][^'\"]*['\"]\s*,.*\)",
  "django_re_path": r"\bre_path\(r?['\"][^'\"]*['\"]\s*,.*\)",
  
  # Matches `.register("...", ...)` for route registration
  # To many false positives
  # "dot_register": r"\.register\(r?['\"][^'\"]*['\"]\s*,.*\)",
  
  # Matches `.add_url_rule("...")` in Flask
  "dot_add_url_rule": r"\.add_url_rule\(['\"][^'\"]*['\"]",

  # Matches `.endpoint("...")`
  "dot_endpoint": r"\.endpoint\(['\"][^'\"]*['\"]",
  
  # Matches `Rule("...")` in Flask/Werkzeug
  "rule_instantiation": r"Rule\(['\"][^'\"]*['\"]",
  
  # Matches `view_functions['...']` in Flask
  "view_functions": r"view_functions\['[^'\"]*'\]",
  
  # Matches `route_base="..."` in class-based views
  "route_base_assignment": r"route_base=['\"][^'\"]*['\"]"
}

IMPORT_FRAMEWORK_REGEX = {
  # Major frameworks
  "import_flask": r"^\s*(from\s+flask\b[\w.]*\s+import|import\s+flask\b[\w.]*)\b",
  "import_django": r"^\s*(from\s+django\b[\w.]*\simport|import\s+django\b[\w.]*)\b",
  "import_fastapi": r"^\s*(from\s+fastapi\b[\w.]*\s+import|import\s+fastapi\b[\w.]*)\b",
  "import_pyramid": r"^\s*(from\s+pyramid\b[\w.]*\s+import|import\s+pyramid\b[\w.]*)\b",
  "import_falcon": r"^\s*(from\s+falcon\b[\w.]*\s+import|import\s+falcon\b[\w.]*)\b",
  "import_streamlit": r"^\s*(from\s+streamlit\b[\w.]*\s+import|import\s+streamlit\b[\w.]*)\b",
  "import_gradio": r"^\s*(from\s+gradio\b[\w.]*\s+import|import\s+gradio\b[\w.]*)\b",
  "import_mesop": r"^\s*(from\s+mesop\b[\w.]*\s+import|import\s+mesop\b[\w.]*)\b",
  "import_turbogears": r"^\s*(from\s+tg\b[\w.]*\s+import|import\s+tg\b[\w.]*)\b",
  "import_web2py": r"^\s*(from\s+web2py\b[\w.]*\s+import|import\s+web2py\b[\w.]*)\b",
  "import_flask_restful": r"^\s*(from\s+flask_restful\b[\w.]*\s+import|import\s+flask_restful\b[\w.]*)\b",
  "import_dash": r"^\s*(from\s+dash\b[\w.]*\s+import|import\s+dash\b[\w.]*)\b",
  "import_pytorch_lightning": r"^\s*(from\s+lightning\b[\w.]*\s+import|import\s+lightning\b[\w.]*)\b",

  # Async frameworks
  "import_aiohttp": r"^\s*(from\s+aiohttp\b[\w.]*\s+import|import\s+aiohttp\b[\w.]*)\b",
  "import_quart": r"^\s*(from\s+quart\b[\w.]*\s+import|import\s+quart\b[\w.]*)\b",
  "import_blacksheep": r"^\s*(from\s+blacksheep\b[\w.]*\s+import|import\s+blacksheep\b[\w.]*)\b",
  
  # Microframeworks
  "import_bottle": r"^\s*(from\s+bottle\b[\w.]*\s+import|import\s+bottle\b[\w.]*)\b",
  "import_hug": r"^\s*(from\s+hug\b[\w.]*\s+import|import\s+hug\b[\w.]*)\b",
  "import_responder": r"^\s*(from\s+responder\b[\w.]*\s+import|import\s+responder\b[\w.]*)\b",
  
  # Full-stack frameworks
  "import_turbogears": r"^\s*(from\s+turbogears\b[\w.]*\s+import|import\s+turbogears\b[\w.]*)\b",
  "import_web2py": r"^\s*(from\s+web2py\b[\w.]*\s+import|import\s+web2py\b[\w.]*)\b",
  
  # Server/HTTP tools
  "import_tornado": r"^\s*(from\s+tornado\b[\w.]*\s+import|import\s+tornado\b[\w.]*)\b",
  "import_sanic": r"^\s*(from\s+sanic\b[\w.]*\s+import|import\s+sanic\b[\w.]*)\b",
  "import_starlette": r"^\s*(from\s+starlette\b[\w.]*\s+import|import\s+starlette\b[\w.]*)\b",
  "import_litestar": r"^\s*(from\s+litestar\b[\w.]*\s+import|import\s+litestar\b[\w.]*)\b",
  "import_cherrypy": r"^\s*(from\s+cherrypy\b[\w.]*\s+import|import\s+cherrypy\b[\w.]*)\b",
  "import_fastapi_utils": r"^\s*(from\s+fastapi_utils\b[\w.]*\s+import|import\s+fastapi_utils\b[\w.]*)\b"
}

REMOTE_INDICATORS = {
    **{k: re.compile(v, re.IGNORECASE | re.MULTILINE) for k, v in IMPORT_FRAMEWORK_REGEX.items()},
    **{k: re.compile(v) for k, v in ROUTE_REGEX.items()}
}

LOCAL_INDICATORS = {}

def classify(repo_src_path):
  web_patterns = set()
  local_patterns = set()

  for root, _, files in os.walk(repo_src_path):
    for file in files:
      if not file.endswith('.py'):
        continue

      if 'test' in root:
        continue

      path = os.path.join(root, file)
      try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
          content = f.read()
          file_web_matches = set()

          # Check for web interface patterns
          for key, pattern in REMOTE_INDICATORS.items():
            if pattern.search(content):
              file_web_matches.add(key)
              web_patterns.add(key)

          # Check local patterns without tracking file matches
          for key, pattern in LOCAL_INDICATORS.items():
            if pattern.search(content):
              local_patterns.add(key)

          # Log web matches only
          if file_web_matches:
            logging.info(f"Web patterns in {os.path.relpath(path, repo_src_path)}:")
            for key in file_web_matches:
              logging.info(f"  - {key}")

      except Exception as e:
        logging.error(f"Error processing {file}: {str(e)}", exc_info=False)

  return web_patterns, local_patterns