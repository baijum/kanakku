package main

import (
	"encoding/json"
	"errors" // Import errors package
	"flag"
	"fmt"
	"net/http"
	"os"
)

// Define the expected structure of the API response for ledger transactions
// Adjust this based on the actual data structure returned by the API
type LedgerTransaction struct {
	// Example fields - replace with actual fields
	ID          string  `json:"id"`
	Date        string  `json:"date"`
	Description string  `json:"description"`
	Amount      float64 `json:"amount"`
}

// Define the expected structure for items in the /api/v1/preambles response
// Adjust this based on the actual data structure returned by the API
type Preamble struct {
	ID   string `json:"id"`   // Assuming the ID field is named "id"
	Name string `json:"name"` // Assuming the name field is named "name"
}

const (
	// Remove the constant apiBaseURL
	// !!! IMPORTANT: Replace with your actual API base URL !!!
	// apiBaseURL           = "https://api.example.com" // Example: "https://your-api-domain.com"
	ledgerAPIEndpoint = "/api/v1/ledgertransactions"
	// Remove unused preamblesAPIEndpoint
	// preamblesAPIEndpoint = "/api/v1/preambles"
)

// Function to get Preamble ID by Name using the specific name endpoint
func getPreambleIDByName(apiBaseURL, token, name string) (string, error) {
	// Construct the URL for the specific preamble name endpoint
	preambleByNameEndpoint := fmt.Sprintf("/api/v1/preambles/name/%s", name)
	fmt.Printf("Fetching preamble ID from %s%s\n", apiBaseURL, preambleByNameEndpoint)

	client := &http.Client{}
	reqURL := apiBaseURL + preambleByNameEndpoint
	req, err := http.NewRequest("GET", reqURL, nil)
	if err != nil {
		return "", fmt.Errorf("error creating request for preamble by name: %w", err)
	}

	// Use "Token" prefix instead of "Bearer"
	req.Header.Add("Authorization", "Token "+token)
	req.Header.Add("Accept", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("error making request for preamble by name: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusNotFound { // Handle 404 specifically
		return "", fmt.Errorf("preamble with name '%s' not found", name)
	}
	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("preamble by name API returned non-OK status: %s", resp.Status)
	}

	// Decode the single Preamble object response
	var preamble Preamble
	decoder := json.NewDecoder(resp.Body)
	if err := decoder.Decode(&preamble); err != nil {
		return "", fmt.Errorf("error decoding preamble by name JSON response: %w", err)
	}

	// Check if ID is present (though it should be if status is OK)
	if preamble.ID == "" {
		return "", errors.New("preamble ID not found in the response")
	}

	fmt.Printf("Found Preamble ID: %s for Name: %s\n", preamble.ID, name)
	return preamble.ID, nil
}

func main() {
	// Option 1: Get token and preamble name from command-line flags
	tokenFlag := flag.String("token", "", "API Access Token")
	preambleNameFlag := flag.String("preamble-name", "", "Preamble Name")
	flag.Parse()

	accessToken := *tokenFlag
	preambleName := *preambleNameFlag

	// Option 2: Fallback to environment variables if flags are not provided
	if accessToken == "" {
		accessToken = os.Getenv("API_ACCESS_TOKEN")
	}
	if preambleName == "" {
		preambleName = os.Getenv("PREAMBLE_NAME")
	}
	// Get API Base URL from environment variable
	apiBaseURL := os.Getenv("API_BASE_URL")

	// Validate inputs
	if apiBaseURL == "" { // Add validation for apiBaseURL
		fmt.Println("Error: API Base URL is required.")
		fmt.Println("Please provide it using the API_BASE_URL environment variable.")
		os.Exit(1)
	}
	if accessToken == "" {
		fmt.Println("Error: API Access Token is required.")
		fmt.Println("Please provide it using the -token flag or the API_ACCESS_TOKEN environment variable.")
		os.Exit(1)
	}
	if preambleName == "" {
		fmt.Println("Error: Preamble Name is required.")
		fmt.Println("Please provide it using the -preamble-name flag or the PREAMBLE_NAME environment variable.")
		os.Exit(1)
	}

	// Get the Preamble ID using the Name
	preambleID, err := getPreambleIDByName(apiBaseURL, accessToken, preambleName)
	if err != nil {
		fmt.Printf("Error getting Preamble ID: %v\n", err)
		os.Exit(1)
	}

	// Construct the Ledger Transactions URL with the fetched preamble_id query parameter
	requestURL := fmt.Sprintf("%s%s?preamble_id=%s", apiBaseURL, ledgerAPIEndpoint, preambleID)
	fmt.Println("Fetching ledger transactions from:", requestURL)

	client := &http.Client{}
	req, err := http.NewRequest("GET", requestURL, nil)
	if err != nil {
		fmt.Printf("Error creating ledger request: %v\n", err)
		os.Exit(1)
	}

	// Add the Authorization header
	req.Header.Add("Authorization", "Token "+accessToken)
	req.Header.Add("Accept", "application/json") // Assuming the API returns JSON

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("Error making ledger request: %v\n", err)
		os.Exit(1)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("Error: Ledger API returned non-OK status: %s\n", resp.Status)
		// Optionally, read and print the error body
		// bodyBytes, _ := io.ReadAll(resp.Body)
		// fmt.Println("Response Body:", string(bodyBytes))
		os.Exit(1)
	}

	// Decode the JSON response
	var transactions []LedgerTransaction // Assuming the API returns a JSON array
	decoder := json.NewDecoder(resp.Body)
	if err := decoder.Decode(&transactions); err != nil {
		fmt.Printf("Error decoding ledger JSON response: %v\n", err)
		os.Exit(1)
	}

	// Process or print the transactions
	fmt.Printf("Successfully fetched %d ledger transactions.\n", len(transactions))

	// Example: Print the fetched data as JSON
	jsonData, err := json.MarshalIndent(transactions, "", "  ")
	if err != nil {
		fmt.Printf("Error marshalling JSON for output: %v\n", err)
		os.Exit(1)
	}
	fmt.Println(string(jsonData))

	// TODO: Add logic here to save the data to a file if needed
}
