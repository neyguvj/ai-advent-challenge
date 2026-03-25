#!/usr/bin/env python3
"""
CLI client for the AI Advent Challenge backend server.
This client provides three commands:
- list: List available models
- request: Run a request on a given model
- user create: Create a new user
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


def run_request(base_url, model, temperature, prompt, user_request, max_tokens, user):
    """Run a request on the given model"""
    try:
        user_id = get_user_id(base_url, user)
        print(user_id)
        payload = {
            "model": model,
            "prompt": prompt,
            "request": user_request,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "user_id": user_id,
        }

        session_id = get_session_id(base_url, user_id)
        if session_id is not None:
            payload["session_id"] = session_id
            messages = load_messages(base_url, session_id)
            print_messages(messages)

        print("human:", user_request)
        response = requests.post(f"{base_url}/completion", json=payload)

        if response.status_code == 200:
            result = response.json()
            print(f"assistant: {result.get('response')}")

            # Print token usage statistics if available
            stats = result.get("statistics", {})
            if stats:
                print(f"Total Input tokens: {stats.get('total_input_tokens', 0)}")
                print(f"Total Output tokens: {stats.get('total_output_tokens', 0)}")
                print(f"Last input tokens: {stats.get('last_input_tokens', 0)}")
                print(f"Last output tokens: {stats.get('last_output_tokens', 0)}")

            # Print price information if available
            price = result.get("price", {})
            if price:
                print(f"Last request price: {price.get('last_request_price', 0):.6f}р")
                print(f"Total input price: {price.get('total_input_price', 0):.6f}р")
                print(f"Total output price: {price.get('total_output_price', 0):.6f}р")
                print(f"All requests price: {price.get('all_requests_price', 0):.6f}р")
        else:
            print(
                f"Error: Failed to get completion (status code: {response.status_code})"
            )
            print(response.json().get("error", "Unknown error"))
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
        sys.exit(1)


def create_user(base_url, email, password):
    """Create a new user via the backend server"""
    try:
        payload = {"email": email, "password": password}

        response = requests.post(f"{base_url}/users", json=payload)

        if response.status_code == 201:
            result = response.json()
            print(f"User created successfully:")
            print(f"  ID: {result.get('id')}")
            print(f"  Email: {result.get('email')}")
        else:
            print(f"Error: Failed to create user (status code: {response.status_code})")
            print(response.json().get("error", "Unknown error"))
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
        sys.exit(1)


def get_user_id(base_url, email):
    try:
        response = requests.get(f"{base_url}/users/email/{email}")
        if response.status_code == 200:
            result = response.json()
            return result.get("id")
        else:
            print(
                f"Error: Failed to get user by email (status code: {response.status_code})"
            )
            print(response.json().get("error", "Unknown error"))
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
        sys.exit(1)


def get_session_id(base_url, user_id):
    try:
        response = requests.get(f"{base_url}/users/{user_id}/sessions")
        if response.status_code == 200:
            result = response.json()
            if result:
                return result[0].get("id")
        elif response.status_code == 404:
            return None
        else:
            print(
                f"Error: Failed to get session id (status code: {response.status_code})"
            )
            print(response.json().get("error", "Unknown error"))
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
        sys.exit(1)


def load_messages(base_url, session_id):
    try:
        response = requests.get(f"{base_url}/sessions/{session_id}/messages")
        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Error: Failed to load messages (status code: {response.status_code})"
            )
            print(response.json().get("error", "Unknown error"))
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
        sys.exit(1)


def print_messages(messages):
    print("loaded message history")
    for msg in messages:
        print(f"{msg.get("timestamp")}:, {msg.get("role")}")
        print(msg.get("content"))
        print("\n")


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
    request_parser.add_argument("--user", help="user email", required=True)
    request_parser.add_argument("--request", required=True, help="User request")

    # User create command
    user_parser = subparsers.add_parser("user", help="Commands to manage users")
    user_subparsers = user_parser.add_subparsers(
        dest="user_command", help="Available commands"
    )
    user_create_parser = user_subparsers.add_parser("create", help="Create new user")
    user_create_parser.add_argument(
        "--base-url", required=True, help="Base URL of the backend server"
    )
    user_create_parser.add_argument(
        "--email", required=True, help="Email of the new user"
    )
    user_create_parser.add_argument(
        "--password", required=True, help="Password of the new user"
    )

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
            args.user,
        )
    elif args.command == "user":
        if args.user_command == "create":
            create_user(args.base_url, args.email, args.password)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
