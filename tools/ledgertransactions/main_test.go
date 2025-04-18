package main

import (
   "encoding/json"
   "fmt"
   "net/http"
   "net/http/httptest"
   "strings"
   "testing"
)

// Test success case: server returns valid Preamble JSON
func TestGetPreambleIDByName_Success(t *testing.T) {
   name := "testName"
   token := "testToken"
   expectedID := "12345"
   // Setup mock server
   server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
       // Verify request path and headers
       expectedPath := fmt.Sprintf("/api/v1/preambles/name/%s", name)
       if r.URL.Path != expectedPath {
           t.Errorf("unexpected path: got %s, want %s", r.URL.Path, expectedPath)
       }
       auth := r.Header.Get("Authorization")
       if auth != "Token "+token {
           t.Errorf("unexpected Authorization header: got %s, want %s", auth, "Token "+token)
       }
       accept := r.Header.Get("Accept")
       if accept != "application/json" {
           t.Errorf("unexpected Accept header: got %s, want application/json", accept)
       }
       // Respond with valid JSON
       resp := Preamble{ID: expectedID, Name: name}
       w.Header().Set("Content-Type", "application/json")
       json.NewEncoder(w).Encode(resp)
   }))
   defer server.Close()
   // Call function under test
   id, err := getPreambleIDByName(server.URL, token, name)
   if err != nil {
       t.Fatalf("expected no error, got %v", err)
   }
   if id != expectedID {
       t.Errorf("unexpected id: got %s, want %s", id, expectedID)
   }
}

// Test not found case: server returns 404
func TestGetPreambleIDByName_NotFound(t *testing.T) {
   name := "missing"
   token := "token"
   server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
       w.WriteHeader(http.StatusNotFound)
   }))
   defer server.Close()
   _, err := getPreambleIDByName(server.URL, token, name)
   if err == nil {
       t.Fatal("expected error for 404 response, got nil")
   }
   want := fmt.Sprintf("preamble with name '%s' not found", name)
   if err.Error() != want {
       t.Errorf("unexpected error message: got %q, want %q", err.Error(), want)
   }
}

// Test non-OK status: server returns 500
func TestGetPreambleIDByName_ServerError(t *testing.T) {
   name := "error"
   token := "token"
   server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
       http.Error(w, "internal error", http.StatusInternalServerError)
   }))
   defer server.Close()
   _, err := getPreambleIDByName(server.URL, token, name)
   if err == nil {
       t.Fatal("expected error for 500 response, got nil")
   }
   // Error should mention non-OK status and status text
   if !strings.Contains(err.Error(), "preamble by name API returned non-OK status: 500 Internal Server Error") {
       t.Errorf("unexpected error message: %q", err.Error())
   }
}

// Test invalid JSON response
func TestGetPreambleIDByName_InvalidJSON(t *testing.T) {
   name := "badjson"
   token := "token"
   server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
       w.Header().Set("Content-Type", "application/json")
       w.Write([]byte("not a json"))
   }))
   defer server.Close()
   _, err := getPreambleIDByName(server.URL, token, name)
   if err == nil {
       t.Fatal("expected error for invalid JSON, got nil")
   }
   if !strings.Contains(err.Error(), "error decoding preamble by name JSON response") {
       t.Errorf("unexpected error message: %q", err.Error())
   }
}

// Test empty ID in JSON
func TestGetPreambleIDByName_EmptyID(t *testing.T) {
   name := "noid"
   token := "token"
   server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
       resp := Preamble{ID: "", Name: name}
       w.Header().Set("Content-Type", "application/json")
       json.NewEncoder(w).Encode(resp)
   }))
   defer server.Close()
   _, err := getPreambleIDByName(server.URL, token, name)
   if err == nil {
       t.Fatal("expected error for empty ID, got nil")
   }
   if !strings.Contains(err.Error(), "preamble ID not found in the response") {
       t.Errorf("unexpected error message: %q", err.Error())
   }
}
