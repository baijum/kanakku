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
	// !!! IMPORTANT: Replace with your actual API base URL !!!
	apiBaseURL           = "https://api.example.com" // Example: "https://your-api-domain.com"
	ledgerAPIEndpoint    = "/api/v1/ledgertransactions"
	preamblesAPIEndpoint = "/api/v1/preambles" // Endpoint to fetch all preambles
)

// Function to get Preamble ID by Name
func getPreambleIDByName(baseURL, token, name string) (string, error) {
	fmt.Printf("Fetching preambles to find ID for name: %s\n", name)
	client := &http.Client{}
	reqURL := baseURL + preamblesAPIEndpoint
	req, err := http.NewRequest("GET", reqURL, nil)
	if err != nil {
		return "", fmt.Errorf("error creating request for preambles: %w", err)
	}

	req.Header.Add("Authorization", "Bearer "+token)
	req.Header.Add("Accept", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("error making request for preambles: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("preambles API returned non-OK status: %s", resp.Status)
	}

	var preambles []Preamble // Assuming the API returns a JSON array
	decoder := json.NewDecoder(resp.Body)
	if err := decoder.Decode(&preambles); err != nil {
		return "", fmt.Errorf("error decoding preambles JSON response: %w", err)
	}

	// Find the preamble with the matching name
	for _, p := range preambles {
		if p.Name == name {
			fmt.Printf("Found Preamble ID: %s for Name: %s\n", p.ID, name)
			return p.ID, nil
		}
	}

	return "", errors.New("preamble name not found")
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

	// Validate inputs
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
	req.Header.Add("Authorization", "Bearer "+accessToken)
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
