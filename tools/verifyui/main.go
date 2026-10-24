package main

import (
	"encoding/csv"
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/mxschmitt/playwright-go"
)

func snippet(s string) string {
	s = strings.Join(strings.Fields(s), " ")
	if len(s) > 180 {
		return s[:180]
	}

	return s
}

func main() {
	if len(os.Args) != 3 {
		fmt.Println("usage: verifyui <input.csv> <output.csv>")
		os.Exit(2)
	}

	pw, err := playwright.Run()
	if err != nil {
		panic(err)
	}
	defer pw.Stop()

	browser, err := pw.Chromium.Launch(playwright.BrowserTypeLaunchOptions{
		Headless:         playwright.Bool(true),
		ChromiumSandbox:  playwright.Bool(false),
		Args:             []string{"--no-sandbox", "--disable-dev-shm-usage"},
	})
	if err != nil {
		panic(err)
	}
	defer browser.Close()

	in, err := os.Open(os.Args[1])
	if err != nil {
		panic(err)
	}
	defer in.Close()

	rows, err := csv.NewReader(in).ReadAll()
	if err != nil {
		panic(err)
	}

	out, err := os.Create(os.Args[2])
	if err != nil {
		panic(err)
	}
	defer out.Close()

	writer := csv.NewWriter(out)
	_ = writer.Write([]string{"group", "url", "permanent", "temporary", "claim", "snippet"})

	for _, row := range rows[1:] {
		group, url := row[0], row[1]

		page, err := browser.NewPage()
		if err != nil {
			_ = writer.Write([]string{group, url, "ERR", "", "", err.Error()})
			writer.Flush()

			continue
		}

		_, err = page.Goto(url, playwright.PageGotoOptions{
			WaitUntil: playwright.WaitUntilStateDomcontentloaded,
			Timeout:   playwright.Float(45000),
		})
		if err != nil {
			_ = writer.Write([]string{group, url, "ERR", "", "", err.Error()})
			writer.Flush()
			_ = page.Close()

			continue
		}

		time.Sleep(2 * time.Second)

		text, err := page.Locator("body").InnerText()
		if err != nil {
			_ = writer.Write([]string{group, url, "ERR", "", "", err.Error()})
			writer.Flush()
			_ = page.Close()

			continue
		}

		lower := strings.ToLower(text)
		_ = writer.Write([]string{
			group,
			url,
			fmt.Sprintf("%t", strings.Contains(lower, "permanently closed")),
			fmt.Sprintf("%t", strings.Contains(lower, "temporarily closed")),
			fmt.Sprintf("%t", strings.Contains(lower, "claim this business")),
			snippet(text),
		})
		writer.Flush()
		_ = page.Close()

		fmt.Println("checked", group, url)
	}
}
