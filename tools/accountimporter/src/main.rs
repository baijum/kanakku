use anyhow::{Context, Result};
use clap::Parser;
use regex::Regex;
use reqwest::header::{HeaderMap, HeaderValue, AUTHORIZATION, CONTENT_TYPE};
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::PathBuf;

#[derive(Parser, Debug)]
#[command(author, version, about = "Import accounts from ledger files and create them in Kanakku")]
struct Args {
    /// Path to the ledger file to parse
    #[arg(short, long)]
    file: PathBuf,

    /// API URL for the Kanakku backend
    #[arg(short, long, default_value = "http://localhost:8000")]
    api_url: String,

    /// API token for authenticating with the Kanakku backend
    #[arg(short, long)]
    token: String,

    /// Enable verbose output
    #[arg(short, long)]
    verbose: bool,

    /// Dry run - parse the file but don't create accounts
    #[arg(short, long)]
    dry_run: bool,
}

#[derive(Debug, Serialize, Deserialize)]
struct Account {
    name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    description: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    currency: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    balance: Option<f64>,
}

#[derive(Debug, Deserialize)]
#[allow(dead_code)]
struct ApiResponse {
    message: String,
    account: AccountResponse,
}

#[derive(Debug, Deserialize)]
struct AccountResponse {
    id: i32,
    name: String,
    // Include other fields as needed
}

#[derive(Debug, Deserialize)]
struct ErrorResponse {
    error: String,
}

#[tokio::main]
async fn main() -> Result<()> {
    let args = Args::parse();
    
    // Configure the API client 
    let client = reqwest::Client::new();
    let mut headers = HeaderMap::new();
    
    // Set up Token authentication
    headers.insert(
        AUTHORIZATION,
        HeaderValue::from_str(&format!("Token {}", args.token))
            .context("Failed to create authorization header")?,
    );
    
    headers.insert(CONTENT_TYPE, HeaderValue::from_static("application/json"));

    if args.verbose {
        println!("Using Token authentication");
        println!("API URL: {}", args.api_url);
    }

    // Open the ledger file
    let file = File::open(&args.file)
        .with_context(|| format!("Failed to open file: {}", args.file.display()))?;
    let reader = BufReader::new(file);

    // Regex to match account declarations
    let account_re = Regex::new(r"^account\s+(.+)$").context("Failed to compile regex")?;
    let mut accounts = Vec::new();

    // Parse the file line by line
    for line in reader.lines() {
        let line = line.context("Failed to read line from file")?;
        if let Some(captures) = account_re.captures(&line) {
            let account_name = captures.get(1).unwrap().as_str().trim();
            if args.verbose {
                println!("Found account: {}", account_name);
            }
            accounts.push(Account {
                name: account_name.to_string(),
                description: Some(format!("Imported from ledger file")),
                currency: Some("INR".to_string()),
                balance: Some(0.0),
            });
        }
    }

    if accounts.is_empty() {
        println!("No accounts found in the file.");
        return Ok(());
    }

    println!("Found {} accounts in the file.", accounts.len());
    
    if args.dry_run {
        println!("Dry run mode enabled. Not creating accounts in Kanakku.");
        return Ok(());
    }

    // Create each account via the API
    for account in accounts {
        match create_account(&client, &args.api_url, &headers, &account).await {
            Ok(response) => {
                println!("Created account: {} (ID: {})", response.account.name, response.account.id);
            }
            Err(e) => {
                eprintln!("Error creating account '{}': {}", account.name, e);
            }
        }
    }

    Ok(())
}

async fn create_account(
    client: &reqwest::Client,
    api_url: &str,
    headers: &HeaderMap,
    account: &Account,
) -> Result<ApiResponse> {
    let url = format!("{}/api/v1/accounts", api_url);
    
    // Debugging information
    println!("Creating account: {}", account.name);
    println!("API URL: {}", url);
    
    let response = client
        .post(&url)
        .headers(headers.clone())
        .json(account)
        .send()
        .await
        .context("Failed to send API request")?;

    if response.status().is_success() {
        let api_response = response
            .json::<ApiResponse>()
            .await
            .context("Failed to parse API response")?;
        Ok(api_response)
    } else {
        // Handle error response
        let status = response.status();
        
        // Get the response body text
        let body_text = response.text().await.unwrap_or_default();
        
        // Try to parse as JSON error if possible
        let error_text = if !body_text.is_empty() {
            if let Ok(error) = serde_json::from_str::<ErrorResponse>(&body_text) {
                error.error
            } else {
                // If not valid JSON or doesn't match our error format, return the raw text
                format!("Error response: {}", body_text)
            }
        } else {
            format!("HTTP Error: {} (no response body)", status)
        };
        
        anyhow::bail!("API error ({} {}): {}", status.as_u16(), status.canonical_reason().unwrap_or("Unknown"), error_text)
    }
} 