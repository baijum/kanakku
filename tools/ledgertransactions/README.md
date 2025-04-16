# Ledger Transactions Fetcher

This command-line program fetches ledger transactions from a specific API endpoint based on a given Preamble Name. It first retrieves the Preamble ID associated with the provided name and then uses that ID to query the ledger transactions endpoint.

## Prerequisites

- Go programming language installed (for building).
- Access to the target API.

## Building

Navigate to the `ledgertransactions` directory and run the following command to build the executable:

```bash
go build -o ledger-fetcher
```

This will create an executable file named `ledger-fetcher` (or `ledger-fetcher.exe` on Windows) in the current directory.

## Configuration

The program requires the following information to run:

1.  **API Base URL:** The base URL of the API (e.g., `https://your-api-domain.com`).
2.  **API Access Token:** Your authentication token for the API.
3.  **Preamble Name:** The specific name of the Preamble whose ledger transactions you want to fetch.

You can provide this information using either environment variables or command-line flags. Command-line flags take precedence over environment variables.

### Environment Variables

-   `API_BASE_URL`: Set this to the base URL of your API.
-   `API_ACCESS_TOKEN`: Set this to your API access token.
-   `PREAMBLE_NAME`: Set this to the Preamble Name.

**Example (bash/zsh):**

```bash
export API_BASE_URL="https://api.example.com"
export API_ACCESS_TOKEN="your_actual_api_token_here"
export PREAMBLE_NAME="Your Preamble Name"
./ledger-fetcher
```

### Command-line Flags

-   `-token`: Use this flag to provide the API Access Token.
-   `-preamble-name`: Use this flag to provide the Preamble Name.

**Note:** The API Base URL *must* be provided via the `API_BASE_URL` environment variable.

**Example:**

```bash
export API_BASE_URL="https://api.example.com"
./ledger-fetcher -token="your_actual_api_token_here" -preamble-name="Your Preamble Name"
```

**Example (Mixing flags and environment variables):**

```bash
export API_BASE_URL="https://api.example.com"
export API_ACCESS_TOKEN="your_actual_api_token_here"
./ledger-fetcher -preamble-name="Another Preamble Name" # Uses token from env var
```

## Output

The program will:
1. Print the URL it's using to fetch the Preamble ID.
2. Print the found Preamble ID.
3. Print the URL it's using to fetch ledger transactions.
4. Print the number of transactions successfully fetched.
5. Print the fetched transactions in JSON format to standard output.

If any errors occur (e.g., missing configuration, API errors, network issues), an error message will be printed to standard error, and the program will exit with a non-zero status code. 