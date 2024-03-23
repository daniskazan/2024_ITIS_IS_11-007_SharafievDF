package main

import (
	"fmt"
	"github.com/PuerkitoBio/goquery"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
)

type WebCrawler struct {
	URLs       []string
	TargetDir  string
	MaxPages   int
	MinWords   int
	CrawledSet map[string]bool
}

func NewWebCrawler(urls []string, targetDir string, maxPages, minWords int) *WebCrawler {
	return &WebCrawler{
		URLs:       urls,
		TargetDir:  targetDir,
		MaxPages:   maxPages,
		MinWords:   minWords,
		CrawledSet: make(map[string]bool),
	}
}

func (wc *WebCrawler) Crawl() {
	indexFile, err := os.Create(filepath.Join(wc.TargetDir, "index.txt"))
	if err != nil {
		log.Fatalf("Failed to create index file: %v", err)
	}
	defer indexFile.Close()

	for len(wc.CrawledSet) < wc.MaxPages && len(wc.URLs) > 0 {
		url := wc.URLs[0]
		wc.URLs = wc.URLs[1:]

		if wc.CrawledSet[url] {
			continue
		}

		html, err := wc.download(url)
		if err != nil {
			log.Printf("Failed to fetch %s: %v", url, err)
			continue
		}

		text := wc.extract(html)
		if !wc.isSufficientText(text) {
			continue
		}

		filename := fmt.Sprintf("page_%d.txt", len(wc.CrawledSet)+1)
		filePath := filepath.Join(wc.TargetDir, filename)
		err = os.WriteFile(filePath, []byte(text), 0644)
		if err != nil {
			log.Printf("Failed to save page %s: %v", url, err)
			continue
		}
		indexFile.WriteString(fmt.Sprintf("%d: %s\n", len(wc.CrawledSet)+1, url))
		wc.CrawledSet[url] = true

		wc.addLinksToCrawl(url, html, &wc.URLs)
	}
}

func (wc *WebCrawler) download(url string) (string, error) {
	resp, err := http.Get(url)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("failed to fetch %s: %s", url, resp.Status)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	return string(body), nil
}

func (wc *WebCrawler) extract(html string) string {
	doc, err := goquery.NewDocumentFromReader(strings.NewReader(html))
	if err != nil {
		log.Printf("Failed to parse HTML: %v", err)
		return ""
	}
	return doc.Text()
}

func (wc *WebCrawler) isSufficientText(text string) bool {
	return len(strings.Fields(text)) >= wc.MinWords
}

func (wc *WebCrawler) joinURL(baseURL, link string) (string, error) {
	base, err := url.Parse(baseURL)
	if err != nil {
		return "", err
	}
	rel, err := url.Parse(link)
	if err != nil {
		return "", err
	}
	resolvedURL := base.ResolveReference(rel).String()
	return resolvedURL, nil
}
func (wc *WebCrawler) addLinksToCrawl(url, html string, pagesToCrawl *[]string) {
	doc, err := goquery.NewDocumentFromReader(strings.NewReader(html))
	if err != nil {
		log.Printf("Failed to parse HTML: %v", err)
		return
	}

	doc.Find("a").Each(func(_ int, s *goquery.Selection) {
		link, exists := s.Attr("href")
		if !exists {
			return
		}
		absoluteLink, err := wc.joinURL(url, link)
		if err != nil {
			log.Fatal(err)
		}
		if !wc.CrawledSet[absoluteLink] {
			*pagesToCrawl = append(*pagesToCrawl, absoluteLink)
		}
	})
}

func main() {
	dir, _ := os.Getwd()
	targetDirectory := filepath.Join(dir, "downloaded_pages_uk_rf")
	fmt.Printf(targetDirectory)
	os.MkdirAll(targetDirectory, os.ModePerm)
	crawler := NewWebCrawler(
		[]string{"https://habr.com/ru/feed"},
		targetDirectory,
		100,
		1000,
	)
	crawler.Crawl()
}
