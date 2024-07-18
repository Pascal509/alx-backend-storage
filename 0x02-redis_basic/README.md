# Redis Basic

This project involves writing a `Cache` class that interacts with a Redis instance to store and retrieve data. The class includes methods to store data in Redis using randomly generated keys, retrieve the stored data, and convert it back to the original type. Additionally, the class tracks how many times its methods are called and maintains a history of method inputs and outputs. The `replay` function can be used to display the history of calls of a particular function.

## Requirements

- Python 3.7
- Redis server running on the local machine

## Usage

1. Ensure Redis server is running.
2. Run the main script to store and retrieve data.

```bash
$ python3 main.py
