"""Command-line interface for log manager."""

from __future__ import annotations

import argparse
import sys

from log_manager.manager import LogManager


def cmd_index(args: argparse.Namespace) -> int:
    """Index a log file.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code
    """
    manager = LogManager(args.logs_dir)

    try:
        count = manager.index_log(args.log_file)
        print(f"[OK] Indexed {count} log entries from {args.log_file}")
        return 0
    except Exception as e:
        print(f"[ERROR] Error indexing {args.log_file}: {e}", file=sys.stderr)
        return 1


def cmd_list_executions(args: argparse.Namespace) -> int:
    """List all executions in a log file.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code
    """
    manager = LogManager(args.logs_dir)

    executions = manager.list_executions(args.log_file)

    if not executions:
        print(f"No executions found in {args.log_file}")
        print("Run 'log_manager index' first to index the log file.")
        return 1

    print(f"\nExecutions in {args.log_file}:")
    print("-" * 80)

    for i, exec_info in enumerate(executions, 1):
        exec_id = exec_info["execution_id"]
        start = exec_info["start_time"]
        end = exec_info.get("end_time", "ongoing")
        desc = exec_info.get("description", "")

        print(f"{i:3d}. {exec_id}")
        print(f"     Start: {start}")
        print(f"     End:   {end}")
        if desc:
            print(f"     Desc:  {desc}")
        print()

    return 0


def cmd_show(args: argparse.Namespace) -> int:
    """Show filtered logs.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code
    """
    manager = LogManager(args.logs_dir)

    # Parse multiple levels if provided
    level = None
    if args.level:
        levels = [lvl.strip().upper() for lvl in args.level.split(",")]
        if len(levels) == 1:
            level = levels[0]
        else:
            level = levels[0]
            print(
                f"Note: Multiple levels not yet supported, using {level}",
                file=sys.stderr,
            )

    try:
        manager.show_logs(
            args.log_file,
            colorize=not args.no_color,
            execution_id=args.execution,
            level=level,
            logger=args.logger,
            category=args.category,
            file=args.file,
            limit=args.limit,
        )
        return 0
    except Exception as e:
        print(f"[ERROR] Error: {e}", file=sys.stderr)
        return 1


def cmd_export(args: argparse.Namespace) -> int:
    """Export filtered logs to a file.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code
    """
    manager = LogManager(args.logs_dir)

    try:
        count = manager.export_logs(
            args.log_file,
            args.output,
            execution_id=args.execution,
            level=args.level,
            logger=args.logger,
            category=args.category,
            file=args.file,
            limit=args.limit,
        )
        print(f"[OK] Exported {count} entries to {args.output}")
        return 0
    except Exception as e:
        print(f"[ERROR] Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Robot log manager - filter and analyze logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index a log file
  %(prog)s index 2025-11-06.log

  # List all executions
  %(prog)s list-executions 2025-11-06.log

  # Show logs from specific execution
  %(prog)s show 2025-11-06.log --execution 2025-11-06_exec002

  # Filter by category
  %(prog)s show 2025-11-06.log --category "NAV:Task"

  # Filter by level and logger
  %(prog)s show 2025-11-06.log --level ERROR --logger Navigator

  # Export filtered logs
  %(prog)s export 2025-11-06.log -o errors.txt --level ERROR

  # Combine multiple filters
  %(prog)s show 2025-11-06.log \\
      --execution 2025-11-06_exec002 \\
      --category "CTRL:RB" \\
      --level "WARNING,ERROR" \\
      --limit 100
        """,
    )

    parser.add_argument(
        "--logs-dir",
        default="logs",
        help="Directory containing log files (default: logs)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Index command
    index_parser = subparsers.add_parser(
        "index",
        help="Index a log file for faster searching",
    )
    index_parser.add_argument(
        "log_file",
        help="Log file to index (e.g., 2025-11-06.log)",
    )
    index_parser.set_defaults(func=cmd_index)

    # List executions command
    list_parser = subparsers.add_parser(
        "list-executions",
        aliases=["list", "ls"],
        help="List all executions in a log file",
    )
    list_parser.add_argument("log_file", help="Log file to query")
    list_parser.set_defaults(func=cmd_list_executions)

    # Show command
    show_parser = subparsers.add_parser(
        "show",
        help="Display filtered logs",
    )
    show_parser.add_argument("log_file", help="Log file to query")
    show_parser.add_argument(
        "-e",
        "--execution",
        help="Filter by execution ID",
    )
    show_parser.add_argument(
        "-l",
        "--level",
        help="Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    show_parser.add_argument(
        "-L",
        "--logger",
        help="Filter by logger name (supports wildcards)",
    )
    show_parser.add_argument(
        "-c",
        "--category",
        help="Filter by category prefix (e.g., NAV:Task, CTRL:RB)",
    )
    show_parser.add_argument(
        "-f",
        "--file",
        help="Filter by source file (supports wildcards)",
    )
    show_parser.add_argument(
        "-n",
        "--limit",
        type=int,
        help="Limit number of results",
    )
    show_parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    show_parser.set_defaults(func=cmd_show)

    # Export command
    export_parser = subparsers.add_parser(
        "export",
        help="Export filtered logs to a file",
    )
    export_parser.add_argument("log_file", help="Log file to query")
    export_parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output file path",
    )
    export_parser.add_argument(
        "-e",
        "--execution",
        help="Filter by execution ID",
    )
    export_parser.add_argument(
        "-l",
        "--level",
        help="Filter by log level",
    )
    export_parser.add_argument(
        "-L",
        "--logger",
        help="Filter by logger name",
    )
    export_parser.add_argument(
        "-c",
        "--category",
        help="Filter by category prefix",
    )
    export_parser.add_argument(
        "-f",
        "--file",
        help="Filter by source file",
    )
    export_parser.add_argument(
        "-n",
        "--limit",
        type=int,
        help="Limit number of results",
    )
    export_parser.set_defaults(func=cmd_export)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
