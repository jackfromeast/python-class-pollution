"""
Given the debug.jsonl file, the script helps to profile the LLM usage during analysis.

Usage:
python3 scripts/profile_llm_usage.py --debug_file /home/jackfromeast/Desktop/python-class-pollution/tasks/llm-check/github-1K-r1/archive/logs-0728/debug_info.jsonl --scheduler_file /home/jackfromeast/Desktop/python-class-pollution/tasks/llm-check/github-1K-r1/archive/logs-0728/scheduler/scheduler.info.log
"""

import json
import re
import argparse
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import sys


def parse_scheduler_log(scheduler_file):
  """Parse scheduler log to extract timing information."""
  start_time = None
  end_time = None
  repo_timings = {}
  
  with open(scheduler_file, 'r') as f:
    for line in f:
      line = line.strip()
      if not line:
        continue
        
      # Extract timestamp and event
      timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3}', line)
      if not timestamp_match:
        continue
        
      timestamp_str = timestamp_match.group(1)
      timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
      
      # Track overall start and end times
      if start_time is None:
        start_time = timestamp
      end_time = timestamp
      
      # Extract repo information
      if "Starting worker for repo:" in line:
        repo_match = re.search(r'Starting worker for repo: (https://github\.com/[^/]+/[^/\s]+)', line)
        if repo_match:
          repo_url = repo_match.group(1)
          repo_timings[repo_url] = {'start': timestamp}
          
      elif "Worker completed for repo:" in line:
        repo_match = re.search(r'Worker completed for repo: (https://github\.com/[^/]+/[^/\s]+)', line)
        if repo_match:
          repo_url = repo_match.group(1)
          if repo_url in repo_timings:
            repo_timings[repo_url]['end'] = timestamp
            repo_timings[repo_url]['duration'] = (timestamp - repo_timings[repo_url]['start']).total_seconds()
  
  total_duration = (end_time - start_time).total_seconds() if start_time and end_time else 0
  
  return {
    'start_time': start_time,
    'end_time': end_time,
    'total_duration_seconds': total_duration,
    'total_duration_minutes': total_duration / 60,
    'repo_timings': repo_timings
  }


def extract_repo_name_from_path(file_path):
  """Extract repository name from file path in debug data."""
  # The debug format has paths like /app/... where /app is the repository root
  # So we need to extract the repo from session tool usage context
  return None  # Will be determined from context


def parse_debug_jsonl(debug_file):
  """Parse debug.jsonl file to extract token usage information."""
  total_tokens = 0
  total_repos = 0
  repo_tokens = defaultdict(int)
  repo_details = {}
  lines_processed = 0
  lines_with_tokens = 0
  
  with open(debug_file, 'r') as f:
    for line_num, line in enumerate(f, 1):
      line = line.strip()
      if not line or line.startswith('//'):
        continue
        
      lines_processed += 1
      try:
        data = json.loads(line)
      except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse line {line_num}: {e}")
        continue
      
      # Extract debug info from the new format
      debug_info = data.get('debug_info', {})
      resource_usage = debug_info.get('resource_usage', {})
      line_tokens = resource_usage.get('total_tokens', 0)
      
      if line_tokens > 0:
        lines_with_tokens += 1
      total_tokens += line_tokens
      total_repos += 1
      
      # Extract repository name from the analysis context
      sessions = debug_info.get('sessions', {})
      repo_name = f"repository_{line_num:03d}"  # More readable format with zero-padding
      
      # Try to infer some info from file paths in tool usage to make names more meaningful
      file_patterns = set()
      for session_id, session_data in sessions.items():
        tool_usage = session_data.get('tool_usage', [])
        for tool in tool_usage:
          args = tool.get('args', {})
          # Look for file or dir paths that might indicate project characteristics
          for key in ['file', 'dir']:
            if key in args:
              path = args[key]
              # Extract some identifying characteristics from paths
              if 'package.json' in path:
                file_patterns.add('nodejs')
              elif '.ts' in path:
                file_patterns.add('typescript')
              elif '.js' in path:
                file_patterns.add('javascript')
              elif 'electron' in path.lower():
                file_patterns.add('electron')
              elif 'main' in path.lower():
                file_patterns.add('main')
              elif 'src' in path.lower():
                file_patterns.add('src')
      
      # Create a more descriptive name if we found patterns
      if file_patterns:
        pattern_str = '_'.join(sorted(file_patterns)[:2])  # Max 2 patterns to keep names reasonable
        repo_name = f"repo_{line_num:03d}_{pattern_str}"
      
      # Update repository tracking
      repo_tokens[repo_name] += line_tokens
      repo_details[repo_name] = {
        'total_tokens': repo_tokens[repo_name],
        'sessions': len(sessions),
        'total_tool_calls': resource_usage.get('total_tool_calls', 0),
        'matches_found': debug_info.get('analysis_summary', {}).get('total_matches_found', 0)
      }
  
  print(f"Debug parsing: {lines_processed} lines processed, {lines_with_tokens} lines had token data")
  
  return {
    'total_tokens': total_tokens,
    'total_repos': total_repos,
    'repo_tokens': dict(repo_tokens),
    'repo_details': repo_details
  }


def calculate_statistics(debug_data, timing_data):
  """Calculate comprehensive statistics."""
  total_tokens = debug_data['total_tokens']
  total_repos = debug_data['total_repos']
  total_minutes = timing_data['total_duration_minutes']
  total_tool_calls = sum(details.get('total_tool_calls', 0) for details in debug_data['repo_details'].values())
  
  stats = {
    'total_tokens': total_tokens,
    'total_repos': total_repos,
    'total_minutes': total_minutes,
    'total_tool_calls': total_tool_calls,
    'tokens_per_minute': total_tokens / total_minutes if total_minutes > 0 else 0,
    'tokens_per_repo': total_tokens / total_repos if total_repos > 0 else 0,
    'minutes_per_repo': total_minutes / total_repos if total_repos > 0 else 0,
    'tools_per_repo': total_tool_calls / total_repos if total_repos > 0 else 0,
    'tools_per_token': total_tool_calls / total_tokens if total_tokens > 0 else 0,
  }
  
  return stats


def print_detailed_repo_analysis(debug_data, timing_data):
  """Print detailed analysis per repository."""
  print("\n" + "="*80)
  print("DETAILED REPOSITORY ANALYSIS")
  print("="*80)
  
  repo_tokens = debug_data['repo_tokens']
  repo_details = debug_data['repo_details']
  repo_timings = timing_data['repo_timings']
  
  # Create combined data
  combined_data = []
  for repo_name, tokens in repo_tokens.items():
    # Try to find corresponding timing data
    timing_info = None
    repo_url = None
    for url, timing in repo_timings.items():
      if repo_name in url or url.endswith(f"/{repo_name}"):
        timing_info = timing
        repo_url = url
        break
    
    details = repo_details.get(repo_name, {})
    combined_data.append({
      'name': repo_name,
      'url': repo_url,
      'tokens': tokens,
      'duration': timing_info.get('duration', 0) if timing_info else 0,
      'sessions': details.get('sessions', 0),
      'tool_calls': details.get('total_tool_calls', 0),
      'matches': details.get('matches_found', 0)
    })
  
  # Sort by tokens (descending)
  combined_data.sort(key=lambda x: x['tokens'], reverse=True)
  
  print(f"{'Rank':<4} {'Repository':<35} {'Tokens':<8} {'Minutes':<8} {'T/Min':<8} {'Sessions':<8} {'Tools':<8} {'Matches':<8}")
  print("-" * 80)
  
  for i, data in enumerate(combined_data[:20], 1):  # Top 20
    tokens = data['tokens']
    duration_min = data['duration'] / 60 if data['duration'] > 0 else 0
    tokens_per_min = tokens / duration_min if duration_min > 0 else 0
    
    print(f"{i:<4} {data['name'][:34]:<35} {tokens:<8} {duration_min:<8.1f} {tokens_per_min:<8.0f} "
          f"{data['sessions']:<8} {data['tool_calls']:<8} {data['matches']:<8}")


def main():
  parser = argparse.ArgumentParser(description='Profile LLM usage from debug logs')
  parser.add_argument('--debug_file', required=True, help='Path to debug.jsonl file')
  parser.add_argument('--scheduler_file', required=True, help='Path to scheduler log file')
  parser.add_argument('--detailed', action='store_true', help='Show detailed per-repository analysis')
  parser.add_argument('--top', type=int, default=10, help='Number of top consumers to show (default: 10)')
  
  args = parser.parse_args()
  
  # Validate input files
  if not Path(args.debug_file).exists():
    print(f"Error: Debug file not found: {args.debug_file}")
    sys.exit(1)
    
  if not Path(args.scheduler_file).exists():
    print(f"Error: Scheduler file not found: {args.scheduler_file}")
    sys.exit(1)
  
  # Parse data
  print("Parsing debug data...")
  debug_data = parse_debug_jsonl(args.debug_file)
  
  print("Parsing scheduler log...")
  timing_data = parse_scheduler_log(args.scheduler_file)
  
  # Calculate statistics
  stats = calculate_statistics(debug_data, timing_data)
  
  # Print summary
  print("\n" + "="*60)
  print("LLM USAGE ANALYSIS SUMMARY")
  print("="*60)
  print(f"Total tokens consumed: {stats['total_tokens']:,}")
  print(f"Total tool calls made: {stats['total_tool_calls']:,}")
  print(f"Total repositories analyzed: {stats['total_repos']}")
  print(f"Total analysis time: {stats['total_minutes']:.1f} minutes ({stats['total_minutes']/60:.1f} hours)")
  print(f"")
  print(f"Per-repository averages:")
  print(f"  Tokens per repository: {stats['tokens_per_repo']:.0f}")
  print(f"  Tool calls per repository: {stats['tools_per_repo']:.1f}")
  print(f"  Minutes per repository: {stats['minutes_per_repo']:.1f}")
  print(f"")
  print(f"Efficiency metrics:")
  print(f"  Tokens per minute: {stats['tokens_per_minute']:.0f}")
  print(f"  Tools per token ratio: {stats['tools_per_token']:.6f}")
  print(f"  Cost per repository: ${(stats['tokens_per_repo'] / 1000000) * 2.0:.3f}")
  
  # Analysis period
  if timing_data['start_time'] and timing_data['end_time']:
    print(f"Analysis period: {timing_data['start_time']} to {timing_data['end_time']}")
  
  # Efficiency metrics
  completed_repos = len([r for r in timing_data['repo_timings'].values() if 'duration' in r])
  if completed_repos > 0:
    print(f"Successfully completed repositories: {completed_repos}")
    avg_duration = sum(r['duration'] for r in timing_data['repo_timings'].values() if 'duration' in r) / completed_repos
    print(f"Average time per completed repository: {avg_duration/60:.1f} minutes")
  
  # Top token consumers
  print("\n" + "="*50)
  print(f"TOP {args.top} TOKEN CONSUMERS")
  print("="*50)
  if stats['total_tokens'] == 0:
    print("No token usage data found. Please check your debug file.")
    print("This could mean:")
    print("  - The debug file is empty or contains no valid JSON")
    print("  - Token usage data is not present in the expected format")
    print("  - The LLM analysis didn't generate any token usage data")
  else:
    sorted_repos = sorted(debug_data['repo_tokens'].items(), key=lambda x: x[1], reverse=True)
    for i, (repo, tokens) in enumerate(sorted_repos[:args.top], 1):
      percentage = (tokens / stats['total_tokens']) * 100
      details = debug_data['repo_details'].get(repo, {})
      sessions = details.get('sessions', 0)
      tool_calls = details.get('total_tool_calls', 0)
      print(f"{i:2}. {repo:<35} {tokens:>8,} tokens ({percentage:5.1f}%) | {sessions} sessions | {tool_calls} tools")
  
  # Detailed analysis if requested
  if args.detailed:
    print_detailed_repo_analysis(debug_data, timing_data)
  
  # Tool usage statistics
  total_tool_calls = sum(details.get('total_tool_calls', 0) for details in debug_data['repo_details'].values())
  print(f"\n" + "="*50)
  print("TOOL USAGE STATISTICS")
  print("="*50)
  print(f"Total tool calls across all repositories: {total_tool_calls:,}")
  print(f"Average tool calls per repository: {total_tool_calls / stats['total_repos']:.1f}")
  print(f"Tool calls per token ratio: {total_tool_calls / stats['total_tokens']:.6f}")
  
  # Show top tool users
  print(f"\nTOP {min(10, args.top)} REPOSITORIES BY TOOL USAGE:")
  sorted_by_tools = sorted(debug_data['repo_details'].items(), key=lambda x: x[1].get('total_tool_calls', 0), reverse=True)
  for i, (repo, details) in enumerate(sorted_by_tools[:min(10, args.top)], 1):
    tool_calls = details.get('total_tool_calls', 0)
    tokens = debug_data['repo_tokens'].get(repo, 0)
    ratio = tool_calls / tokens if tokens > 0 else 0
    print(f"{i:2}. {repo:<35} {tool_calls:>6} tools | {tokens:>8,} tokens | {ratio:.4f} tools/token")

  print(f"\nAnalysis complete. Processed {debug_data['total_repos']} repositories.")
  print(f"Total token cost estimate (at $2.00/1M tokens): ${(stats['total_tokens'] / 1000000) * 2.0:.2f}")


if __name__ == "__main__":
  main()