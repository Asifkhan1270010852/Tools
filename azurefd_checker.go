package main

import (
	"bufio"
	"crypto/tls"
	"encoding/json"
	"flag"
	"fmt"
	"net"
	"net/http"
	"os"
	"strings"
	"time"
)

type Result struct {
	Domain string `json:"domain"`
	CNAME  string `json:"cname"`
	Status string `json:"status"`
	Notes  string `json:"notes"`
}

func getCNAME(domain string) string {
	cname, err := net.LookupCNAME(domain)
	if err != nil {
		return ""
	}
	return strings.TrimSuffix(cname, ".")
}

func checkAzureFD(endpoint string) string {
	client := &http.Client{
		Timeout: 5 * time.Second,
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		},
	}

	resp, err := client.Get("https://" + endpoint)
	if err != nil {
		return "unreachable"
	}
	defer resp.Body.Close()

	buf := new(strings.Builder)
	_, _ = buf.ReadFrom(resp.Body)
	body := strings.ToLower(buf.String())

	if strings.Contains(body, "azure front door") || strings.Contains(body, "error 404") || strings.Contains(body, "resource you are looking for") {
		return "default_error"
	}
	return "active"
}

func suffixPresent(cname string) bool {
	parts := strings.Split(strings.Split(cname, ".")[0], "-")
	last := parts[len(parts)-1]
	return len(last) > 10 && strings.ContainsAny(last, "0123456789")
}

func checkCustomDomainVerification(domain string) bool {
	client := &http.Client{
		Timeout: 5 * time.Second,
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		},
	}

	resp, err := client.Get("http://" + domain)
	if err != nil {
		return false
	}
	defer resp.Body.Close()

	for k := range resp.Header {
		if strings.Contains(strings.ToLower(k), "azurefd-verification") {
			return false
		}
	}
	return true
}

func analyzeDomain(target string) Result {
	res := Result{Domain: target, Status: "safe", Notes: ""}
	cname := getCNAME(target)
	if cname == "" {
		res.Notes = "No CNAME found"
		return res
	}
	res.CNAME = cname

	if !strings.Contains(cname, ".azurefd.net") {
		res.Notes = "Not AzureFD endpoint"
		return res
	}

	if suffixPresent(cname) {
		if checkCustomDomainVerification(target) {
			res.Status = "vulnerable"
			res.Notes = "Suffix present, custom domain verification missing → bypass possible"
		} else {
			res.Notes = "Suffix present, verification enabled"
		}
	} else {
		status := checkAzureFD(cname)
		if status == "default_error" {
			res.Status = "vulnerable"
			res.Notes = "No suffix, default AzureFD error → dangling endpoint"
		} else {
			res.Notes = "No suffix, endpoint active"
		}
	}

	return res
}

func main() {
	url := flag.String("u", "", "Single domain/subdomain to check")
	listFile := flag.String("l", "", "File with list of domains")
	vulnOnly := flag.Bool("vuln-only", false, "Show only vulnerable domains")
	jsonOut := flag.Bool("json", false, "Output in JSON format")
	flag.Parse()

	if *url == "" && *listFile == "" {
		fmt.Println("Usage:")
		flag.PrintDefaults()
		return
	}

	var targets []string
	if *url != "" {
		targets = append(targets, strings.TrimSpace(*url))
	}
	if *listFile != "" {
		file, err := os.Open(*listFile)
		if err != nil {
			fmt.Println("Error opening file:", err)
			return
		}
		defer file.Close()
		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			line := strings.TrimSpace(scanner.Text())
			if line != "" {
				targets = append(targets, line)
			}
		}
	}

	var results []Result
	for _, t := range targets {
		results = append(results, analyzeDomain(t))
	}

	if *vulnOnly {
		var filtered []Result
		for _, r := range results {
			if r.Status == "vulnerable" {
				filtered = append(filtered, r)
			}
		}
		results = filtered
	}

	if *jsonOut {
		data, _ := json.MarshalIndent(results, "", "  ")
		fmt.Println(string(data))
	} else {
		fmt.Printf("%-40s %-60s %-12s %s\n", "Domain", "CNAME", "Status", "Notes")
		fmt.Println(strings.Repeat("-", 130))
		for _, r := range results {
			fmt.Printf("%-40s %-60s %-12s %s\n", r.Domain, r.CNAME, r.Status, r.Notes)
		}
	}
}
