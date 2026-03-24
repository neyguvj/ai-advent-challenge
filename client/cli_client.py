#!/usr/bin/env python3
"""
CLI client for the AI Advent Challenge backend server.
This client provides two commands:
- list: List available models
- request: Run a request on a given model
"""

import argparse
import requests
import sys


def list_models(base_url):
    """List available models from the backend server"""
    try:
        response = requests.get(f"{base_url}/list_models")
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("Available models:")
            for model in models:
                print(f"  - {model}")
        else:
            print(
                f"Error: Failed to fetch models (status code: {response.status_code})"
            )
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
        sys.exit(1)


def run_request(base_url, model, temperature, prompt, user_request, max_tokens):
    """Run a request on the given model"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "request": user_request,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(f"{base_url}/completion", json=payload)

        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response')}")
        else:
            print(
                f"Error: Failed to get completion (status code: {response.status_code})"
            )
            print(response.json().get("error", "Unknown error"))
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="CLI client for AI Advent Challenge")

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List available models")
    list_parser.add_argument(
        "--base-url", required=True, help="Base URL of the backend server"
    )

    # Request command
    request_parser = subparsers.add_parser(
        "request", help="Run a request on a given model"
    )
    request_parser.add_argument(
        "--base-url", required=True, help="Base URL of the backend server"
    )
    request_parser.add_argument("--model", required=True, help="Model ID to use")
    request_parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Model temperature (default: 0.1)",
    )
    request_parser.add_argument(
        "--max-tokens", default=2048, help="Max tokens in model response"
    )
    request_parser.add_argument(
        "--prompt", default="", help="System prompt (default: empty)"
    )
    request_parser.add_argument("--request", required=True, help="User request")

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute the appropriate command
    if args.command == "list":
        list_models(args.base_url)
    elif args.command == "request":
        run_request(
            args.base_url,
            args.model,
            args.temperature,
            args.prompt,
            args.request,
            args.max_tokens,
        )
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
