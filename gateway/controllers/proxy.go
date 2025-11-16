package controllers

import (
	"bytes"
	"gateway/utils"
	"io"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
)

func ProxyItems(c *gin.Context) {
	productURL := os.Getenv("PRODUCT_SERVICE_URL")
	if productURL == "" {
		productURL = "http://localhost:8081"
	}

	url := productURL + "/items"
	method := c.Request.Method
	body, _ := io.ReadAll(c.Request.Body)

	req, err := http.NewRequest(method, url, bytes.NewBuffer(body))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create request"})
		return
	}

	// Copy headers
	for key, values := range c.Request.Header {
		for _, value := range values {
			req.Header.Add(key, value)
		}
	}

	// Get token from context and set in req
	userID, exists := c.Get("user_id")
	if exists {
		username, _ := c.Get("username")
		email, _ := c.Get("email")
		token, _ := utils.GenerateToken(userID.(uint), username.(string), email.(string))
		req.Header.Set("Authorization", "Bearer "+token)
	}

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to proxy request"})
		return
	}
	defer resp.Body.Close()

	bodyResp, _ := io.ReadAll(resp.Body)
	c.Data(resp.StatusCode, resp.Header.Get("Content-Type"), bodyResp)
}

func ProxyItem(c *gin.Context) {
	productURL := os.Getenv("PRODUCT_SERVICE_URL")
	if productURL == "" {
		productURL = "http://localhost:8081"
	}

	url := productURL + "/items/" + c.Param("id")
	method := c.Request.Method
	body, _ := io.ReadAll(c.Request.Body)

	req, err := http.NewRequest(method, url, bytes.NewBuffer(body))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create request"})
		return
	}

	// Copy headers
	for key, values := range c.Request.Header {
		for _, value := range values {
			req.Header.Add(key, value)
		}
	}

	// Get token from context and set in req
	userID, exists := c.Get("user_id")
	if exists {
		username, _ := c.Get("username")
		email, _ := c.Get("email")
		token, _ := utils.GenerateToken(userID.(uint), username.(string), email.(string))
		req.Header.Set("Authorization", "Bearer "+token)
	}

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to proxy request"})
		return
	}
	defer resp.Body.Close()

	bodyResp, _ := io.ReadAll(resp.Body)
	c.Data(resp.StatusCode, resp.Header.Get("Content-Type"), bodyResp)
}

func ProxyCategories(c *gin.Context) {
	productURL := os.Getenv("PRODUCT_SERVICE_URL")
	if productURL == "" {
		productURL = "http://localhost:8081"
	}

	url := productURL + "/categories"
	method := c.Request.Method
	body, _ := io.ReadAll(c.Request.Body)

	req, err := http.NewRequest(method, url, bytes.NewBuffer(body))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create request"})
		return
	}

	// Copy headers
	for key, values := range c.Request.Header {
		for _, value := range values {
			req.Header.Add(key, value)
		}
	}

	// For categories, if POST, might need auth, but in product, POST categories has no auth, but to be consistent, since proxy uses auth, but product doesn't require for categories.

	// But since proxy has auth, and product doesn't check for categories, it's fine.

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to proxy request"})
		return
	}
	defer resp.Body.Close()

	bodyResp, _ := io.ReadAll(resp.Body)
	c.Data(resp.StatusCode, resp.Header.Get("Content-Type"), bodyResp)
}

func ProxyBids(c *gin.Context) {
	productURL := os.Getenv("PRODUCT_SERVICE_URL")
	if productURL == "" {
		productURL = "http://localhost:8081"
	}

	url := productURL + "/bids"
	if c.Param("item_id") != "" {
		url += "/" + c.Param("item_id")
	}
	method := c.Request.Method
	body, _ := io.ReadAll(c.Request.Body)

	req, err := http.NewRequest(method, url, bytes.NewBuffer(body))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create request"})
		return
	}

	// Copy headers
	for key, values := range c.Request.Header {
		for _, value := range values {
			req.Header.Add(key, value)
		}
	}

	// Get token from context and set in req
	userID, exists := c.Get("user_id")
	if exists {
		username, _ := c.Get("username")
		email, _ := c.Get("email")
		token, _ := utils.GenerateToken(userID.(uint), username.(string), email.(string))
		req.Header.Set("Authorization", "Bearer "+token)
	}

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to proxy request"})
		return
	}
	defer resp.Body.Close()

	bodyResp, _ := io.ReadAll(resp.Body)
	c.Data(resp.StatusCode, resp.Header.Get("Content-Type"), bodyResp)
}
